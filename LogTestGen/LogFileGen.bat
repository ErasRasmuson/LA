
ECHO OFF

SET MY_PATH=P:\Projects\LA

SET SCRIPT_PATH=%MY_PATH%\LogTestGen\
SET OUTPUT_LOG_PATH=%MY_PATH%\LogFile\PreProsessed\

python %SCRIPT_PATH%LogFileGen.py ^
					-test_name "EX1" ^
					-log_path %OUTPUT_LOG_PATH% ^
					-tble_min 1 ^
					-tble_max 1 ^
					-tbnu_min 1 ^
					-tbnu_max 1 ^
					-bctype "All" ^
					-tnu_min 3 ^
					-tnu_max 3 ^
					-bmer_min 1 ^
					-bmer_max 1 ^
					-bmer_ctrl 1 ^
					-tle_min 2 ^
					-tle_max 3 ^
					-btre_min 1 ^
					-btre_max 1 ^
					-branching_events_ctrl 1 ^
					-lver 1 ^
					-lsnoe "M" ^
					-lsnof 1 ^
					-lcnoi 100 ^
					-lcmis 100 ^
					-lcinc 100 ^
					-lsrc "gen" ^
					-lmeta "" ^
					-time_start 10 ^
					-time_ev_min 10 ^
					-time_ev_max 10 ^
					-time_etc 10 ^
					-time_ttc 10 ^
					-time_wtc 10 ^
					-gui_enable 0
