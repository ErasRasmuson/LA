#!/bin/bash

echo "Start"

MY_PATH="/Users/EsaHeikkinen/MyProjects/LA"

SCRIPT_PATH=${MY_PATH}"/LogPrep/"
OUTPUT_PATH=${MY_PATH}"/LogFile/"

INPUT_PATH="/Users/esaheikkinen/Documents/Bd2016/"

LOG_GROUP_NAME=TRE
OUTPUT_PATH=${MY_PATH}/LogFile/PreProsessed/${LOG_GROUP_NAME}/

FILE_DATE=2015-12-31
FILE_SAVE_DATE=311215

INPUT_FILES=journeys_${FILE_DATE}-07.csv,journeys_${FILE_DATE}-08.csv

python ${SCRIPT_PATH}LogPrep.py \
					-input_path $INPUT_PATH \
					-input_files $INPUT_FILES \
					-input_read_mode COMBINE \
					-combined_file_name journeys_${FILE_DATE}_COMB \
					-output_path $OUTPUT_PATH \
					-output_files_divide_col "vehicleRef" \
					-output_sep_char "," \
					-date $FILE_SAVE_DATE \
					-msg_type "BUS" \
					-column_name_prefix "BUS_" \
					-columns "" \
					-regexps ""
