import re

def extract_answer(text):
    # Pattern looks for everything between <answer> and </answer>
    # re.DOTALL allows the dot (.) to match newlines if the answer is multi-line
    match = re.findall(r'<answer>(.*?)</answer>', text, re.DOTALL)
    
    if match:
        return match[-1].strip()
    
    # If no tags exist, return the original string
    return text

def extract_content(text):
    # extract the <think><\think> tags and return result
    match = re.search(r"(?<=<\/think>)\s*([\s\S]*)", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()