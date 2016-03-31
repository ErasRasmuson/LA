
ECHO OFF

SET MY_PATH=D:\MyProjects\LA

SET SCRIPT_PATH=%MY_PATH%\LogDig\
SET LOGS_PATH=%MY_PATH%\LogFile\PreProsessed\TRE\
SET SSD_PATH=%MY_PATH%\SSDFile\SSD_TRE_BS\
SET RESULT_PATH=%MY_PATH%\LogRes\TRE\
SET ANALYZE_PATH=%MY_PATH%\LogAna\
SET ANALYZE_FILE=logdig_TRE2

python %SCRIPT_PATH%LogDig.py ^
						-date 31.12.2015 ^
						-start_time 09:00:00 ^
						-stop_time 14:00:00 ^
						-input_logs_path %LOGS_PATH% ^
						-input_ssd_path %SSD_PATH% ^
						-output_files_path %RESULT_PATH% ^
						-analyze_file_path %ANALYZE_PATH% ^
						-analyze_file %ANALYZE_FILE% ^
						-analyze_file_mode NEW ^
						-analyzing_mode COMPARE:0 ^
						-gui_enable 1 ^
						-gui_seq_draw_mode "time" ^
						-ge_kml_enable 0 

REM						-analyzing_mode COMPARE:3 ^
REM						-analyzing_mode NORMAL:0 ^
REM						-gui_seq_draw_mode "search"