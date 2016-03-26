#!/bin/bash
echo "Start"

MY_PATH="/Users/EsaHeikkinen/MyProjects/LA"

SCRIPT_PATH=${MY_PATH}"/LogDig/"
LOGS_PATH=${MY_PATH}"/LogFile/PreProsessed/TLG_1/"
RESULT_PATH=${MY_PATH}"/LogRes/TLG_1/"
ANALYZE_PATH=${MY_PATH}"/LogAna/"
ANALYZE_FILE="logdig_TLG_1_new4"

python ${SCRIPT_PATH}LogDig.py \
						-date 24.02.2016 \
						-start_time 08:00:00 \
						-stop_time 09:00:00 \
						-input_logs_path $LOGS_PATH \
						-input_ssd_path $LOGS_PATH \
						-output_files_path $RESULT_PATH \
						-analyze_file_path $ANALYZE_PATH \
						-analyze_file $ANALYZE_FILE \
						-analyze_file_mode NEW \
						-analyzing_mode NORMAL:0 \
						-gui_enable 0 \
						-gui_seq_draw_mode "time"

#						-analyzing_mode COMPARE:3 ^
#						-analyzing_mode NORMAL:0 ^
#						-gui_seq_draw_mode "search"