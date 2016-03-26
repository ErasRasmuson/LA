
echo "Start"

MY_PATH="/Users/EsaHeikkinen/MyProjects/LA"

SCRIPT_PATH=${MY_PATH}"/SSDPrep/"

INPUT_PATH="/Users/esaheikkinen/Documents/tampere_gtfs_20151215/"
INPUT_FILE=stops.txt

SSD_TYPE=SSD_TRE_BS
SSD_PATH=${MY_PATH}/SSDFile/${SSD_TYPE}/

python3 ${SCRIPT_PATH}SSDPrep.py \
						-datafile_path ${INPUT_PATH} \
						-datafile_name ${INPUT_FILE} \
						-datafile_type ${SSD_TYPE} \
						-ssdfile_path ${SSD_PATH} \
						-ssdfile_name ${SSD_TYPE} \
						-stop_area_size 50
