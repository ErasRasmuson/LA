# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER:     Taxi_LongRides.py

AUTHOR:     Esa Heikkinen
DATE:       25.06.2018
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
	"CASENAME":    		"CEL"
	}
START = {
	"state":   "START",
	"func":   "start"
	}
ESU["START"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "TaxiRide_<RIDEID>.txt",
	"log_varnames":         "isStart==START",
	"log_timecol_name":     "startTime",
	"log_start_time_expr":  "<STARTTIME>,+1",
	"log_stop_time_expr":   "<STOPTIME>,0",

	"TF_state":    "END",
	"TF_func":     "found_begin",
	"TN_state":    "STOP",
	"TN_func":     "exit_normal",
	"TE_state":    "STOP",
	"TE_func":     "exit_error",
	"GUI_line_num":	"0"
}
ESU["END"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "TaxiRide_<RIDEID>.csv",
	"log_varnames":         "isStart==END",
	"log_timecol_name":     "endTime",
	"log_start_time_expr":  "<startTime>,0",
	"log_stop_time_expr":   "<startTime>,7200",

	"TF_state":    "BEGIN",
	"TF_func":     "found_end",
	"TN_state":    "STOP",
	"TN_func":     "exit_normal",
	"TE_state":    "STOP",
	"TE_func":     "exit_error",
	"GUI_line_num":	"1"
}
STOP = {
	"func":     ""
}

# ----------------------------- FUNCTION PART -----------------------------
def start():
	set_variable("EV-PAR","B")
	set_datetime_variable("STARTTIME","STARTTIME-DATE","STARTTIME-ORIG")
	set_datetime_variable("STOPTIME","STARTTIME-DATE","STOPTIME-ORIG")
	set_sbk_file("COUNTER-OK","COUNTER-ERROR")
	set_counter("COUNTER-OK",0)
	set_counter("COUNTER-ERROR",0)

def found_begin():
	copy_variable("EV-START","EV-TIME")
	set_variable("EV-PAR","E")

def found_end():
	set_variable("EV-PAR","B")
	copy_variable("EV-STOP","EV-TIME")
	set_variable("EV-STATUS","OK")
	calc_time_diff("TIME-DIFF","EV-LEN","EV-STOP","EV-START")
	if compare_variable("ERR-TIME","EV-LEN",">","EVENT-MAX-LEN") == 1:
		set_variable("EV-STATUS","ERR")
		incr_counter("COUNTER-ERROR")
	else:
		incr_counter("COUNTER-OK")
	copy_variable("STARTTIME","EV-START")
	print_sbk_file()

def exit_normal():
	print("exit_normal")

def exit_error():
	print("exit_error")
