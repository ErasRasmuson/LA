
ECHO OFF

SET MY_PATH=D:\MyProjects\LA

SET SCRIPT_PATH=%MY_PATH%\LogGen\
SET OUTPUT_PATH=%MY_PATH%\LogFile\PreProsessed\

python %SCRIPT_PATH%LogGen.py ^
					-log_name "TLG_5" ^
					-event_versatility 3 ^
					-traces_max 5 ^
					-area_size  "1500x1000" ^
					-area_pixel_size  "10" ^
					-date  		 "25.01.2016" ^
					-start_time  "08:00:00" ^
					-stop_time  "09:00:00" ^
					-busstops_matrix "3x2" ^
					-busstops_area "300x300" ^
					-busstops_A 4 ^
					-busstops_B 3 ^
					-busstop_size "40x40" ^
					-bus_msg_interval 30 ^
					-bus_speed 50 ^
					-bus_speed_variance 15 ^
					-bus_amount 1 ^
					-line_route "L001:red:0:A1,M1,M3,B1" ^
					-line_route "L002:green:6:A2,M2,M3,M6,B2" ^
					-line_route "L004:blue:12:A3,M2,M3,M5,B2" ^
					-line_route "L003:magenta:18:A4,M4,B3" ^
					-line_locat_reso 10 ^
					-single_log 0 ^
					-debug 0 ^
					-output_path %OUTPUT_PATH% ^
					-gui_enable 1 ^
					-gui_zoom 0.75 ^
					-gui_line_zoom 6
