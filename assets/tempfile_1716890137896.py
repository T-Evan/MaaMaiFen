import re

if __name__ == "__main__":
    text = "每日限购（1/3）"
    match = re.search(r'\((\d+)', text)

    if match:
        extracted_value = match.group(1)
        print(extracted_value)
    else:
        print("未找到匹配项")
