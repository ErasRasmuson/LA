# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	logdig_analyze_template.py    

AUTHOR:     Esa Heikkinen
DATE:       02.03.2016
DOCUMENT:   - 
VERSION:    "$Id$"
REFERENCES: -
PURPOSE:    
CHANGES:    "$Log$"
###############################################################################
"""
#import datetime
from datetime import datetime
import os.path
import sys
import re
import collections

# 4.7.2018 Esa
from LogFilesData import *
logfiles_data = LogFilesData()


#ESU = {}
ESU = collections.OrderedDict()

# Tilat
states = []

# Aputualukko, jossa tilan järjestysnumero
state_order = {}

# Muuttujien taulukko
variables = {}

# Tilan tyypit
state_type = {}

# Alkutila
start_state_name = "START"

# Syöteaakkosto (tilasiirtymien nimet)
#input_alphabets =
transition_names = ["Found","Not found","Exit"]

# Tilasiirtymät
transition = {}

# Tilasiirtymäfunktiot (vastaa tilasiirtymien tietorakennetta)
transition_function = {}

# Funktiot, jotka suoritetaan tilaan mennessä
state_onentry_function = {}
#state_onentry_function["RTAT"] = "RTAT_onentry"

# Funktiot, jotka suoritetaan tilasta poistuttaessa.
state_onexit_function = {}

# Lopputila
end_state_name = "STOP"

# Tilojen luettavat lokitiedostot
state_logfiles = {}

# Tilojen data-tiedostot
state_datafiles = {}

# Tilojen asetukset. Tarviiko ?
state_settings = {}

# Globaalit asetukset ?
#variables["SET_MAX_LOGIN_RTAT_TIME"] = 1200 

# Tilojen lokitiedoston muuttujat
state_log_variables = {}

# Tilojen lokitiedostojen muuttujien lausekkeet. Esa 2.8.2018
state_log_variables_exprs = {}

# Tilojen datatiedoston muuttujat
state_data_variables = {}

# Tilojen lokin paikkatieto muuttujien (lon ja lat) nimet
state_position_variables = {}

# Tilan lokin aika-sarakkeen nimi
state_log_time_column = {}

# Tilojen tapahtumahaun aikaikkunan aikarajat
state_start_time_limit = {}
state_stop_time_limit  = {}

# Tilojen aikaikkunan maksimi tapahtumalaskuri. Esa 13.8.2018
state_timewindow_event_count_max = {}

# Tilojen GUI:n piirtolinjan järjestysnumero 
state_GUI_line_num = {}

# Tämä kirjoitetaan logdig.py:n komentoriviparametrin kautta !
outputs_file_path = ""

#------------------------------------------------------------------------------

# Utility-functions, that are used in transition functions

# Esa 13.8.2018. This new function can replace almost all old utility-functions ?
def statem(statement):

	# Is it possible to compile only at the first time ? Or checks it is already compiled ?
	# Can be little bit faster ?

	ret,statement_new = convert_meta_variable_names_in_functions(statement)
	code_str = compile(statement_new,"<string>","exec")
	exec(code_str)

def copy_variable(target_var,source_var):

	try:
		print("  Copy variables: %s = %s \"%s\"" % (target_var,source_var,variables[source_var]))
		variables[target_var] = variables[source_var]
	except KeyError:
		print("copy_variable: ERR: Copying variables: %s = %s" % (target_var,source_var))
		
def set_variable(var_name,var_value):

	try:
		print("  Set variable: %s = \"%s\"" % (var_name,var_value))
		variables[var_name] = var_value
	except KeyError:
		print("set_variable: ERR: Setting variable: %s = \"%s\"" % (var_name,var_value))

def set_counter(var_name,int_value):

	try:
		print("  Set counter: %s = \"%d\"" % (var_name,int_value))
		variables[var_name] = int_value
	except KeyError:
		print("set_counter: ERR: variable: %s = \"%s\"" % (var_name,int_value))

def incr_counter(var_name):

	try:
		variables[var_name] += 1
		print("  Incr counter: %s = \"%d\"" % (var_name,variables[var_name]))
	except KeyError:
		print("incr_counter: ERR: variable: %s" % (var_name))

# Esa 6.8.2018
def add_value(var_name,value_var_name):

	try:
		if type(variables[value_var_name]) is not int:
			variables[var_name] += int(variables[value_var_name])
		else:
			variables[var_name] += variables[value_var_name]
		print("  Add value: %s, %s = \"%d\"" % (var_name,value_var_name,variables[var_name]))
	except KeyError:
		print("add_value: ERR: variable: %s or %s" % (var_name,value_var_name))

# Esa 6.8.2018
def add_string(var_name,value_var_name):

	try:
		variables[var_name] += "," + variables[value_var_name]
		print("  Add string: %s, %s = \"%s\"" % (var_name,value_var_name,variables[var_name]))
	except KeyError:
		print("add_vadd_stringalue: ERR: variable: %s or %s" % (var_name,value_var_name))

# Esa 6.8.2018
def calc_average(avg_var_name,sum_var_name,cnt_var_name):

	try:
		variables[avg_var_name] = variables[sum_var_name] / variables[cnt_var_name]

		print("  Calc avrage: %s, %s = \"%d\"" % (sum_var_name,cnt_var_name,variables[avg_var_name]))
	except KeyError:
		print("calc_average: ERR: variable: %s or %s" % (sum_var_name,cnt_var_name))

def get_variable_str_value(var_name):

	try:
		print("  Get variable: \"%s\"" % (var_name))
		var_value = variables[var_name]
		return var_value
	except KeyError:
		print("get_variable_str_value: ERR: Getting variable: \"%s\"" % (var_name))

def get_variable_int_value(var_name,base):

	try:
		print("  Get variable: \"%s\", base = %s" % (var_name,base))
		var_value = int(variables[var_name],base)
		#print("  Get variable: value = %s" % (var_value))
		return var_value
	except KeyError:
		print("get_variable_int_value: ERR: Getting variable: \"%s\", base = %s" % (var_name,base))

def compare_variable(result_var_name,var1_name,comp_oper,var2_name):

	print("  Compare variable: %s %s %s" % (var1_name,comp_oper,var2_name))
	try:
		res = 0
		if comp_oper == ">":
			if int(variables[var1_name]) > int(variables[var2_name]):
				res = 1
		elif comp_oper == "<":
			if int(variables[var1_name]) < int(variables[var2_name]):
				res = 1
		elif comp_oper == "==":
			if variables[var1_name] == variables[var2_name]:
				res = 1
		else:
			print("compare_variable: ERR: Unknown oper: %s" % comp_oper)

		variables[result_var_name] = res
		return res

	except KeyError:
		print("compare_variable: ERR")
		return 2

def set_datetime_variable(timestamp_var_name,date_var_name,time_var_name):

	print("set_datetime_variable: timestamp_var_name: %s, date_var_name: %s, time_var_name: %s" % 
		(timestamp_var_name,date_var_name,time_var_name))

	try:
		# Muutetaan aikaleimat pythonin datetime-muotoon
		timestamp_str = variables[date_var_name] + " " + variables[time_var_name]
		#timestamp_value = datetime.datetime.strptime(timestamp_str,"%Y-%m-%d %H:%M:%S")
		timestamp_value = datetime.strptime(timestamp_str,"%Y-%m-%d %H:%M:%S")
		print("  Variable: %s, timestamp: %s" % (timestamp_var_name,timestamp_value))
		variables[timestamp_var_name] = timestamp_value
	except KeyError:
		print("set_datetime_variable: ERR: Setting time variable: %s" % (timestamp_var_name))

def get_time_variable_value(timestamp_var_name):

	print("get_time_variable_value: timestamp_var_name: %s" % timestamp_var_name)
	#timestamp_value = datetime.datetime.strptime(variables[timestamp_var_name][:19],"%Y-%m-%d %H:%M:%S")
	timestamp_value = datetime.strptime(variables[timestamp_var_name][:19],"%Y-%m-%d %H:%M:%S")
	return timestamp_value

def calc_time_diff(timediff_var_name,timediff_sec_var_name,time1_var_name,time2_var_name):

	print("calc_time_diff: timediff_var_name: %s, time1_var_name: %s, time1_var_name: %s" % 
		(timediff_var_name,time1_var_name,time2_var_name))

	try:
		#time1 = datetime.datetime.strptime(variables[time1_var_name],"%Y-%m-%d %H:%M:%S")
		#time2 = datetime.datetime.strptime(variables[time2_var_name],"%Y-%m-%d %H:%M:%S")
		time1 = datetime.strptime(variables[time1_var_name],"%Y-%m-%d %H:%M:%S")
		time2 = datetime.strptime(variables[time2_var_name],"%Y-%m-%d %H:%M:%S")
		diff = time1 - time2
		diff_sec = diff.seconds
		print("calc_time_diff: %s - %s = %s, %s sec" % (time1,time2,diff,diff_sec))

		variables[timediff_var_name] = diff
		variables[timediff_sec_var_name] = diff_sec
	except KeyError:
		print("calc_time_diff: ERR")

def set_sbk_file(filename,*sbk_variables):

	global sbk_file_name
	global sbk_var_list
	global sbk_id_counter

	print("set_sbk_file")

	sbk_id_counter = 0

	var_str = "SBK_ID"
	sbk_var_list = ["SBK_ID"]
	var_counter = 1
	for var_name in sbk_variables:
		var_counter += 1
		print("SBK: %3d, var=%s" % (var_counter,var_name))
		if var_counter > 1:
			var_str += "," + var_name
		else:
			 var_str += var_name
		sbk_var_list.append(var_name)

	#print("sbk_var_list = %s" % sbk_var_list)

	sbk_file_name = output_files_path + filename + ".sbk"
	make_dir_if_no_exist(sbk_file_name)

	str_header = "%s" % (var_str)
	print("SBK file : %s, header: %s" % (sbk_file_name,str_header))

	f_sbk = open(sbk_file_name, 'w')
	f_sbk.writelines(str_header + "\n")
	f_sbk.close()

def print_sbk_file():

	global sbk_file_name
	global sbk_var_list
	global sbk_id_counter

	#print("print_sbk_file")
	#print("sbk_var_list = %s" % sbk_var_list)

	sbk_id_counter += 1
	variables["SBK_ID"] = sbk_id_counter

	str_data = ""
	var_counter = 0
	for var_name in sbk_var_list:
		var_value = ""
		try:
			var_value = variables[var_name]
		except:
			print("print_sbk_file: ERR: Not found variable: %s" % var_name)

		var_counter += 1
		if var_counter > 1:
			str_data += "," + str(var_value) 
		else:
			str_data += str(var_value)

	#print("str_data = %s" % str_data)

	f_sbk = open(sbk_file_name, 'a')
	f_sbk.writelines(str_data + "\n")
	f_sbk.close()

#def set_rcl_file():

#def print_rcl_data():

#def print_rcl_file():


def make_dir_if_no_exist(file_path_name):

	# Python3
	#os.makedirs(os.path.dirname(file_path_name), exist_ok=True)

	# Python2
	if not os.path.exists(os.path.dirname(file_path_name)):
		try:
			os.makedirs(os.path.dirname(file_path_name))
		#except OSError as exc:
		#	if exc.errno != errno.EEXIST:
		#		raise
		except:
			print("make_dir_if_no_exist: ERROR: file_path_name: %s" % file_path_name)

#******************************************************************************
#
#	FUNCTION:	convert_meta_variable_names_in_functions
#
#******************************************************************************
# Esa 11.8.2018 This is almost same function as in LogDig.py. It is possible to combine ?
def convert_meta_variable_names_in_functions(var_string):

	# Searches all indexes of "<"
	indexes = [i for i, ltr in enumerate(var_string) if ltr == "<"]
	#print("indexes: %s" % indexes)

	# Searches variable names
	var_names_list = []
	for index in indexes:
		# Next char should be letter
		if var_string[index+1].isalpha():
			end_ind = var_string[index+1:].find(">")
			if end_ind == -1:
				print("ERR: Convert meta-variable names: No \">\" char found in %s" % var_string)
				return (False,var_string)
			sub_string = var_string[index+1:index+end_ind+1]
			#print("  sub_string: %s" % sub_string)
			# Sub string (variable name) should not include spaces
			if " " in sub_string:
				print("ERR: Convert meta-variable names: Spaces are not allowed in \"%s\"" % sub_string)
				return (False,var_string)
			else:
				var_names_list.append(sub_string)
		else:
			print("Convert variable meta-names: After \"<\" char should be alpha char in %s" % var_string)
			continue

	# Converts all variable names
	for var_name in var_names_list:

		print("var_name: %s" % var_name)

		#var_internal_name = "ana.variables[\"%s\"]" % var_name
		var_internal_name = "variables[\"%s\"]" % var_name
		#var_internal_name = "last_read_variables[\"%s\"]" % var_name
		var_name_ext = "<"+var_name+">"
		var_string = var_string.replace(var_name_ext,var_internal_name)

	return (True,var_string)