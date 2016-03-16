# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	logdig_TLG_1_new.py    

AUTHOR:     Esa Heikkinen
DATE:       01.03.2016
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
	"INT-START-DATE":    "24.02.16",
	"INT-START-TIME":    "07:00:00",
	"INT-STOP-TIME":     "10:00:00",
	"SET-LINE-NUMBER":   "L001",
	"SET-MAX-LOGIN-RTAT-TIME": "1200",
	"SET-MAX-START-PASS-TIME": "430",
	"SET-MAX-RTAT-PASS-TIME":  "1800",
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
	"log_stop_time_expr":   "<INT-STOP-TIMESTAMP>,0",
	
	"TF_state":    "LOGIN",
	"TF_func":     "RTAT_found_function",
	"TN_state":    "STOP",
	"TN_func":     "",
	"TE_state":    "STOP",
	"TE_func":     "",
	"onentry_func": "",
	"onexit_func": ""
}
ESU["LOGIN"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "bus_login.csv",
	"log_varnames":         "LOG-LINE=<RTAT-LINE>, LOG-BUS=<RTAT-BUS>, LOG-LINE-DIR=<RTAT-LINE-DIR>",
	"log_timecol_name":     "LOG-TIME",
	"log_start_time_expr":  "<RTAT-TIME>,-<SET-MAX-LOGIN-RTAT-TIME>",
	"log_stop_time_expr":   "<RTAT-TIME>,0",
	
	"TF_state":    "BS-START",
	"TF_func":     "LOGIN_found_funtion",
	"TN_state":    "STOP",
	"TN_func":     "",
	"TE_state":    "STOP",
	"TE_func":     "",
	"onentry_func": "",
	"onexit_func": ""
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
	"TN_func":     "",
	"TE_state":    "STOP",
	"TE_func":     "",
	"onentry_func": "",
	"onexit_func": ""
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
	"TN_func":     "",
	"TE_state":    "STOP",
	"TE_func":     "",
	"onentry_func": "",
	"onexit_func": ""
}
ESU["AD"] = {
	"esu_mode":             "SEARCH_EVENT:Last",
	"log_filename_expr":    "ccs_ad.csv",
	"log_varnames":         "AD-LINE=<SET-LINE-NUMBER>, AD-BUS=<RTAT-BUS>, AD-BUS-DIR=<RTAT-LINE-DIR>",
	"log_timecol_name":     "AD-TIME",
	"log_start_time_expr":  "<RTAT-TIME>,0",
	"log_stop_time_expr":   "<RES-BUSSTOP-PASS-TIME>,0",
	
	"TF_state":    "LOGOUT",
	"TF_func":     "AD_found_function",
	"TN_state":    "STOP",
	"TN_func":     "",
	"TE_state":    "STOP",
	"TE_func":     "",
	"onentry_func": "",
	"onexit_func": ""
}
ESU["LOGOUT"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "bus_login.csv",
	"log_varnames":         "LOG-LINE,LOG-BUS,LOG-LINE-DIR",
	"log_timecol_name":     "LOG-TIME",
	"log_start_time_expr":  "<RES-BUSSTOP-PASS-TIME>,0",
	"log_stop_time_expr":   "<INT-STOP-TIMESTAMP>,0",
	
	"TF_state":    "RTAT",
	"TF_func":     "LOGOUT_found_function",
	"TN_state":    "STOP",
	"TN_func":     "",
	"TE_state":    "STOP",
	"TE_func":     "",
	"onentry_func": "",
	"onexit_func": ""
}
STOP = {
	"func":     "stop"
}

# ----------------------------- FUNCTION PART -----------------------------
def start():
	print("  Transition-function: start_function")
	set_sbk_file("TLG_1",
				 "LOG-BUS","SET-LINE-NUMBER",
				 "RES-BUS-START-TIME","RES-BUSSTOP-PASS-TIME",
				 "RES-TIME-DIFF","RES-TIME-DIFF-SEC",
				 "ERR-TIME")
	
	set_datetime_variable("INT-START-TIMESTAMP","INT-START-DATE","INT-START-TIME")
	set_datetime_variable("INT-STOP-TIMESTAMP","INT-START-DATE","INT-STOP-TIME")

	#copy_variable("RTAT-LINE","SET-LINE-NUMBER")

def RTAT_found_function():
	print("")
	print("  Transition-function: RTAT_found_function")
	#copy_variable("LOG-LINE","RTAT-LINE")
	#copy_variable("LOG-BUS","RTAT-BUS")
	#copy_variable("LOG-LINE-DIR","RTAT-LINE-DIR")
	set_variable("START-BUSSTOP","A1")	
	copy_variable("INT-START-TIMESTAMP","RTAT-TIME")

def LOGIN_found_funtion():
	print("")
	print("  Transition-function: LOGIN_found_funtion")
	#copy_variable("LOCAT-BUS","RTAT-BUS")

def START_found_function():
	print("")
	print("  Transition-function: START_found_function")
	copy_variable("RES-BUS-START-TIME","INT-LOCAT-TIME-OLD")

def PASS_found_function():
	print("")
	print("  Transition-function: PASS_found_function")
	copy_variable("RES-BUSSTOP-PASS-TIME","INT-LOCAT-TIME-OLD")
	#copy_variable("AD-LINE","SET-LINE-NUMBER")
	#copy_variable("AD-BUS","RTAT-BUS")
	#copy_variable("AD-BUS-DIR","RTAT-LINE-DIR")

	calc_time_diff("RES-TIME-DIFF","RES-TIME-DIFF-SEC","RES-BUSSTOP-PASS-TIME","RES-BUS-START-TIME")
	compare_variable("ERR-TIME","RES-TIME-DIFF-SEC",">","SET-MAX-START-PASS-TIME")

def AD_found_function():
	print("")
	print("  Transition-function: AD_found_function")

def LOGOUT_found_function():
	print("")
	print("  Transition-function: LOGOUT_found_function")

	print_sbk_file()

def stop():
	print("stop")
	print_sbk_file()
