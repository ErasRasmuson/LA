#!/bin/sh
echo "start"

MY_PATH=${HOME}/projects/LA

SCRIPT_PATH=${MY_PATH}/LogDig/
LOGS_PATH=${MY_PATH}/LogFile/PreProsessed/Simple/
SSD_PATH=${MY_PATH}/SSDFile/Simple/
RESULT_PATH=${MY_PATH}/LogRes/Simple/
ANALYZE_PATH=${MY_PATH}/LogAna/
ANALYZE_FILE=Simple_bml_plus

BML_PATH=${MY_PATH}/BML_plus/

# Compiles higher level bml+ language into LogDig's python based bml language 
python3 ${BML_PATH}BML_plus_compiler.py -bml_plus_path $BML_PATH -bml_plus_file ${ANALYZE_FILE}.bml

cp ${BML_PATH}${ANALYZE_FILE}.py ${ANALYZE_PATH}

cd $SCRIPT_PATH

# Does analysis
python3 ${SCRIPT_PATH}LogDig.py \
	-date 21.06.2016 \
	-start_time 12:00:00 \
	-stop_time 12:20:00 \
	-input_logs_path $LOGS_PATH \
	-input_ssd_path $SSD_PATH \
	-output_files_path $RESULT_PATH \
	-analyze_file_path $ANALYZE_PATH \
	-analyze_file $ANALYZE_FILE \
	-analyze_file_mode NEW \
	-analyzing_mode NORMAL:0 \
	-gui_enable 0 \
	-gui_seq_draw_mode "order" \
	-ge_kml_enable 0
 
cd $BML_PATH
