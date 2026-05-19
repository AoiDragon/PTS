# 根据question和answer直接生成一段话的回复
# 答案放在\boxed里
import json
import os

PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')

input_files = [
    os.path.join(PROJECT_ROOT, 'annotation/1d_length/images_info.jsonl'),
    os.path.join(PROJECT_ROOT, 'annotation/1d_perimeter/images_info.jsonl'),
    os.path.join(PROJECT_ROOT, 'annotation/2d_area_accurate/images_info.jsonl'),
    os.path.join(PROJECT_ROOT, 'annotation/2d_area_bbox/images_info.jsonl'),
]
output_file = os.path.join(PROJECT_ROOT, 'instruction/direct/data.json')

output = []
for file_path in input_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = json.loads(line)
            new_item = {
                "messages":[
                    {
                        "content": line["question"] + " The final answer should be placed within \\boxed{}.",
                        "role": "user"
                    },
                    {
                        "content": f"\\boxed{{{line['answer']}}}",
                        "role": "assistant"
                    }
                ],
                "images": line["image"] if isinstance(line["image"], list) else [line["image"]]
            }
            output.append(new_item)

print(len(output))
with open(output_file, 'w') as f:
    json.dump(output, f, indent=4)
