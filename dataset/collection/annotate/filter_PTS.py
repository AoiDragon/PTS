import json
import re
import argparse


def validate_and_process_content(content):
    required_tags = [
        '<think>', '</think>', 
        '<answer>', '</answer>', 
        '<hint>', '</hint>', 
        '<review>', '</review>', 
        '<reference>', '</reference>',
        '<estimation>', '</estimation>', 
        '<calculation>', '</calculation>', 
    ]
    for tag in required_tags:
        if tag not in content:
            return False, f"Missing required tag: {tag}"

    # 检查<answer>中的内容是否可以转为浮点数
    answer_match = re.search(r'<answer>(.*?)</answer>', content)
    if not answer_match:
        return False, "No answer found"
    
    try:
        float(answer_match.group(1).strip())
    except ValueError:
        return False, f"Answer cannot be converted to float: {answer_match.group(1)}"

    # 处理内容：删除标签及其前面的换行符（如果有的话）
    tags_to_remove = ['hint', 'review', 'reference', 'estimation', 'calculation']
    for tag in tags_to_remove:
        # 删除开始标签及其前面的换行符
        content = re.sub(r'\n*<{}>'.format(tag), '', content)
        # 删除结束标签及其前面的换行符
        content = re.sub(r'</{}>\n*'.format(tag), '', content)
    
    return True, content.strip()

def process_jsonl_file(args):
    """
    处理JSONL文件
    :param input_file: 输入文件路径
    :param output_file: 输出文件路径
    """
    processed_count = 0
    error_count = 0
    skipped_count = 0
    
    with open(args.input_file, 'r', encoding='utf-8') as infile, \
         open(args.output_file, 'w', encoding='utf-8') as outfile:
        
        for line in infile:
            try:
                item = json.loads(line)
                if "messages" in item and len(item["messages"]) > 1 and "content" in item["messages"][1]:
                    content = item["messages"][1]["content"]
                    is_valid, result = validate_and_process_content(content)
                    
                    if is_valid:
                        item["messages"][1]["content"] = result
                        outfile.write(json.dumps(item, ensure_ascii=False) + '\n')
                        processed_count += 1
                    else:
                        print(f"Validation error: {result} in item: {item.get('id', 'unknown')}")
                        skipped_count += 1
                else:
                    print(f"Invalid item structure, skipping: {item.get('id', 'unknown')}")
                    skipped_count += 1
                
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e} in line: {line}")
                error_count += 1
                continue
    
    print(f"Processing complete. Processed: {processed_count}, Errors: {error_count}, Skipped: {skipped_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, default="input.jsonl")
    parser.add_argument("--output_file", type=str, default="output.jsonl")
    args = parser.parse_args()
    process_jsonl_file(args)