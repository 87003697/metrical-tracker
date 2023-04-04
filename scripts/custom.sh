INPUT_VIDEO="empty"
OUTPUT_DIR="empty"
CROP=none

if [ -n "$1" ]; then INPUT_VIDEO=${1}; fi
if [ -n "$2" ]; then OUTPUT_DIR=${2}; fi
if [ -n "$3" ]; then CROP=${3}; fi

python tracker_custom.py \
    --input_video ${INPUT_VIDEO} \
    --output_dir ${OUTPUT_DIR} \
    --crop ${CROP}