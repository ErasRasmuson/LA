
ECHO OFF

SET MY_PATH=D:\MyProjects\LogAnalyze

SET SCRIPT_PATH=%MY_PATH%\LogDig\
SET LOGS_PATH=%MY_PATH%\LogFile\PreProsessed\TLG_1\
SET RESULT_PATH=%MY_PATH%\LogRes\TLG_1\
SET ANALYZE_PATH=%MY_PATH%\LogAna\
SET ANALYZE_FILE=logdig_TLG_1_new4

python %SCRIPT_PATH%LogDig.py ^
						-date 24.02.2016 ^
						-start_time 08:00:00 ^
						-stop_time 09:00:00 ^
						-input_logs_path %LOGS_PATH% ^
						-output_files_path %RESULT_PATH% ^
						-analyze_file_path %ANALYZE_PATH% ^
						-analyze_file %ANALYZE_FILE% ^
						-analyze_file_mode NEW ^
						-analyzing_mode NORMAL:0 ^
						-gui_enable 1 ^
						-gui_seq_draw_mode "time"

REM						-analyzing_mode COMPARE:3 ^
REM						-analyzing_mode NORMAL:0 ^
REM						-gui_seq_draw_mode "search"