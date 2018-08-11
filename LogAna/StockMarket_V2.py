# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER:     StockMarket_V2.py

AUTHOR:     Esa Heikkinen
DATE:       11.08.2018
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
	"esu_mode":             "SEARCH_EVENT:First:NextRow",
	"log_filename_expr":    "StockMarket.csv",
	"log_varexprs":         "int(<LAST-VOLUME>) > 1000",
	"log_timecol_name":     "TIME",
	"log_start_time_expr":  "<A-STARTTIME>,1",
	"log_stop_time_expr":   "<STOPTIME>,0",

	"TF_state":    "Aplus",
	"TF_func":     "E:<Aplus-STARTTIME> = <TIME>; \
					<AVG-PRICE> = int(<PRICE>); \
					<Aplus-SUM> = int(<PRICE>); \
					<Aplus-CNT> = int(1); \
					<EVENT-PATTERN> = <ID>",
	"TN_state":    "STOP",
	"TN_func":     "not_found_A",
	"TE_state":    "STOP",
	"TE_func":     "exit_error",
	"GUI_line_num":	"0"
}
ESU["Aplus"] = {
	"esu_mode":             "SEARCH_EVENT:First:NextRow",
	"log_filename_expr":    "StockMarket.csv",
	"log_varexprs":         "int(<LAST-PRICE>) > <AVG-PRICE>",
	"log_timecol_name":     "TIME",
	"log_start_time_expr":  "<Aplus-STARTTIME>,1",
	"log_stop_time_expr":   "<Aplus-STARTTIME>,3600",

	"TF_state":    "B",
	"TF_func":     "found_Aplus",
	"TN_state":    "A",
	"TN_func":     "E:print(\"not_found_Aplus\")",
	"TE_state":    "STOP",
	"TE_func":     "exit_error",
	"GUI_line_num":	"1"
}
ESU["B"] = {
	"esu_mode":             "SEARCH_EVENT:First:NextRow",
	"log_filename_expr":    "StockMarket.csv",
	"log_varexprs":         "float(<LAST-VOLUME>) < float(<VOLUME>)*0.8",
	"log_timecol_name":     "TIME",
	"log_start_time_expr":  "<Aplus-FOUND-TIME>,0",
	"log_stop_time_expr":   "<Aplus-FOUND-TIME>,11",

	"TF_state":    "A",
	"TF_func":     "found_B",
	"TN_state":    "Aplus",
	"TN_func":     "not_found_B",
	"TE_state":    "STOP",
	"TE_func":     "exit_error",
	"GUI_line_num":	"2"
}
STOP = {
	"func":     ""
}

# ----------------------------- FUNCTION PART -----------------------------
def start():
	set_datetime_variable("STARTTIME","STARTTIME-DATE","STARTTIME-TIME")
	set_datetime_variable("STOPTIME","STOPTIME-DATE","STOPTIME-TIME")
	set_sbk_file("StockMarket","EVENT-PATTERN")
	#copy_variable("A-STARTTIME","STARTTIME")
	expr("<A-STARTTIME> = <STARTTIME>")

#def found_A():
#	print("found_A")
	#copy_variable("Aplus-STARTTIME","TIME")
	#set_variable("AVG-PRICE",get_variable_int_value("PRICE",10))
	#set_variable("Aplus-SUM",get_variable_int_value("PRICE",10))
	#set_counter("Aplus-CNT",1)
	#copy_variable("EVENT-PATTERN","ID")

def not_found_A():
	print("not_found_A")
	print_sbk_file()

def found_Aplus():
	print("found_Aplus")
	#add_string("EVENT-PATTERN","ID")
	expr("<EVENT-PATTERN> += \",\" + <ID>")

def found_B():
	print("found_B")
	#add_string("EVENT-PATTERN","ID")
	expr("<EVENT-PATTERN> += \",\" + <ID>")
	#copy_variable("A-STARTTIME","A-FOUND-TIME")
	expr("<A-STARTTIME> = <A-FOUND-TIME>")

	print_sbk_file()

def not_found_B():
	print("not_found_B")
	#copy_variable("Aplus-STARTTIME","Aplus-FOUND-TIME")
	expr("<Aplus-STARTTIME> = <Aplus-FOUND-TIME>")
	#incr_counter("Aplus-CNT")
	expr("<Aplus-CNT> += 1")
	#add_value("Aplus-SUM","PRICE")
	expr("<Aplus-SUM> += int(<PRICE>)")
	#calc_average("AVG-PRICE","Aplus-SUM","Aplus-CNT")
	expr("<AVG-PRICE> = <Aplus-SUM> / <Aplus-CNT>")

def exit_error():
	print("exit_error")
