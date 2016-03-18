
ECHO OFF

SET MY_PATH=D:\MyProjects\LA
SET SCRIPT_PATH=%MY_PATH%\LogPrep\

SET INPUT_PATH=D:\opiskelu\Tampere_data\Bd2016\Bd2016\

SET LOG_GROUP_NAME=TRE
SET OUTPUT_PATH=%MY_PATH%\LogFile\PreProsessed\%LOG_GROUP_NAME%\

SET FILE_DATE=2015-12-31
SET FILE_SAVE_DATE=311215

REM SET INPUT_FILES=journeys_%FILE_DATE%*.csv
REM SET INPUT_FILES=journeys_%FILE_DATE%-07*.csv
SET INPUT_FILES=journeys_%FILE_DATE%-07.csv,journeys_%FILE_DATE%-08.csv

python %SCRIPT_PATH%LogPrep.py ^
					-input_path %INPUT_PATH% ^
					-input_files %INPUT_FILES% ^
					-input_read_mode COMBINE ^
					-combined_file_name journeys_%FILE_DATE%_COMB^
					-output_path %OUTPUT_PATH% ^
					-output_files_divide_col "vehicleRef" ^
					-output_sep_char "," ^
					-date %FILE_SAVE_DATE% ^
					-msg_type "BUS" ^
					-column_name_prefix "BUS_" ^
					-columns "" ^
					-regexps ""
					