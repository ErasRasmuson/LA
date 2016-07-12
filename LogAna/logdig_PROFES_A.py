# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	logdig_PROFES_A.py    

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
	"INT-STOP-TIME":     "08:00:00",
	"SET-LINE-NUMBER":   "L001",
	"EVENT-MAX-LEN": 	 "1900"
	}
START = {
	"state":   "LOGIN",
	"func":   "start"
	}
ESU["LOGIN"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "bus_login.csv",
	"log_varnames":         "LOG-TYPE=LOGIN",
	"log_timecol_name":     "LOG-TIME",
	"log_start_time_expr":  "<INT-START-TIMESTAMP>,+1",
	"log_stop_time_expr":   "<INT-START-TIMESTAMP>,+2700",
	
	"TF_state":    "LOGOUT",
	"TF_func":     "LOGIN_found_function",
	"TN_state":    "STOP",
	"TE_state":    "STOP",
	"GUI_line_num":	"0"
}
ESU["LOGOUT"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "bus_login.csv",
	"log_varnames":         "LOG-TYPE=LOGOUT,LOG-BUS",
	"log_timecol_name":     "LOG-TIME",
	"log_start_time_expr":  "<LOG-TIME>,+1",
	"log_stop_time_expr":   "<LOG-TIME>,+2700",
	
	"TF_state":    "LOGIN",
	"TF_func":     "LOGOUT_found_function",
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
	
	set_datetime_variable("INT-START-TIMESTAMP","INT-START-DATE","INT-START-TIME")
	set_datetime_variable("INT-STOP-TIMESTAMP","INT-START-DATE","INT-STOP-TIME")
	set_sbk_file("PROFES_A","LOG-BUS","LOGIN","LOGOUT","DIFF","STATUS","CNT_OK","CNT_ERROR")
	set_counter("CNT_OK",0)
	set_counter("CNT_ERROR",0)

def LOGIN_found_function():
	print("")
	print("  Transition-function: LOGIN_found_function")
	copy_variable("LOGIN","LOG-TIME")
	#set_variable("EV-PAR","E")

def LOGOUT_found_function():
	print("")
	print("  Transition-function: LOGOUT_found_function")

	#set_variable("EV-PAR","B")
	copy_variable("LOGOUT","LOG-TIME")
	set_variable("STATUS","OK")
	calc_time_diff("TIME-DIFF","DIFF","LOGOUT","LOGIN")
	if compare_variable("ERR-TIME","DIFF",">","EVENT-MAX-LEN") == 1:
		set_variable("STATUS","ERR")
		incr_counter("CNT_ERROR")
	else:
		incr_counter("CNT_OK")
	copy_variable("INT-START-TIMESTAMP","LOG-TIME")

	print_sbk_file()

def stop():
	print("stop")
	print_sbk_file()