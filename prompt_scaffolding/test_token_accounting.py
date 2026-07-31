"""Offline end-to-end check of the pipeline's token accounting.

Runs main.run() for real -- real chunking, real selection/ranking control flow, real
aggregation, real JSON writer -- against a stub LLM that reports exactly the token counts
vLLM would. The stub keeps a ledger of every token it charged, so the numbers in the
emitted JSON can be checked against ground truth instead of against themselves.

The accounting under test is DECODE-ONLY (see model/utils.py). The cost model, per
question of a pruned arm at best-of-N with prune ratio r (k = N/r survivors):

    N x max_plan_tokens          drafting all N plans   (not just the k that survive)
  + prune reply                  rank / bracket / cluster; zero for the random arm
  + N continuations              regen: N, spread over k requests
    (or k)                       prune-only: one per survivor
  + judge reply

Nothing charges prompt tokens, and this asserts that too -- a prefill field reappearing in
the output is a regression.
"""
import json, math, os, statistics, sys, tempfile, types, glob

REPO = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO)
os.environ.setdefault("HF_HUB_OFFLINE", "1")

from transformers import AutoTokenizer
from model.utils import draft_messages

TOK = AutoTokenizer.from_pretrained("Qwen/Qwen3-4B-Instruct-2507")

# --------------------------------------------------------------------------- stub vLLM
class FakeCompletionOutput:
    def __init__(self, text):
        self.text = text
        self.token_ids = TOK.encode(text, add_special_tokens=False)

class FakeRequestOutput:
    def __init__(self, prompt_ids, texts):
        self.prompt_token_ids = prompt_ids          # present, and deliberately NOT counted
        self.outputs = [FakeCompletionOutput(t) for t in texts]

class FakeLLM:
    """Reports sampled tokens per sequence, like vLLM. Also exposes prompt_token_ids, so a
    pipeline that started charging prefill again would show up in the ledger comparison."""
    def __init__(self):
        self.ledger = []          # (kind, prefill, decode, n)

    def get_tokenizer(self):
        return TOK

    def _kind(self, text):
        if "select the single best solution" in text:            return "judge"
        if "Group them by their core SOLUTION APPROACH" in text: return "cluster"
        if "Rank the" in text:                                   return "rank"
        if "First, write out your step-by-step" in text:         return "draft"
        return "completion"

    def _reply(self, kind, n_cand):
        if kind == "judge":
            return "<evaluation>ok</evaluation>\n<results>\ni0\n</results>"
        if kind == "rank":
            return "<evaluation>ok</evaluation>\n<results>\n" + "\n".join(f"i{j}" for j in range(n_cand)) + "\n</results>"
        if kind == "cluster":
            return "<results>\n" + "\n".join(f"i{j}: {chr(65+j)}" for j in range(n_cand)) + "\n</results>"
        if kind == "draft":
            return "thinking about it step by step <answer>1 + 2</answer>"
        return " and so the plan concludes <answer>1 + 2</answer>"

    @staticmethod
    def _n_candidates(text):
        import re
        return max(1, len(re.findall(r"<example id='i\d+'>", text)) or len(re.findall(r"<plan id='i\d+'>", text)))

    def chat(self, messages, sampling_params=None, **kw):
        outs = []
        for conv in messages:
            rendered = TOK.apply_chat_template(conv, add_generation_prompt=True, tokenize=False)
            ids = TOK.encode(rendered, add_special_tokens=False)
            content = conv[-1]["content"]
            kind = self._kind(content)
            n = getattr(sampling_params, "n", 1) or 1
            texts = [self._reply(kind, self._n_candidates(content)) for _ in range(n)]
            out = FakeRequestOutput(ids, texts)
            self.ledger.append((kind, len(ids), sum(len(o.token_ids) for o in out.outputs), n))
            outs.append(out)
        return outs

    def generate(self, prompts, sampling_params=None, **kw):
        sps = sampling_params if isinstance(sampling_params, list) else [sampling_params] * len(prompts)
        outs = []
        for text, sp in zip(prompts, sps):
            ids = TOK.encode(text, add_special_tokens=False)
            n = getattr(sp, "n", 1) or 1
            out = FakeRequestOutput(ids, [self._reply("completion", 1) for _ in range(n)])
            self.ledger.append(("completion", len(ids), sum(len(o.token_ids) for o in out.outputs), n))
            outs.append(out)
        return outs

# --------------------------------------------------------------------------- harness
import main as main_mod
from model.model import Model
from model.rank import ranker

FAKE = FakeLLM()

def fake_model(*a, **kw):
    m = Model.__new__(Model)
    m.llm = FAKE
    m.seed = 42
    m.ranker = ranker("Solutions", FAKE, 42)
    return m

main_mod.Model = fake_model

WORK = tempfile.mkdtemp(prefix="token_accounting_")
print(f"scratch: {WORK}\n")
os.chdir(WORK)

def args(**kw):
    base = dict(dataset_type="countdown", level=6, num_examples=3, temperature=1.0,
                best_of_ns=[1, 2, 4], max_plan_tokens=400, prune_ratio=2, group_size=4,
                num_gpus=1, data_parallel=False, baseline=False, regen=False, diverse=False,
                cache_fn="")
    base.update(kw)
    return types.SimpleNamespace(**base)

def newest(pattern):
    files = sorted(glob.glob(pattern), key=os.path.getmtime)
    assert files, f"no file matching {pattern}"
    return files[-1]

FAILS = []
def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)

def close(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))

def pooled_std(means, stds, n):
    N = len(means) * n
    if N < 2: return 0.0
    g = statistics.mean(means)
    return math.sqrt(sum((n - 1) * s * s + n * (m - g) ** 2 for m, s in zip(means, stds)) / (N - 1))

BANNED = ("prefill", "prompt_token", "decode_mean_tokens")

def validate(path, label):
    print(f"\n-- {label}: {os.path.basename(path)}")
    raw = open(path).read()
    for word in BANNED:
        check(word not in raw, f"{label}: no '{word}' anywhere in the output (decode-only)")
    d = json.loads(raw)
    for bon, blk in sorted(d.items(), key=lambda kv: int(kv[0])):
        dm, pm = blk["dataset_metrics"], blk["prompt_metrics"]
        n = dm["num_chunks_averaged"]
        check(sorted(dm) == ["average_score", "mean_tokens", "num_chunks_averaged", "std_tokens"],
              f"bon{bon}: dataset_metrics has exactly the decode-only keys")
        check(close(dm["mean_tokens"], statistics.mean(p["mean_tokens"] for p in pm)),
              f"bon{bon}: dataset mean_tokens == mean of per-question means")
        check(close(dm["std_tokens"], pooled_std([p["mean_tokens"] for p in pm],
                                                [p["std_tokens"] for p in pm], n), 1e-6),
              f"bon{bon}: dataset std_tokens is the spread of the same values mean_tokens averages")
        check(all(p["mean_tokens"] > 0 for p in pm), f"bon{bon}: every question charged")
    return d

print("=" * 78)
print("1. BASELINE run (writes baseline_cache.json)")
print("=" * 78)
FAKE.ledger.clear()
main_mod.run(args(baseline=True))
base_json = validate(newest("*_baseline_bon_*.json"), "baseline")

cache = json.load(open("baseline_cache.json"))
recs = [r for chunks in cache.values() for ch in chunks for drafts in ch for r in drafts]
check(all(sorted(r) == ["text", "token_count"] for r in recs),
      "baseline_cache.json stores only text + token_count (no prompt-token machinery)")

# The judge runs even at bon=1 (no single-candidate short-circuit), so the baseline's
# total must exceed the drafts alone at every N.
draft_dec = {}
for kind, pf, dec, n in FAKE.ledger:
    if kind == "draft":
        draft_dec.setdefault("per_seq", dec / n)
check(base_json["1"]["prompt_metrics"][0]["mean_tokens"] > draft_dec["per_seq"],
      "bon=1: total exceeds the single draft -> the judge reply IS charged at bon=1")

print("\n" + "=" * 78)
print("2. STRATEGY run off the cache (rank / random / tourney)")
print("=" * 78)
FAKE.ledger.clear()
main_mod.run(args(cache_fn="baseline_cache.json"))
arms = {arm: validate(newest(f"*_{arm}_bon_*.json"), arm) for arm in ("rank", "random", "tourney")}

print("\n-- cross-arm relationships")
for bon in ("2", "4"):
    r = arms["rank"][bon]["dataset_metrics"]["mean_tokens"]
    n_ = arms["random"][bon]["dataset_metrics"]["mean_tokens"]
    check(r > n_, f"bon{bon}: rank total {r:.0f} > random total {n_:.0f} (random makes no prune call)")

print("\n" + "=" * 78)
print("3. STAGE-BY-STAGE RECONCILIATION against the stub's ledger")
print("=" * 78)
# A synthetic cache with KNOWN token_counts, all above the cap, makes the drafting term
# exactly N * max_plan_tokens so an under- or over-charge cannot hide in real variation.
from model.strategies import CompletionStrategy
from model.model import Model as RealModel

NQ, BON, CAP, PRUNE = 2, 4, 400, 2
K = max(1, BON // PRUNE)

synth = {str(BON): [[[{"text": "one plan step. " * 400, "token_count": CAP * 3 + 7 * d}
                      for d in range(BON)]
                     for _ in range(NQ)]]}
json.dump(synth, open("synth_cache.json", "w"))

def reconcile(arm, regen):
    captured = {}
    real_gp = CompletionStrategy.generate_prompts
    real_pfs = RealModel._process_final_selection
    def spy_gp(self, *a, **kw):
        out = real_gp(self, *a, **kw)
        captured["base"], captured["prune"] = out["base_tokens"], out["paths"][arm]["tokens"]
        return out
    def spy_pfs(self, *a, **kw):
        cd = real_pfs(self, *a, **kw)
        captured["chunk"] = cd
        return cd
    CompletionStrategy.generate_prompts, RealModel._process_final_selection = spy_gp, spy_pfs
    os.environ["ONLY_PATHS"] = arm
    FAKE.ledger.clear()
    try:
        main_mod.run(args(num_examples=NQ, best_of_ns=[BON], max_plan_tokens=CAP,
                          prune_ratio=PRUNE, cache_fn="synth_cache.json", regen=regen))
    finally:
        CompletionStrategy.generate_prompts = real_gp
        RealModel._process_final_selection = real_pfs
        del os.environ["ONLY_PATHS"]
    return captured, [e for e in FAKE.ledger if e[0] == "completion"]

for arm in ("rank", "random"):
    for regen in (False, True):
        tag = f"{arm} regen={regen}"
        print(f"\n-- {tag}")
        cap_, comp = reconcile(arm, regen)
        b, s, cd = cap_["base"], cap_["prune"], cap_["chunk"]
        c, total = cd["sel_tokens"], cd["total_tokens"]

        want = BON if regen else K
        check(len(comp) == K * NQ,
              f"{tag}: {len(comp)} continuation REQUESTS == k*NQ = {K * NQ} (one per survivor)")
        check(sum(e[3] for e in comp) == want * NQ,
              f"{tag}: {sum(e[3] for e in comp)} continuations decoded == "
              f"{'N' if regen else 'k'}*NQ = {want * NQ}"
              f"{' (pruned to k, regenerated back to N)' if regen else ''}")

        for q in range(NQ):
            check(b[q] == BON * CAP,
                  f"{tag} q{q}: drafting {b[q]} == N*max_plan_tokens = {BON * CAP} "
                  f"(all {BON} drafts, not just the {K} survivors)")
            if arm == "random":
                check(s[q] == 0, f"{tag} q{q}: random prune costs nothing (no LLM call)")
            else:
                check(s[q] > 0, f"{tag} q{q}: prune reply charged ({s[q]})")
            g = sum(e[2] for e in comp[q * K:(q + 1) * K])
            check(c[q] > 0, f"{tag} q{q}: judge reply charged ({c[q]})")
            check(total[q] == b[q] + s[q] + g + c[q],
                  f"{tag} q{q}: total {total[q]} == drafting {b[q]} + prune {s[q]} "
                  f"+ continuations {g} + judge {c[q]}")

        emitted = json.load(open(newest(f"*_{arm}_bon_{BON}_*{'_regen' if regen else ''}.json")))
        check(close(emitted[str(BON)]["prompt_metrics"][0]["mean_tokens"], total[0]),
              f"{tag}: emitted mean_tokens {emitted[str(BON)]['prompt_metrics'][0]['mean_tokens']:.0f} "
              f"== reconciled total {total[0]}")

print("\n-- regen costs exactly (N-k) extra continuations over prune-only")
for arm in ("rank", "random"):
    plain, _ = reconcile(arm, False)
    rg, _ = reconcile(arm, True)
    per_completion = (rg["chunk"]["total_tokens"][0] - plain["chunk"]["total_tokens"][0]) / (BON - K)
    check(per_completion > 0 and float(per_completion).is_integer(),
          f"{arm}: regen - prune-only == (N-k) x {per_completion:.0f} continuation tokens")

print("\n" + "=" * 78)
print("4. strip_prefill.py restores an already-written file to this basis")
print("=" * 78)
import strip_prefill
blk = {"dataset_metrics": {"average_score": 0.5, "mean_tokens": 8377.0, "std_tokens": 6311.0,
                           "num_chunks_averaged": 4,
                           "decode_mean_tokens": 8238.0, "prefill_mean_tokens": 139.0},
       "prompt_metrics": [{"mean_score": 1.0, "mean_tokens": 500.0, "std_tokens": 10.0,
                           "tourney_mean_tokens": 520.0, "decode_mean_tokens": 480.0,
                           "prefill_mean_tokens": 20.0, "tourney_decode_mean_tokens": 495.0,
                           "tourney_prefill_mean_tokens": 25.0}]}
check(strip_prefill.decode_only(blk) is True, "strip: reports a change on a patched block")
check(blk["dataset_metrics"]["mean_tokens"] == 8238.0, "strip: dataset mean_tokens <- decode")
check(blk["prompt_metrics"][0]["mean_tokens"] == 480.0, "strip: question mean_tokens <- decode")
check(blk["prompt_metrics"][0]["tourney_mean_tokens"] == 495.0, "strip: tourney mean <- tourney decode")
check(blk["dataset_metrics"]["std_tokens"] == 6311.0,
      "strip: std_tokens untouched (it was always decode-only, so it now agrees with the mean)")
check(not any(k.startswith(("decode_", "prefill_", "tourney_decode", "tourney_prefill"))
              for h in [blk["dataset_metrics"]] + blk["prompt_metrics"] for k in h),
      "strip: every decode_/prefill_ key removed")
check(strip_prefill.decode_only(blk) is False, "strip: idempotent -- second pass is a no-op")

print("\n" + "=" * 78)
print(f"{'ALL CHECKS PASSED' if not FAILS else str(len(FAILS)) + ' CHECK(S) FAILED'}")
print("=" * 78)
for f in FAILS:
    print("  FAILED:", f)
sys.exit(1 if FAILS else 0)
