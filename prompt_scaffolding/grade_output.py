with open("/u/stevex2/prompt_scaffolding/CS497/prompt_scaffolding/Qwen_Qwen3-0_6B_2026-02-24-18-00_n=8_t=0.9_countdown_n=100_CountdownStrategy.txt", 'r') as f:
    total_score = 0
    total_puzzles = 0
    for line in f:
        res = line
        if "Num Tokens: " in res:
            total_puzzles += 1
            if "Score:" in res:
                score = float(res.split(' ')[-1].strip())
                total_score += score
         
    print("Acc:", total_score)