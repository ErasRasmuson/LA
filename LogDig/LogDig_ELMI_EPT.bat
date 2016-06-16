
ECHO OFF

SET MY_PATH=D:\MyProjects\LA

SET SCRIPT_PATH=%MY_PATH%\LogDig\
SET LOGS_PATH=%MY_PATH%\LogFile\PreProsessed\ELMI\
SET SSD_PATH=%MY_PATH%\SSDFile\ELMI\
SET RESULT_PATH=%MY_PATH%\LogRes\ELMI\
SET ANALYZE_PATH=%MY_PATH%\LogAna\
SET ANALYZE_FILE=logdig_ELMI_EPT

python %SCRIPT_PATH%LogDig.py ^
						-date 21.08.2006 ^
						-start_time 07:00:00 ^
						-stop_time 09:30:00 ^
						-input_logs_path %LOGS_PATH% ^
						-input_ssd_path %SSD_PATH% ^
						-output_files_path %RESULT_PATH% ^
						-analyze_file_path %ANALYZE_PATH% ^
						-analyze_file %ANALYZE_FILE% ^
						-analyze_file_mode NEW ^
						-analyzing_mode NORMAL:0 ^
						-gui_enable 1 ^
						-gui_seq_draw_mode "order"

REM						-analyzing_mode COMPARE:3 ^
REM						-analyzing_mode NORMAL:0 ^
REM						-gui_seq_draw_mode "search"
REM						-gui_seq_draw_mode "order"