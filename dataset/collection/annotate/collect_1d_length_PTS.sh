#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)

INPUT_FILE=$PROJECT_ROOT/annotation/1d_length/images_info.jsonl
OUTPUT_FILE=$PROJECT_ROOT/instruction/pts_raw/1d_length_pts_raw.jsonl
PROCESSED_FILE=$PROJECT_ROOT/instruction/pts_processed/1d_length_pts_processed.jsonl
PROMPT_FILE=$SCRIPT_DIR/prompts/1d_length.txt
THREAD_NUM=8
MAX_RETRIES=3

python $SCRIPT_DIR/collect_PTS.py \
    --input_file $INPUT_FILE \
    --output_file $OUTPUT_FILE \
    --prompt_file $PROMPT_FILE \
    --thread_num $THREAD_NUM \
    --max_retries $MAX_RETRIES

python $SCRIPT_DIR/filter_PTS.py \
    --input_file $OUTPUT_FILE \
    --output_file $PROCESSED_FILE