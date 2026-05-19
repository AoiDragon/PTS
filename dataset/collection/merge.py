import json
import os

PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

# 在这里直接指定要合并的文件列表
input_files = [
    os.path.join(PROJECT_ROOT, 'grpo/2d_area/images_info.jsonl'),
    os.path.join(PROJECT_ROOT, 'grpo/1d_perimeter/images_info.jsonl'),
    os.path.join(PROJECT_ROOT, 'grpo/1d_length/images_info.jsonl'),
    ]  
output_file = os.path.join(PROJECT_ROOT, 'grpo/mixed.jsonl')  # 合并后的输出文件名

# 合并文件
with open(output_file, 'w', encoding='utf-8') as outfile:
    for file_path in input_files:
        with open(file_path, 'r', encoding='utf-8') as infile:
            for line in infile:
                # 验证是否为有效的JSON行(可选)
                try:
                    json.loads(line)
                    outfile.write(line)
                except json.JSONDecodeError:
                    print(f"跳过无效JSON行(文件: {file_path}): {line.strip()}")
                    continue

print(f"合并完成! 结果保存在 {output_file}")