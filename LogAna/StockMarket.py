# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER:     StockMarket.py

AUTHOR:     Esa Heikkinen
DATE:       06.08.2018
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
	"STARTTIME-DATE":   "2018-08-06",
	"STARTTIME-TIME": 	"10:00:00",
	"STOPTIME-DATE":	"2018-08-06",
	"STOPTIME-TIME": 	"12:00:00"
	}
START = {
	"state":   "A",
	"func":   "start"
	}
ESU["A"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "StockMarket.csv",
	"log_varexprs":         "int(<LAST-VOLUME>) > 1000",
	"log_timecol_name":     "TIME",
	"log_start_time_expr":  "<A-STARTTIME>,0",
	"log_stop_time_expr":   "<STOPTIME>,0",

	"TF_state":    "AplusB",
	"TF_func":     "found_A",
	"TN_state":    "STOP",
	"TN_func":     "not_found_A",
	"TE_state":    "STOP",
	"TE_func":     "exit_error",
	"GUI_line_num":	"0"
}
ESU["AplusB"] = {
	"esu_mode":             "SEARCH_EVENT:First:NextRow",
	"log_filename_expr":    "StockMarket.csv",
	"log_varexprs":         "int(<LAST-PRICE>) > ana.variables[\"AVG-PRICE\"],int(<LAST-VOLUME>) < ana.variables[\"VOLUME-80\"]",
	"log_timecol_name":     "TIME",
	"log_start_time_expr":  "<AplusB-TIME>,0",
	"log_stop_time_expr":   "<A-TIME>,3600",

	"TF_state":    "AplusB",
	"TF_func":     "found_AplusB",
	"TN_state":    "A",
	"TN_func":     "not_found_AplusB",
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
	set_sbk_file("StockMarket","EVENT-PATTERN")
	copy_variable("A-STARTTIME","STARTTIME")

def found_A():
	print("found_A")
	copy_variable("A-TIME","TIME")
	#AVG-PRICE = PRICE
	set_variable("AVG-PRICE",get_variable_int_value("PRICE",10))
	#AplusB-SUM = PRICE
	set_variable("AplusB-SUM",get_variable_int_value("PRICE",10))
	#AplusB-CNT = 1
	set_counter("AplusB-CNT",1)
	#EVENT-PATTERN = ID
	copy_variable("EVENT-PATTERN","ID")

	#VOLUME-80 = 80% VOLUME
	set_variable("VOLUME-80",get_variable_int_value("VOLUME",10) * 0.8)
	set_variable("AplusB-TIME",str(get_time_variable_value("TIME")))

def not_found_A():
	print("not_found_A")
	print_sbk_file()

def found_AplusB():
	print("found_AplusB")
	#copy_variable("AplusB-TIME","TIME")
	set_variable("AplusB-TIME",str(get_time_variable_value("TIME")))
	#AplusB-CNT += 1
	incr_counter("AplusB-CNT")
	#AplusB-SUM += PRICE
	add_value("AplusB-SUM","PRICE")
	#AVG-PRICE = AplusB-SUM / AplusB-CNT
	calc_average("AVG-PRICE","AplusB-SUM","AplusB-CNT")

	#EVENT-PATTERN.ADD = ID
	add_string("EVENT-PATTERN","ID")

	#VOLUME-80 = 80% VOLUME
	set_variable("VOLUME-80",get_variable_int_value("VOLUME",10) * 0.8)

def not_found_AplusB():
	print("not_found_AplusB")

def exit_error():
	print("exit_error")
