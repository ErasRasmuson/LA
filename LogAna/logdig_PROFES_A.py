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
	"SET-LINE-NUMBER":   "L001"
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
	"log_stop_time_expr":   "<INT-STOP-TIMESTAMP>,0",
	
	"TF_state":    "LOGOUT",
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
	"log_stop_time_expr":   "<LOG-TIME>,+2000",
	
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
	set_sbk_file("IECON_A","LOG-BUS","SET-LINE-NUMBER")
	
	set_datetime_variable("INT-START-TIMESTAMP","INT-START-DATE","INT-START-TIME")
	set_datetime_variable("INT-STOP-TIMESTAMP","INT-START-DATE","INT-STOP-TIME")

def LOGOUT_found_function():
	print("")
	print("  Transition-function: LOGOUT_found_function")
	print_sbk_file()

def stop():
	print("stop")
	print_sbk_file()