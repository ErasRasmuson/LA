# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	logdig_EX1_test.py

AUTHOR:     Esa Heikkinen
DATE:       18.04.2018
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
	"INT-START-DATE":    "09.03.18",
	"INT-START-TIME":    "10:00:00",
	"INT-STOP-TIME":     "10:10:00"
	}
START = {
	"state":   "TEST",
	"func":   "start"
	}
ESU["TEST"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "Log_EX1_gen_track_5.csv",
	"log_varnames":         "DATA=D5-1",
	"log_timecol_name":     "TIME",
	"log_start_time_expr":  "<INT-START-TIMESTAMP>,0",
	"log_stop_time_expr":   "<INT-STOP-TIMESTAMP>,0",

	"TF_state":    "TEST2",
	"TF_func":     "",
	"TN_state":    "STOP",
	"TE_state":    "STOP",
	"GUI_line_num":	"1"
}
ESU["TEST2"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "Log_EX1_gen_track_5.csv",
	"log_varnames":         "DATA=D5-4",
	"log_timecol_name":     "TIME",
	"log_start_time_expr":  "<TIME>,0",
	"log_stop_time_expr":   "<INT-STOP-TIMESTAMP>,0",

	"TF_state":    "STOP",
	"TF_func":     "",
	"TN_state":    "STOP",
	"TE_state":    "STOP",
	"GUI_line_num":	"2"
}
STOP = {
	"func":     "stop"
}

# ----------------------------- FUNCTION PART -----------------------------
def start():

	print("  Transition-function: start_function")
	set_sbk_file("EX1_test","TIME","ID","SOURCES","TARGETS","ATTR","DATA")

	set_datetime_variable("INT-START-TIMESTAMP","INT-START-DATE","INT-START-TIME")
	set_datetime_variable("INT-STOP-TIMESTAMP","INT-START-DATE","INT-STOP-TIME")

def stop():
	print("stop")
	print_sbk_file()
