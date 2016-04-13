
ECHO OFF

SET MY_PATH=D:\MyProjects\LA
SET SCRIPT_PATH=%MY_PATH%\LogPrep\

SET INPUT_PATH=D:\opiskelu\VANHAT\vanhat\ELMI\Lokit\
REM SET OUTPUT_PATH=D:\opiskelu\Skriptit\logs_new\

SET LOG_GROUP_NAME=ELMI
SET OUTPUT_PATH=%MY_PATH%\LogFile\PreProsessed\%LOG_GROUP_NAME%\

SET DIR_SAVE_DATE=220806
SET FILE_SAVE_DATE=210806

SET INPUT_FILE=FromCCS.txt

python %SCRIPT_PATH%LogPrep.py ^
					-input_path %INPUT_PATH%save_%DIR_SAVE_DATE%\ ^
					-input_files %INPUT_FILE% ^
					-output_path %OUTPUT_PATH% ^
					-output_sep_char "," ^
					-date %FILE_SAVE_DATE% ^
					-msg_type "RTAT" ^
					-column_name_prefix "RTAT-" ^
					-columns ""CCS-ENGINE","CCS-DAY","CCS-TIME","SIGN-NUMBER","MSG-TYPE","LINE-NUMBER","DIRECTION","BUS-NUMBER","TAT-TIME"" ^
					-regexps "\[([0-9]+)\].(..).(........).<(....)(21)([0-9][0-9][0-9][0-9A-Z][0-9A-Z][0-9A-Z])([1-2])([0][0-9A-F][0-9A-F][0-9A-F])([0-9][0-9][0-9][0-9][0-9][0-9])>" ^
					-column_oper "<MSG-TIMESTAMP>=ccs_time(<CCS-DAY>,<CCS-TIME>,%FILE_SAVE_DATE%)" ^
					-column_oper "<TAT-TIME>=ccs_rtattime(<TAT-TIME>,%FILE_SAVE_DATE%)" ^
					-column_oper "<BUS-NUMBER>=ccs_busnum(<BUS-NUMBER>)"
					
REM					-regexps "\[([0-9]+)\].(..).(........).<(....)(21)([0-9][0-9][0-9][0-9A-Z][0-9A-Z][0-9A-Z])([1-2])([0-9A-F][0-9A-F][0-9A-F][0-9A-F])([0-9][0-9][0-9][0-9][0-9][0-9])>" ^

					
python %SCRIPT_PATH%LogPrep.py ^
					-input_path %INPUT_PATH%save_%DIR_SAVE_DATE%\ ^
					-input_files %INPUT_FILE% ^
					-output_path %OUTPUT_PATH% ^
					-output_sep_char "," ^
					-date %FILE_SAVE_DATE% ^
					-msg_type "AD" ^
					-column_name_prefix "AD-" ^
					-columns ""CCS-ENGINE","CCS-DAY","CCS-TIME","SIGN-NUMBER","MSG-TYPE","LINE-NUMBER","DIRECTION","BUS-NUMBER","TYPE","VALUE"" ^
					-regexps "\[([0-9]+)\].(..).(........).<(....)(22)([0-9][0-9][0-9][0-9A-Z][0-9A-Z][0-9A-Z])([1-2])([0-9A-F][0-9A-F][0-9A-F][0-9A-F])([0-1])([0-9A-F][0-9A-F][0-9A-F][0-9A-F])>" ^
					-column_oper "<MSG-TIMESTAMP>=ccs_time(<CCS-DAY>,<CCS-TIME>,%FILE_SAVE_DATE%)" ^
					-column_oper "<BUS-NUMBER>=ccs_busnum(<BUS-NUMBER>)"
					
REM SET INPUT_FILES=Apo_304.txt,Apo_364.txt,Apo_355.txt,Apo_158.txt
SET INPUT_FILES=Apo_*.txt

python %SCRIPT_PATH%LogPrep.py ^
					-input_path %INPUT_PATH%save_%DIR_SAVE_DATE%\ ^
					-input_files %INPUT_FILES% ^
					-output_path %OUTPUT_PATH% ^
					-output_sep_char "," ^
					-date %FILE_SAVE_DATE% ^
					-msg_type "LOG" ^
					-column_name_prefix "LOG-" ^
					-columns ""MSG-TYPE","BASESTATION","MSG-DAY","MSG-MONTH","MSG-TIME","BUS-NUMBER","BUS-NUMBER-HEX","LINE-NUMBER","DIRECTION"" ^
					-regexps "(LO[A-Z]+)\[([0-9]+)\].(..).(..).(........).([0-9]+).<([0-9A-Z][0-9A-Z][0-9A-Z][0-9A-Z])....([0-9][0-9][0-9][0-9A-Z][0-9A-Z][0-9A-Z]).([1-2])>" ^
					-column_oper "<MSG-TIMESTAMP>=bus_time(<MSG-DAY>,<MSG-MONTH>,<MSG-TIME>,%FILE_SAVE_DATE%)"
					
python %SCRIPT_PATH%LogPrep.py ^
					-input_path %INPUT_PATH%save_%DIR_SAVE_DATE%\ ^
					-input_files %INPUT_FILES% ^
					-output_path %OUTPUT_PATH% ^
					-output_sep_char "," ^
					-date %FILE_SAVE_DATE% ^
					-msg_type "LOCAT" ^
					-column_name_prefix "LOCAT-" ^
					-columns ""MSG-TYPE","BASESTATION","MSG-DAY","MSG-MONTH","MSG-TIME","BUS-NUMBER","BUS-NUMBER-HEX","LATITUDE","LONGITUDE","SEC","ODOM","ALM3","DGPS","GPS"" ^
					-regexps "(LO[A-Z]+)\[([0-9]+)\].(..).(..).(........).([0-9]+).<([0-9A-Z][0-9A-Z][0-9A-Z][0-9A-Z])....([0-9]+).([0-9]+).SEC=([0-9]+).ODO=([0-9]+).ALM3=(.).DGPS=(.).GPS=(.)>" ^
					-column_oper "<MSG-TIMESTAMP>=bus_time(<MSG-DAY>,<MSG-MONTH>,<MSG-TIME>,%FILE_SAVE_DATE%)" ^
					-column_oper "<LATITUDE>=coord_ms2aadd(<LATITUDE>)" ^
					-column_oper "<LONGITUDE>=coord_ms2aadd(<LONGITUDE>)"
				
SET INPUT_FILE=BQD_log.txt

python %SCRIPT_PATH%LogPrep.py ^
					-input_path %INPUT_PATH%save_%DIR_SAVE_DATE%\ ^
					-input_files %INPUT_FILE% ^
					-output_path %OUTPUT_PATH% ^
					-output_sep_char "," ^
					-date %FILE_SAVE_DATE% ^
					-msg_type "BQD" ^
					-column_name_prefix "BQD-" ^
					-columns ""YEAR","MONTH","DAY","TIME","BUS-NUMBER","LINE-NUMBER","EVENT","STR"" ^
					-regexps "(....).(..).(..) (........) APO= *([0-9]+) LINE=(......) E=(.) BQD=(.*)" ^
					-column_oper "<MSG-TIMESTAMP>=bqd_bus_time(<YEAR>,<MONTH>,<DAY>,<TIME>)"
					

