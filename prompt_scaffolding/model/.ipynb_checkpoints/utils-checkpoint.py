import re
import json

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

def vllm_encoder(obj):
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj) # Fallback for any weird types inside

def format_json_inplace(filepath, indent=4):
    # 1. Read the existing data
    with open(filepath, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {filepath} is not valid JSON.", file=sys.stderr)
            return

    # 2. Create the standard pretty-printed string
    # This ensures strings and objects are on new lines as requested
    pretty_json = json.dumps(data, indent=indent)

    # 3. Use Regex to find numeric arrays and collapse them
    # This matches '[' followed by numbers, commas, and whitespace, ending in ']'
    # It will NOT match ["a", "b"] because of the quote marks.
    numeric_array_pattern = r'\[(?:\s*-?[\d\.]+\s*,?)+\s*\]'

    def collapse_match(match):
        # Remove all newlines and extra spaces, then add a single space after commas
        collapsed = re.sub(r'\s+', '', match.group(0))
        return collapsed.replace(',', ', ')

    fixed_json = re.sub(numeric_array_pattern, collapse_match, pretty_json)

    # 4. Overwrite the original file
    with open(filepath, 'w') as f:
        f.write(fixed_json)