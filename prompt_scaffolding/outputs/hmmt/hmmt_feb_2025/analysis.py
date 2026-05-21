from matharena.json_zst import OUTPUT_JSON_SUFFIX, load_json_zst
import json

all_token_count = 0
for i in range(1, 31):
    res = load_json_zst(f"/home/stevex2/CS497/prompt_scaffolding/outputs/hmmt/hmmt_feb_2025/qwen3_4b_bon_8_prune15_0_43/{i}.json.zst")
    all_token_count += res['detailed_costs'][0]['output_tokens']

print(all_token_count)

# qwen3_4b_bon_1_none_0_3 == 0.3 == 220295 tokens
# qwen3_4b_bon_2_none_0_33 == 0.33 == 441101 tokens
# qwen3_4b_bon_4_none_0_43 == 0.43 == 882168 tokens
# qwen3_4b_bon_8_none_0_53 == 0.53 == 1815763 tokens

# CS497/prompt_scaffolding/outputs/hmmt/hmmt_feb_2025/qwen3_4b_bon_1_prune15_0_36