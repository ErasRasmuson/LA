
ECHO OFF

SET INPUT_PATH=D:\opiskelu\Tampere_data\tampere_gtfs_20151215\
SET INPUT_FILE=stops.txt

SET SSD_TYPE=SSD_TRE_BS

SET MY_PATH=D:\MyProjects\LA
SET SCRIPT_PATH=%MY_PATH%\SSDPrep\
SET SSD_PATH=%MY_PATH%\SSDFile\%SSD_TYPE%\

python %SCRIPT_PATH%SSDPrep.py ^
						-datafile_path %INPUT_PATH% ^
						-datafile_name %INPUT_FILE% ^
						-datafile_type %SSD_TYPE% ^
						-ssdfile_path %SSD_PATH% ^
						-ssdfile_name %SSD_TYPE% ^
						-stop_area_size 50
