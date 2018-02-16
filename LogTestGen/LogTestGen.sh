
#!/bin/bash
echo "start"

MY_PATH=/home/esa/projects/LA

SCRIPT_PATH=${MY_PATH}"/LogTestGen/"
OUTPUT_LOG_PATH=${MY_PATH}"/LogFile/PreProsessed/"
OUTPUT_ANA_PATH=${MY_PATH}"/LogAna/"

python ${SCRIPT_PATH}LogTestGen.py \
					-test_name "EX1" \
					-log_path $OUTPUT_LOG_PATH \
					-ana_path $OUTPUT_ANA_PATH \
					-ana_lang "BML" \
					-b0_bmer_min 1 \
					-b0_bmer_max 1 \
					-b0_bctype "All" \
					-b1_btre_min 1 \
					-b1_btre_max 1 \
					-b2_btre_min 2 \
					-b2_btre_max 2 \
					-b2_bctype "All" \
					-b3_bmer_min 3 \
					-b3_bmer_max 3 \
					-t0_tbnu_min 1 \
					-t0_tbnu_max 1 \
					-t0_tnu_min 3 \
					-t0_tnu_max 3 \
					-t1_tle_min 3 \
					-t1_tle_max 3 \
					-t1_tble_min 1 \
					-t1_tble_max 1 \
					-t2_tle_min 2 \
					-t2_tle_max 3 \
					-t2_tble_min 1 \
					-t2_tble_max 1 \
					-t3_tnu_min 2 \
					-t3_tnu_max 3 \
					-t3_tbnu_min 1 \
					-t3_tbnu_max 1 \
					-lver 1 \
					-lsnoe "M" \
					-lsnof 1 \
					-lcnoi 100 \
					-lcmis 100 \
					-lcinc 100 \
					-lsrc "gen" \
					-lmeta "" \
					-time_start 10 \
					-time_ev_min 10 \
					-time_ev_max 10 \
					-gui_enable 0
