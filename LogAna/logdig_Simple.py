# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	logdig_Simple.py    

AUTHOR:     Esa Heikkinen
DATE:       21.06.2016
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
	"CASENAME":    		"CEL",
	"STARTTIME-DATE":   "2016-06-21",
	"STARTTIME-ORIG":   "12:00:00",
	"STOPTIME-ORIG":    "12:20:00",
	"LOGFILENUM":   	"1",
	"EVENT-MAX-LEN": 	"599",
	}
START = {
	"state":   "BEGIN",
	"func":   "start"
	}
ESU["BEGIN"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "Logfile_<LOGFILENUM>.csv",
	"log_varnames":         "EV-PAR",
	"log_timecol_name":     "EV-TIME",
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
	"log_filename_expr":    "Logfile_<LOGFILENUM>.csv",
	"log_varnames":         "EV-ID,EV-PAR",
	"log_timecol_name":     "EV-TIME",
	"log_start_time_expr":  "<EV-START>,0",
	"log_stop_time_expr":   "<STOPTIME>,0",
	
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
	set_sbk_file("BMU_CEL","EV-ID","EV-START","EV-STOP","EV-LEN","EV-STATUS","COUNTER-OK","COUNTER-ERROR")
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
