# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	SSDPrep.py    

AUTHOR:     Esa Heikkinen
DATE:       21.03.2016
DOCUMENT:   - 
VERSION:    "$Id$"
REFERENCES: -
PURPOSE:    
CHANGES:    "$Log$"
###############################################################################
"""

import argparse
import os.path
import sys
import time
import re
from datetime import datetime
import configparser

lib_path = os.path.abspath(os.path.join('..', 'LogCom'))
sys.path.append(lib_path)
from MapGEkml import *

g_version = "$Id$"


#******************************************************************************
#
#	FUNCTION:	write_ssd_datafile
#
#******************************************************************************
def write_ssd_datafile(ssd_file_path,ssdfile_name,stop_id,stop_lat,stop_lon,stop_area_size,klm_file_path_name):

	#print("write_ssd_datafile: stop_id=%s, stop_lat=%s, stop_lon=%s, stop_area_size=%s m" % (stop_id,stop_lat,stop_lon,stop_area_size))

	ssd_file_name = ssdfile_name + "_" + stop_id + ".csv"
	ssd_path_file_name = os.path.join(ssd_file_path,ssd_file_name)
	
	make_dir_if_no_exist(ssd_path_file_name)

	# Muutetaan laatikoon metri-arvot koordinaattirajoiksi
	lon_diff = int(stop_area_size) / 0.015 / 3600000.0
	lat_diff = int(stop_area_size) / 0.03 / 3600000.0
	area_left_down_lon = float(stop_lon) - lon_diff
	area_left_down_lat = float(stop_lat) - lat_diff
	area_right_up_lon = float(stop_lon) + lon_diff
	area_right_up_lat = float(stop_lat) + lat_diff

	#print("area_left_down_lon = %s" % area_left_down_lon)
	#print("area_left_down_lat = %s" % area_left_down_lat)
	#print("area_right_up_lon  = %s" % area_right_up_lon)
	#print("area_right_up_lat  = %s" % area_right_up_lat)

	f = open(ssd_path_file_name, 'w')

	f.writelines("Counter,Longitude,Latitude\n")

	ssd_str = "1,%s,%s\n" % (area_left_down_lon,area_left_down_lat) 
	f.writelines(ssd_str)

	ssd_str = "2,%s,%s\n" % (area_left_down_lon,area_right_up_lat)
	f.writelines(ssd_str)

	ssd_str = "3,%s,%s\n" % (area_right_up_lon,area_right_up_lat)
	f.writelines(ssd_str)

	ssd_str = "4,%s,%s\n" % (area_right_up_lon,area_left_down_lat)
	f.writelines(ssd_str)	

	# Kirjoitetaan alue Google Earthin kml-tiedostoon
	coord_list = []
	coord_list.append([area_left_down_lon,area_left_down_lat])
	coord_list.append([area_left_down_lon,area_right_up_lat])
	coord_list.append([area_right_up_lon,area_right_up_lat])
	coord_list.append([area_right_up_lon,area_left_down_lat])
	coord_list.append([area_left_down_lon,area_left_down_lat])	
	write_area_to_kml_file(klm_file_path_name,stop_id,coord_list,200)

	# Kirjoitetaan piste Google Earthin kml-tiedostoon
	coord_list = [[stop_lon,stop_lat]]
	write_point_to_kml_file(klm_file_path_name,stop_id,coord_list,200)

	f.close()

#******************************************************************************
#
#	FUNCTION:	convert_TRE_BS_datafile_to_ssdfile
#
#******************************************************************************
def convert_TRE_BS_datafile_to_ssdfile(datafile_type,datafile_path,datafile_name,ssdfile_path,ssdfile_name,stop_area_size):

	
	datafile_path_name = datafile_path + datafile_name
	klm_file_path_name = ssdfile_path + datafile_type + ".kml"

	if os.path.isfile(datafile_path_name):
	
		f = open(datafile_path_name, 'r', encoding='utf-8')
		lines = f.readlines()
		f.close()

		# Alustetaan Google Earthin klm-tiedosto
		init_kml_file(klm_file_path_name,datafile_type,"")

		line_counter = 0
		sel_line_counter = 0					
		# Kaydaan lapi loki-tiedoston rivit
		for line in lines:
		
			# Hylätään tyhjät rivit
			if len(line) < 2:
				continue
		
			# Poistetaan rivinvaihdot riviltä
			line = line.replace("\n","")
		
			line_counter += 1
			line_list = line.split(",")
			line_list_len = len(line_list)

			line_type = "Unknown"
			if line_counter == 1:
				line_type = "Header"
			else:
				line_type = "Data"

				if line_list_len > 4:
					sel_line_counter += 1
					stop_id = line_list[0]
					stop_lat = line_list[3]
					stop_lon = line_list[4]
					print("%5d: stop_id=%s: stop_lat=%s: stop_lon=%s" % (line_counter,stop_id,stop_lat,stop_lon))

					write_ssd_datafile(ssdfile_path,ssdfile_name,stop_id,stop_lat,stop_lon,stop_area_size,
										klm_file_path_name)

			#print("%5d: %s: %s" % (line_counter,line_type,line_list))

		# Lopputekstit klm-tiedostoon
		finalize_kml_file(klm_file_path_name)

		print("\n -- Wrote %s ssd-files to: %s \n" % (sel_line_counter,ssdfile_path))


#******************************************************************************
#
#	FUNCTION:	make_dir_if_no_exist
#
#******************************************************************************
def make_dir_if_no_exist(file_path_name):
	# Python3
	#os.makedirs(os.path.dirname(file_path_name), exist_ok=True)

	# Python2
	if not os.path.exists(os.path.dirname(file_path_name)):
		try:
			os.makedirs(os.path.dirname(file_path_name))
		except OSError as exc:
			if exc.errno != errno.EEXIST:
				raise

#******************************************************************************
#
#	FUNCTION:	main
#
#******************************************************************************
def main():

	print("version: %s" % g_version)

	parser = argparse.ArgumentParser()
	parser.add_argument('-datafile_path','--datafile_path', dest='datafile_path', help='datafile_path')
	parser.add_argument('-datafile_name','--datafile_name', dest='datafile_name', help='datafile_name')
	parser.add_argument('-datafile_type','--datafile_type', dest='datafile_type', help='datafile_type')
	parser.add_argument('-ssdfile_path','--ssdfile_path', dest='ssdfile_path', help='ssdfile_path')
	parser.add_argument('-ssdfile_name','--ssdfile_name', dest='ssdfile_name', help='ssdfile_name')
	parser.add_argument('-stop_area_size','--stop_area_size', dest='stop_area_size', type=int, help='stop_area_size')

	args = parser.parse_args()

	print("datafile_path    : %s" % args.datafile_path)
	print("datafile_name    : %s" % args.datafile_name)
	print("datafile_type    : %s" % args.datafile_type)
	print("ssdfile_path     : %s" % args.ssdfile_path)
	print("ssdfile_name     : %s" % args.ssdfile_name)
	print("stop_area_size   : %s m" % args.stop_area_size)

	print("\n")

	start_time = time.time()

	if args.datafile_type == "SSD_TRE_BS":
		convert_TRE_BS_datafile_to_ssdfile(args.datafile_type,args.datafile_path,args.datafile_name,
			args.ssdfile_path,args.ssdfile_name,args.stop_area_size)
	else:
		print("ERR: Unknown datafile_type: %s" % args.datafile_type)

	print("\n Total execution time: %.3f seconds" % (time.time() - start_time))

if __name__ == '__main__':
    main()