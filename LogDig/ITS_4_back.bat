
ECHO OFF


REM SET MY_PATH=D:\Projekti\Koodit\LA
SET MY_PATH=P:\Projects\LA

SET SCRIPT_PATH=%MY_PATH%\LogDig\
SET LOGS_PATH=%MY_PATH%\LogFile\PreProsessed\ITS\
SET SSD_PATH=%MY_PATH%\SSDFile\ITS\
SET RESULT_PATH=%MY_PATH%\LogRes\ITS\
SET ANALYZE_PATH=%MY_PATH%\LogAna\
SET ANALYZE_FILE=ITS_4_back

python %SCRIPT_PATH%LogDig.py ^
						-date 01.01.2012 ^
						-start_time 00:00:00 ^
						-stop_time 23:59:59 ^
						-input_logs_path %LOGS_PATH% ^
						-input_ssd_path %SSD_PATH% ^
						-output_files_path %RESULT_PATH% ^
						-analyze_file_path %ANALYZE_PATH% ^
						-analyze_file %ANALYZE_FILE% ^
						-analyze_file_mode NEW ^
						-analyzing_mode NORMAL:0 ^
						-gui_enable 0 ^
						-gui_seq_draw_mode "time" ^
						-ge_kml_enable 0 ^
						-debug 0
