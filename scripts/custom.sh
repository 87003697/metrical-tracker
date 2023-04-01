INPUT_VIDEO="empty"
OUTPUT_DIR="empty"

if [ -n "$1" ]; then INPUT_VIDEO=${1}; fi
if [ -n "$2" ]; then OUTPUT_DIR=${2}; fi

python tracker_custom.py \
    --input_video ${INPUT_VIDEO} \
    --output_dir ${OUTPUT_DIR}