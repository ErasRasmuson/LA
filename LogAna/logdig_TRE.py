# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	logdig_TRE.py    

AUTHOR:     Esa Heikkinen
DATE:       23.03.2016
DOCUMENT:   - 
VERSION:    "$Id$"
REFERENCES: -
PURPOSE:    
CHANGES:    "$Log$"
###############################################################################
"""
from logdig_analyze_template import *

# ----------------------------- DATA-DRIVEN PART -----------------------------
VARIABLES = {
	"INT-START-DATE":    "31.12.15",
	"INT-START-TIME":    "07:00:00",
	"INT-STOP-TIME":     "09:00:00",
	"SET-LINE-NUMBER":   "9",
	"SET-BUS-NUMBER":    "paunu_157",
	"SET-BUS-DIR":   	 "1",
	"SET-ORIGN-DIR1-BUSSTOP": "4045",
	"SET-ORIGN-DIR2-BUSSTOP": "0007",
	"SET-LINE-DIR1-BUSTOPS":  "4099,4087,4089,4097,4035,0007",
	"SET-LINE-DIR2-BUSTOPS":  "4030,4034,4106,4108,4082,4104,4045",
	"SET-MAX-SEARCH-TIME": "1600"
	}
START = {
	"state":   "BS-ORIGIN",
	"func":   "start"
	}
ESU["BS-ORIGIN"] = {
	"esu_mode":             "SEARCH_POSITION:Leaving",
	"log_varnames":         "BUS_vehicleRef=<SET-BUS-NUMBER>",
	"log_filename_expr":    "journeys_2015-12-31_COMB_<SET-BUS-NUMBER>_BUS.csv",
	"log_timecol_name":     "BUS_time",
	"log_start_time_expr":  "<CURRENT-TIME>,0",
	"log_stop_time_expr":   "<CURRENT-TIME>,+<SET-MAX-SEARCH-TIME>",
	
	"ssd_lat_col_name":   	"BUS_latitude",
	"ssd_lon_col_name":   	"BUS_longitude",
	"ssd_varnames":   		"BUSSTOP-ORIGIN",
	"ssd_filename_expr":   	"SSD_TRE_BS_<BUSSTOP-ORIGIN>.csv",

	"TF_state":    "BS-NORM-SERIAL",
	"TF_func":     "origin_bus_stop_found",
	"TN_state":    "STOP",
	"TE_state":    "STOP",
	"GUI_line_num":	"0"
}
ESU["BS-NORM-SERIAL"] = {
	"esu_mode":             "SEARCH_POSITION:Entering:Serial",
	"log_varnames":         "BUS_vehicleRef=<SET-BUS-NUMBER>",
	"log_filename_expr":    "journeys_2015-12-31_COMB_<SET-BUS-NUMBER>_BUS.csv",
	"log_timecol_name":     "BUS_time",
	"log_start_time_expr":  "<RES-BUSSTOP-START-TIME>,0",
	"log_stop_time_expr":   "<RES-BUSSTOP-START-TIME>,+<SET-MAX-SEARCH-TIME>",
	
	"ssd_lat_col_name":   	"BUS_latitude",
	"ssd_lon_col_name":   	"BUS_longitude",
	"ssd_varnames":   		"BUSSTOP-LIST",
	"ssd_filename_expr":   	"SSD_TRE_BS_<SERIAL-ID>.csv",

	"TF_state":    "BS-ORIGIN",
	"TF_func":     "bus_stops_found",
	"TN_state":    "STOP",
	"TE_state":    "STOP",
	"GUI_line_num":	"1"
}
STOP = {
	"func":     "stop"
}

# ----------------------------- FUNCTION PART -----------------------------
def start():

	print("  Transition-function: start_function")
	set_sbk_file("TRE_LINE_BS",
				 "BUS_vehicleRef","BUS_lineRef",
				 "CURRENT-DIR","BUSSTOP-ORIGIN","RES-BUSSTOP-START-TIME")
	
	set_datetime_variable("INT-START-TIMESTAMP","INT-START-DATE","INT-START-TIME")
	set_datetime_variable("INT-STOP-TIMESTAMP","INT-START-DATE","INT-STOP-TIME")
	
	copy_variable("CURRENT-TIME","INT-START-TIMESTAMP")
	copy_variable("CURRENT-DIR","SET-BUS-DIR")

	if variables["CURRENT-DIR"] == "1":
		copy_variable("BUSSTOP-ORIGIN","SET-ORIGN-DIR1-BUSSTOP")
		copy_variable("BUSSTOP-LIST","SET-LINE-DIR1-BUSTOPS")
	else:
		copy_variable("BUSSTOP-ORIGIN","SET-ORIGN-DIR2-BUSSTOP")
		copy_variable("BUSSTOP-LIST","SET-LINE-DIR2-BUSTOPS")

def origin_bus_stop_found():
	print("  Transition-function: origin_bus_stop_found")

	copy_variable("RES-BUSSTOP-START-TIME","INT-LOCAT-TIME-OLD")

def bus_stops_found():
	print("  Transition-function: bus_stops_found")

	print_sbk_file()

	if variables["CURRENT-DIR"] == "1":
		copy_variable("BUSSTOP-ORIGIN","SET-ORIGN-DIR2-BUSSTOP")
		copy_variable("BUSSTOP-LIST","SET-LINE-DIR2-BUSTOPS")
		set_variable("CURRENT-DIR","2")
	else:
		copy_variable("BUSSTOP-ORIGIN","SET-ORIGN-DIR1-BUSSTOP")
		copy_variable("BUSSTOP-LIST","SET-LINE-DIR1-BUSTOPS")
		set_variable("CURRENT-DIR","1")

	copy_variable("CURRENT-TIME","INT-LOCAT-TIME-NEW")

def stop():
	print("stop")
	print_sbk_file()
