# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER:     Taxi_LongRides.py

AUTHOR:     Esa Heikkinen
DATE:       26.06.2018
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
	"STARTTIME-DATE":   "2013-01-01",
	"STARTTIME-TIME": 	"00:00:00",
	"STOPTIME-DATE":	"2013-01-01",
	"STOPTIME-TIME": 	"01:40:00"
	}
START = {
	"state":   "BEGIN",
	"func":   "start"
	}
ESU["BEGIN"] = {
	"esu_mode":             "SEARCH_EVENT:First:NextRow",
	"log_filename_expr":    "TaxiRides_small.csv",
	"log_varnames":         "isStart=START",
	"log_timecol_name":     "startTime",
	"log_start_time_expr":  "<STARTTIME-BEGIN>,0",
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
	"log_filename_expr":    "TaxiRides_small.csv",
	"log_varnames":         "isStart=END,rideId=<SET-RIDEID>",
	"log_timecol_name":     "startTime",
	"log_start_time_expr":  "<startTime>,0",
	"log_stop_time_expr":   "<startTime>,7200",

	"TF_state":    "BEGIN",
	"TF_func":     "found_end",
	"TN_state":    "BEGIN",
	"TN_func":     "not_found_end",
	"TE_state":    "STOP",
	"TE_func":     "exit_error",
	"GUI_line_num":	"1"
}
STOP = {
	"func":     ""
}

# ----------------------------- FUNCTION PART -----------------------------
def start():
	set_datetime_variable("STARTTIME","STARTTIME-DATE","STARTTIME-TIME")
	set_datetime_variable("STOPTIME","STOPTIME-DATE","STOPTIME-TIME")
	set_sbk_file("Taxi_LongRides","SET-RIDEID","startTime","endTime")
	copy_variable("STARTTIME-BEGIN","STARTTIME")

def found_begin():
	print("found_begin")
	copy_variable("SET-RIDEID","rideId")
	copy_variable("STARTTIME-BEGIN","startTime")

def found_end():
	print("found_end")

def not_found_end():
	print("not_found_end")
	copy_variable("STARTTIME-BEGIN","startTime")
	print_sbk_file()

def exit_normal():
	print("exit_normal")

def exit_error():
	print("exit_error")
