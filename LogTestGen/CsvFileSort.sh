
#!/bin/bash
echo "start"

MY_PATH=/home/esa/projects/LA

SCRIPT_PATH=${MY_PATH}"/LogTestGen/"
CSV_FILE_PATH=${MY_PATH}"/LogFile/PreProsessed/EX1/"

python ${SCRIPT_PATH}CsvFileSort.py \
	-input_file ${CSV_FILE_PATH}Log_EX1_gen_track_6.csv \
	-output_file ${CSV_FILE_PATH}Log_EX1_gen_track_6_sorted.csv

