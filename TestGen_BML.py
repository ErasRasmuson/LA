# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	TestGen_BML.py    

AUTHOR:     Esa Heikkinen
DATE:       12.11.2016
DOCUMENT:   - 
VERSION:    "$Id$"
REFERENCES: -
PURPOSE:    
CHANGES:    "$Log$"
###############################################################################
"""

# KESKEN !!!

#def init_analy_file():

def generate_BML_test_case_event(event_count,event_data,time_start,time_ev_min,time_ev_max):
	print("generate_BML_test_case_event: event count: %s, data: %s" % (event_count,event_data))

	#fw = open(bml_file, 'a')

	#generate_BML_ESU(fw,)

	#fw.close()

def generate_BML_VARIABLES(key_value_variable_list):

	fw.write("VARIABLES = {")
	for key_value in key_value_variable_list:
		var_name = key_value[0]
		var_value = key_value[1]
		fw.write("	\"%s\":    		\"%s\"," % (var_name,var_value))
	fw.write("}")

def generate_BML_start_section(state,func):
	fw.write("START = {")
	fw.write("	\"state\":   				\"%s\"," % state)
	fw.write("	\"func\":   				\"%s\"" % func)
	fw.write("}")

def generate_BML_ESU(fw,name,esu_mode,log_filename_expr,log_varnames,log_timecol_name,
	log_start_time_expr,log_stop_time_expr,ssd_lat_col_name,ssd_lon_col_name,ssd_filename_expr,ssd_varnames,
	TF_state,TF_func,TN_state,TN_func,TE_state,TE_func,GUI_line_num):

	fw.write("ESU[\"%s\"] = {\n" % name)
	fw.write("	\"esu_mode\":            	\"%s\"," % esu_mode)
	fw.write("	\"log_filename_expr\":   	\"%s\"," % log_filename_expr)
	fw.write("	\"log_varnames\":        	\"%s\"," % log_varnames)
	fw.write("	\"log_timecol_name\":    	\"%s\"," % log_timecol_name)
	fw.write("	\"log_start_time_expr\": 	\"%s\"," % log_start_time_expr)
	fw.write("	\"log_stop_time_expr\":  	\"%s\"," % log_stop_time_expr)

	fw.write("	\"ssd_lat_col_name\":    	\"%s\"," % ssd_lat_col_name)
	fw.write("	\"ssd_lon_col_name\":    	\"%s\"," % ssd_lon_col_name)
	fw.write("	\"ssd_filename_expr\":   	\"%s\"," % ssd_filename_expr)
	fw.write("	\"ssd_varnames\":        	\"%s\"," % ssd_varnames)

	fw.write("	\"TF_state\":				\"%s\"," % TF_state)
	fw.write("	\"TF_func\":     			\"%s\"," % TF_func)
	fw.write("	\"TN_state\":    			\"%s\"," % TN_state)
	fw.write("	\"TN_func\":     			\"%s\"," % TN_func)
	fw.write("	\"TE_state\":    			\"%s\"," % TE_state)
	fw.write("	\"TE_func\":     			\"%s\"," % TE_func)
	fw.write("	\"GUI_line_num\":			\"%s\"" % GUI_line_num)
	fw.write("}")

def generate_BML_stop_section(func):
	fw.write("STOP = {")
	fw.write("	\"func\":   				\"%s\"" % func)
	fw.write("}")

def generate_BML_function(name,body):
	fw.write("def %s():" % name)
	fw.write("	%s" % body)
