import os
import re
import json
import time
import openai
from openai import RateLimitError
import multiprocessing
from tqdm import tqdm
import argparse


def load_prompt_template(prompt_file_path):
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def read_jsonl(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def append_jsonl(file_path, data):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def check_string_format(s):
    pattern = r'^<think>[\s\S]*</think>\s*<answer>[\s\S]*</answer>$'
    return bool(re.match(pattern, s, re.DOTALL))

def chat(messages, max_retries=3, retry_delay=10):
    base_url = "https://search-va.byteintl.net/gpt/openapi/online/multimodal/crawl"
    api_version = "gpt-4o-2024-08-06"
    model_name = "gpt-4o-2024-08-06"
    max_tokens = 4096  # range: [0, 4096]

    client = openai.AzureOpenAI(
        azure_endpoint=base_url,
        api_version=api_version,
        api_key=os.environ.get("OPENAI_API_KEY", "")
    )

    for retry in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                extra_headers={"X-TT-LOGID": "test"},
            )
            res = json.loads(completion.model_dump_json())["choices"][0]["message"]["content"]
            print(res)
            
            if check_string_format(res):
                return res
            print("Response format is incorrect. Retrying...")
        except RateLimitError:
            print(f"Rate limit exceeded. Sleeping for {retry_delay} seconds...")
            time.sleep(retry_delay)
        except Exception as e:
            print(f"Error during API call (attempt {retry + 1}): {str(e)}")
    
    print("Max retries reached. Unable to generate a valid response.")
    return None

def process_item(item, prompt_template, output_file):
    messages = [
        {"role": "user", "content": prompt_template + '\n' + str(item)}
    ]
    res = chat(messages)

    if res is not None:
        new_item = {
            "id": item["id"],
            "messages": [
                {"content": item['question'], "role": "user"},
                {"content": res, "role": "assistant"}
            ],
            "images": [item["image"]]
        }
        append_jsonl(output_file, new_item)

def main(args):
    prompt_template = load_prompt_template(args.prompt_file)

    if not os.path.exists(args.output_file):
        with open(args.output_file, "w", encoding="utf-8") as f:
            pass

    annotations = read_jsonl(args.input_file)

    # 删除annotations中的symbolization results
    def remove_symbolization_result(data):
        if isinstance(data, dict):
            # Remove the key if it exists in the current dictionary
            data.pop("symbolization_result", None)
            # Recursively process all values in the dictionary
            for key, value in data.items():
                data[key] = remove_symbolization_result(value)
        elif isinstance(data, list):
            # Process each item in the list
            data = [remove_symbolization_result(item) for item in data]
        return data

    annotations = remove_symbolization_result(annotations)

    existed_thought = read_jsonl(args.output_file)
    
    existed_ids = {item["id"] for item in existed_thought}
    annotations_for_thought = [item for item in annotations if item["id"] not in existed_ids]

    with multiprocessing.Pool(processes=args.thread_num) as pool:
        with tqdm(total=len(annotations_for_thought)) as pbar:
            from functools import partial
            process_func = partial(process_item, 
                                  prompt_template=prompt_template,  # 使用加载的 prompt
                                  output_file=args.output_file)
            
            for _ in pool.imap(process_func, annotations_for_thought):
                pbar.update(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process spatial reasoning data with GPT-4")
    parser.add_argument("--input_file", required=True, help="Path to input JSONL file")
    parser.add_argument("--output_file", required=True, help="Path to output JSONL file")
    parser.add_argument("--prompt_file", required=True, help="Path to prompt template file") 
    parser.add_argument("--thread_num", type=int, default=16, help="Number of threads for processing")
    parser.add_argument("--max_retries", type=int, default=3, help="Max API retry attempts")
    args = parser.parse_args()
    main(args)