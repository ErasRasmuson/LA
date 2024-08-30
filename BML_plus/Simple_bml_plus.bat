
REM ECHO OFF

SET MY_PATH=D:\Projekti\Koodit\LA

SET SCRIPT_PATH=%MY_PATH%\LogDig\
SET LOGS_PATH=%MY_PATH%\LogFile\PreProsessed\Simple\
SET SSD_PATH=%MY_PATH%\SSDFile\Simple\
SET RESULT_PATH=%MY_PATH%\LogRes\Simple\
SET ANALYZE_PATH=%MY_PATH%\LogAna\
SET ANALYZE_FILE=Simple_bml_plus

SET BML_PATH=%MY_PATH%\BML_plus\

REM Compiles higher level bml+ language into LogDig's python based bml language 
python %BML_PATH%BML_plus_compiler.py -bml_plus_path %BML_PATH% -bml_plus_file %ANALYZE_FILE%.bml

cp %BML_PATH%%ANALYZE_FILE%.py %ANALYZE_PATH%\

cd %SCRIPT_PATH%

REM Does analysis
python %SCRIPT_PATH%LogDig.py ^
						-date 21.06.2016 ^
						-start_time 12:00:00 ^
						-stop_time 12:20:00 ^
						-input_logs_path %LOGS_PATH% ^
						-input_ssd_path %SSD_PATH% ^
						-output_files_path %RESULT_PATH% ^
						-analyze_file_path %ANALYZE_PATH% ^
						-analyze_file %ANALYZE_FILE% ^
						-analyze_file_mode NEW ^
						-analyzing_mode NORMAL:0 ^
						-gui_enable 0 ^
						-gui_seq_draw_mode "order" ^
						-ge_kml_enable 0
 
cd %BML_PATH%
