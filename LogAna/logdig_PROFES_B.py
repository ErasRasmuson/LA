# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	logdig_PROFES_B.py    

AUTHOR:     Esa Heikkinen
DATE:       11.07.2016
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
	"INT-START-DATE":    "14.04.16",
	"INT-START-TIME":    "07:00:00",
	"INT-STOP-TIME":     "07:30:00",
	"SET-LINE-NUMBER":   "L001",
	"SET-MAX-LOGIN-RTAT-TIME": "600",
	"SET-MAX-START-PASS-TIME": "430",
	"SET-MAX-RTAT-PASS-TIME":  "1200",
	"SET-MAX-PASS-ERR-TIME":   "120"
	}
START = {
	"state":   "RTAT",
	"func":   "start"
	}
ESU["RTAT"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "ccs_rtat.csv",
	"log_varnames":         "RTAT-LINE=<SET-LINE-NUMBER>",
	"log_timecol_name":     "RTAT-TIME",
	"log_start_time_expr":  "<INT-START-TIMESTAMP>,+1",
	"log_stop_time_expr":   "<INT-STOP-TIMESTAMP>,<INT-STOP-TIMESTAMP-OFFSET>",
	
	"TF_state":    "LOGIN",
	"TF_func":     "RTAT_found_function",
	"TN_state":    "STOP",
	"TE_state":    "STOP",
	"GUI_line_num":	"0"
}
ESU["LOGIN"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "bus_login.csv",
	"log_varnames":         "LOG-TYPE=LOGIN,LOG-LINE=<RTAT-LINE>,LOG-BUS=<RTAT-BUS>,LOG-LINE-DIR=<RTAT-LINE-DIR>",
	"log_timecol_name":     "LOG-TIME",
	"log_start_time_expr":  "<RTAT-TIME>,-<SET-MAX-LOGIN-RTAT-TIME>",
	"log_stop_time_expr":   "<RTAT-TIME>,0",
	
	"TF_state":    "BS-START",
	"TN_state":    "STOP",
	"TE_state":    "STOP",
	"GUI_line_num":	"1"
}
ESU["BS-START"] = {
	"esu_mode":             "SEARCH_POSITION:Leaving",
	"log_filename_expr":    "bus_coords_<LOCAT-BUS>.csv",
	"log_varnames":         "LOCAT-BUS=<RTAT-BUS>",
	"log_timecol_name":     "LOCAT-TIME",
	"log_start_time_expr":  "<LOG-TIME>,0",
	"log_stop_time_expr":   "<LOG-TIME>,+<SET-MAX-RTAT-PASS-TIME>",
	
	"ssd_lat_col_name":   	"LOCAT-Y",
	"ssd_lon_col_name":   	"LOCAT-X",
	"ssd_varnames":   		"START-BUSSTOP",
	"ssd_filename_expr":   	"area_coords_<START-BUSSTOP>.csv",

	"TF_state":    "BS-PASS",
	"TF_func":     "START_found_function",
	"TN_state":    "STOP",
	"TE_state":    "STOP",
	"GUI_line_num":	"2"
}
ESU["BS-PASS"] = {
	"esu_mode":             "SEARCH_POSITION:Entering",
	"log_filename_expr":    "bus_coords_<LOCAT-BUS>.csv",
	"log_varnames":         "LOCAT-BUS",
	"log_timecol_name":     "LOCAT-TIME",
	"log_start_time_expr":  "<RES-BUS-START-TIME>,0",
	"log_stop_time_expr":   "<RES-BUS-START-TIME>,+<SET-MAX-RTAT-PASS-TIME>",
	
	"ssd_lat_col_name":  	"LOCAT-Y",
	"ssd_lon_col_name":   	"LOCAT-X",
	"ssd_varnames":   		"RTAT-BUSSTOP",
	"ssd_filename_expr":   	"area_coords_<RTAT-BUSSTOP>.csv",

	"TF_state":    "AD",
	"TF_func":     "PASS_found_function",
	"TN_state":    "STOP",
	"TE_state":    "STOP",
	"GUI_line_num":	"3"
}
ESU["AD"] = {
	"esu_mode":             "SEARCH_EVENT:Last",
	"log_filename_expr":    "ccs_ad.csv",
	"log_varnames":         "AD-LINE=<SET-LINE-NUMBER>,AD-BUS=<RTAT-BUS>,AD-BUS-DIR=<RTAT-LINE-DIR>",
	"log_timecol_name":     "AD-TIME",
	"log_start_time_expr":  "<RTAT-TIME>,0",
	"log_stop_time_expr":   "<RES-BUSSTOP-PASS-TIME>,0",
	
	"TF_state":    "LOGOUT",
	"TN_state":    "STOP",
	"TE_state":    "STOP",
	"GUI_line_num":	"4"
}
ESU["LOGOUT"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "bus_login.csv",
	"log_varnames":         "LOG-TYPE=LOGOUT,LOG-LINE,LOG-BUS",
	"log_timecol_name":     "LOG-TIME",
	"log_start_time_expr":  "<RES-BUSSTOP-PASS-TIME>,0",
	"log_stop_time_expr":   "<RES-BUSSTOP-PASS-TIME>,1200",
	
	"TF_state":    "STOP",
	"TF_func":     "LOGOUT_found_function",
	"TN_state":    "STOP",
	"TE_state":    "STOP",
	"GUI_line_num":	"5"
}
STOP = {
	"func":     "stop"
}

# ----------------------------- FUNCTION PART -----------------------------
def start():

	global flip_flop

	flip_flop = 0

	print("  Transition-function: start_function")
	set_sbk_file("PROFES_B",
				 "LOG-BUS","SET-LINE-NUMBER",
				 "RES-BUS-START-TIME","RES-BUSSTOP-PASS-TIME",
				 "RES-TIME-DIFF","RES-TIME-DIFF-SEC",
				 "ERR-TIME")
	
	set_datetime_variable("INT-START-TIMESTAMP","INT-START-DATE","INT-START-TIME")
	set_datetime_variable("INT-STOP-TIMESTAMP","INT-START-DATE","INT-STOP-TIME")
	set_variable("INT-STOP-TIMESTAMP-OFFSET",0)

def RTAT_found_function():

	global flip_flop

	print("")
	print("  Transition-function: RTAT_found_function")

	if flip_flop == 0:
		set_variable("START-BUSSTOP","A1")
		flip_flop = 1
	else:
		set_variable("START-BUSSTOP","B1")
		flip_flop = 0

	#copy_variable("INT-START-TIMESTAMP","RTAT-TIME")

def START_found_function():
	print("")
	print("  Transition-function: START_found_function")
	copy_variable("RES-BUS-START-TIME","INT-LOCAT-TIME-OLD")

def PASS_found_function():
	print("")
	print("  Transition-function: PASS_found_function")
	copy_variable("RES-BUSSTOP-PASS-TIME","INT-LOCAT-TIME-OLD")
	calc_time_diff("RES-TIME-DIFF","RES-TIME-DIFF-SEC","RES-BUSSTOP-PASS-TIME","RES-BUS-START-TIME")
	compare_variable("ERR-TIME","RES-TIME-DIFF-SEC",">","SET-MAX-START-PASS-TIME")

def LOGOUT_found_function():
	print("")
	print("  Transition-function: LOGOUT_found_function")
	copy_variable("INT-START-TIMESTAMP","LOG-TIME")
	copy_variable("INT-STOP-TIMESTAMP","LOG-TIME")
	set_variable("INT-STOP-TIMESTAMP-OFFSET",2700)

	print_sbk_file()

def stop():
	print("stop")
	print_sbk_file()
