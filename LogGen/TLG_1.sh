#!/bin/bash

echo "Start"

MY_PATH="/Users/EsaHeikkinen/MyProjects/LA"

SCRIPT_PATH=${MY_PATH}"/LogGen/"
OUTPUT_PATH=${MY_PATH}"/LogFile/"

python ${SCRIPT_PATH}LogGen.py \
					-log_name "TLG_1" \
					-event_versatility 3 \
					-traces_max 2 \
					-area_size  "1000x600" \
					-area_pixel_size  "10" \
					-date  		 "24.02.2016" \
					-start_time  "08:00:00" \
					-stop_time  "09:00:00" \
					-busstops_matrix "1x1" \
					-busstops_area "100x100" \
					-busstops_A 1 \
					-busstops_B 1 \
					-busstop_size "40x40" \
					-bus_msg_interval 30 \
					-bus_speed 50 \
					-bus_speed_variance 15 \
					-bus_amount 1 \
					-line_route "L001:red:0:A1,M1,B1" \
					-line_locat_reso 10 \
					-single_log 0 \
					-debug 0 \
					-output_path $OUTPUT_PATH \
					-gui_enable 1 \
					-gui_zoom 0.75 \
					-gui_line_zoom 6
