# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	LogPrep.py    

AUTHOR:     Esa Heikkinen
DATE:       24.10.2014
DOCUMENT:   - 
VERSION:    "$Id$"
REFERENCES: -
PURPOSE:    
CHANGES:    "$Log$"
###############################################################################
"""

import argparse
import os.path
import sys
import time
import re
from datetime import datetime, timedelta
from LogPrepColOpers import *
import glob

g_version = "$Id$"


output_lines = []
output_col_lines = {}
divide_col_values = {}
columns_new_list = []

#******************************************************************************
#       
#	CLASS:	LogFile
#
#******************************************************************************
class LogFile:

	global variables
	global date
	
	name = "Unknown"
	#output_lines = []
	columns_list = []
	column_new_list = []
	columns_oper = []
	columns_new_oper = {}
	line_csv = ""
	
	def __init__(self,name):
		self.name=name
		self.output_lines = []
		self.columns_list = []
		self.column_new_list = []
		self.columns_oper = []
		self.columns_new_oper = {}
		self.line_csv = ""
		
	def check_conversions(self):
		
		# Käydään sarakemuutokset läpi
		counter = 0
		
		for col_oper_output in self.columns_new_oper.keys():
			
			counter += 1
			col_oper = self.columns_new_oper[col_oper_output]
			
			# Suoritetaan sarakemuutos riville
			code_str = compile(col_oper,"<string>","eval")
			try:
				variables[col_oper_output] = eval(code_str)
			except:
				print("ERR: Executing: \"%s\"\n" % col_oper)
				sys.exit()
			
			#print("%3d: %-15s = %s = %s" % (counter,col_oper_output,col_oper,variables[col_oper_output]))
		
	def set_columns_conversions(self,columns_list,columns_oper):
	
		self.columns_list = columns_list
		self.columns_oper = columns_oper
		
		self.columns_new_oper = {}
		
		# Käydään sarake-operaattorit läpi
		for column_oper in self.columns_oper:
			print("column_oper: %s" % column_oper)
			
			columns_oper_list = column_oper.split("=")
			columns_oper_list_len = len(columns_oper_list)
			if columns_oper_list_len != 2:
				print("ERR: in column_oper: %s" % column_oper) 
				continue
			
			# Erotetaan output-muuttuja (sarake) sekä sen funktio ja input-muuttujat
			output_var = columns_oper_list[0]
			oper_func_vars = columns_oper_list[1]
			
			output_var = output_var.strip("<>")
			
			# Tukitaan onko uusi sarake ja jos on, lisätään muuttujiin ja sarakelistaan
			if not output_var in self.columns_list:
				print("New column: %s" % output_var)
				variables[output_var]=""
				self.column_new_list.append(output_var)
					
			# Etsitään riviltä sarakkeiden (muuttujien) nimet,
			# jotka "<"- ja ">"-merkkien sisällä
			str_len = len(oper_func_vars)
			start_ptr = 0
			end_ptr = 0
			new_str = oper_func_vars
			while end_ptr < str_len:
			
				start_ptr = new_str.find('<',end_ptr)
				if start_ptr == -1:
					#print("Not found: <")
					break
				start_ptr += 1
				end_ptr = new_str.find('>',start_ptr)
				if end_ptr == -1:
					#print("Not found: >")
					break
					
				col_name = new_str[start_ptr:end_ptr]
				
				print("col_name : %s" % (col_name) )
				#print("str_len = %d, start_ptr=%d, end_ptr=%d" % (str_len,start_ptr,end_ptr))
				
				# Korvataan sarakkeen nimet muuttujanimillä
				col_name_str = "<" + col_name + ">"
				col_name_var_str = "variables[\"" + col_name + "\"]"
				new_str = new_str.replace(col_name_str,col_name_var_str)
				str_len = len(new_str)
				
			self.columns_new_oper[output_var] = new_str
			
			print("new_str = %s" % new_str)
	
	def read_column_names(self,logfile_name,output_sep_char):

		#print("LogFile: read_column_names: %s" % logfile_name)

		cols_list = []

		# Luetaan 1. rivi lokitiedostosta
		if os.path.isfile(logfile_name):
		
			f = open(logfile_name, 'r')
			line = f.readline()
			# Rivinvaihto ja muut tyhjät merkit rivin lopusta pois
			line = line.rstrip()
			f.close()

			if len(line) > 2:
				cols_list = line.split(output_sep_char)

		#print("read_column_names: cols_list: %s" % cols_list)
		return cols_list

	def read(self,logfile_name,regexps,output_sep_char,input_read_mode,output_files_divide_col):

		print("")
		
		vars_list_len = len(self.columns_list)
		
		print("LogFile: read logfile_name: %s" % logfile_name)

		# Luetaan lokitiedosto
		if os.path.isfile(logfile_name):
		
			f = open(logfile_name, 'r')
			lines = f.readlines()
			f.close()
			
			line_counter = 0
			line_sel_counter = 0
			error_counter = 0
			
			# Kaydaan lapi loki-tiedoston rivit
			for line in lines:
			
				# Hylätään tyhjät rivit
				if len(line) < 2:
					continue
			
				# Rivinvaihto ja muut tyhjät merkit rivin lopusta pois
				line = line.rstrip()

				line_counter += 1
				
				#print("LogFile: line: %5d: %s" % (line_counter,line))
				
				# Jos regexp annettu (riviltä pitää parsia arvot)
				if len(regexps) > 0:

					# Parseroidaan tiedoston rivi ja sijoitetaan arvot välimuuttujiin
					p = re.compile(regexps)
					m = p.match(line)
					#print("m: %s" % (m))
					if m != None:
						line_sel_counter += 1
						#print("")
						for cnt in range(vars_list_len):
							var_name = self.columns_list[cnt]
							var_value = m.group(cnt+1)
							variables[var_name]=var_value
							#print("%5d: Var name: %-20s value: %s" % (cnt,var_name,var_value))
						
						self.generate_new_line(variables,output_sep_char,output_files_divide_col)

				# Muuten, arvot ovat valmiina csv-tyyppisellä rivillä
				else:

					# Ei käsitellä otsikko riviä
					if line_counter == 1:
						continue

					columns_value_list = line.split(output_sep_char)
					vars_value_list_len = len(columns_value_list) 
					if vars_value_list_len != vars_list_len:
						 print("ERR: Number of columns: %s and %s are different in line: %s" % 
						 	(vars_value_list_len,vars_list_len,line,output_files_divide_col))
						 sys.exit()

					line_sel_counter += 1
					for cnt in range(vars_list_len):
						var_name = self.columns_list[cnt]
						var_value = columns_value_list[cnt]
						variables[var_name]=var_value
						#print("%5d: Var name: %-20s value: %s" % (cnt,var_name,var_value))

					self.generate_new_line(variables,output_sep_char,output_files_divide_col)

			print("LogFile: Msg-type         = %s" % self.name)
			print("LogFile: line_counter     = %d" % line_counter)
			print("LogFile: line_sel_counter = %d" % line_sel_counter)
			
		else:
			print("LogFile: ERR: Not found logfile: %s" % logfile_name)
	
	def get(self):
		print("")
		return self.output_lines
		
	def get_columns(self):
		print("")
		
		#print("self.columns_list = %s" % self.columns_list)
		#print("self.column_new_list = %s" % self.column_new_list)
		
		return self.columns_list + self.column_new_list
	
	def generate_new_line(self,variables,output_sep_char,output_files_divide_col):

		# Tehdään mahdolliset sarakkeiden konversiot
		self.check_conversions()
		
		# Käydään rivin sarakkeet läpi
		column_list_all = self.columns_list + self.column_new_list
		self.line_csv = ""
		for	col_name in column_list_all:
			
			col_val = variables[col_name]
			
			# Lisätään arvo tulostiedoston (csv) rivin loppuun
			self.line_csv = self.line_csv + output_sep_char + col_val

		if output_files_divide_col == None:
			# Laitetaan tulostiedoston rivi talteen
			self.output_lines.append(self.line_csv)
		else:

			col_value = variables[output_files_divide_col]

			try:
				divide_col_values[col_value] += 1
			except:
				divide_col_values[col_value] = 1

			# Laitetaan annetun sarakkeen arvon mukaiseen tulostiedoston rivi talteen

			try:
				output_col_lines[col_value].append(self.line_csv)
			except:
				output_col_lines[col_value] = [self.line_csv]


#******************************************************************************
#       
#	FUNCTION:	make_dir_if_no_exist
#
#******************************************************************************	
def make_dir_if_no_exist(file_path_name):
	# Python3
	#os.makedirs(os.path.dirname(file_path_name), exist_ok=True)

	# Python2
	if not os.path.exists(os.path.dirname(file_path_name)):
		try:
			os.makedirs(os.path.dirname(file_path_name))
		except OSError as exc:
			if exc.errno != errno.EEXIST:
				raise

#******************************************************************************
#       
#	FUNCTION:	write_output_file
#
#******************************************************************************	
#def write_output_file(logfile_new_name,output_lines,column_name_prefix,output_sep_char,output_files_divide_col):
def write_output_file(output_path,logfile_new_name,column_name_prefix,output_sep_char,output_files_divide_col,combined_file_name,msg_type):

	global output_lines
	global output_col_lines
	global divide_col_values

	if output_files_divide_col == None:

		line_cnt = 0
		make_dir_if_no_exist(logfile_new_name)
		f = open(logfile_new_name, 'w')

		# Otsikko
		f.writelines("%sCounter" % column_name_prefix)
		for col_name in columns_new_list:
		
			# Lisätään prefix sarakkeiden nimien alkuun
			column_name_with_prefix = column_name_prefix + col_name 
		
			#f.writelines("\t" + col_name)
			f.writelines(output_sep_char + column_name_with_prefix)
			
		f.writelines("\n")
	
		# Rivit
		for output_line in output_lines:
			line_cnt += 1
			str = "%d %s\n" % (line_cnt,output_line)
			#print("%s" % str)
			f.writelines(str)
	else:
		
		file_cnt = 0
		col_value_list = divide_col_values.keys()
		for col_value in col_value_list:
			line_cnt = 0
			file_cnt += 1
			logfile_new_name = output_path + combined_file_name + "_" + col_value + "_" + msg_type + ".csv"
			print("writes: %5d: logfile = %s" % (file_cnt,logfile_new_name))

			make_dir_if_no_exist(logfile_new_name)
			f = open(logfile_new_name, 'w')

			# Otsikko
			f.writelines("%sCounter" % column_name_prefix)
			for col_name in columns_new_list:
			
				# Lisätään prefix sarakkeiden nimien alkuun
				column_name_with_prefix = column_name_prefix + col_name 
			
				#f.writelines("\t" + col_name)
				f.writelines(output_sep_char + column_name_with_prefix)
				
			f.writelines("\n")

			# Rivit
			for output_line in output_col_lines[col_value]:
				line_cnt += 1
				str = "%d %s\n" % (line_cnt,output_line)
				#print("%s" % str)
				f.writelines(str)

	f.close()

#******************************************************************************
#       
#	FUNCTION:	main
#
#******************************************************************************

print("version: %s" % g_version)

start_time = time.time()

parser = argparse.ArgumentParser()
parser.add_argument('-input_path','--input_path', dest='input_path', help='input_path')
parser.add_argument('-input_files','--input_files', dest='input_files', help='input_files')
parser.add_argument('-input_read_mode','--input_read_mode', dest='input_read_mode', help='input_read_mode')
parser.add_argument('-combined_file_name','--combined_file_name', dest='combined_file_name', help='combined_file_name')
parser.add_argument('-output_path','--output_path', dest='output_path', help='output_path')
parser.add_argument('-output_files_divide_col','--output_files_divide_col', dest='output_files_divide_col', help='output_files_divide_col')
parser.add_argument('-output_sep_char','--output_sep_char', dest='output_sep_char', help='output_sep_char')
parser.add_argument('-date','--date', dest='date', help='date')
parser.add_argument('-msg_type','--msg_type', dest='msg_type', help='msg_type')
parser.add_argument('-column_name_prefix','--column_name_prefix', dest='column_name_prefix', help='column_name_prefix')
parser.add_argument('-columns','--columns', dest='columns', help='columns')
parser.add_argument('-regexps','--regexps', dest='regexps', help='regexps')
parser.add_argument('-column_oper','--column_oper', action='append', dest='column_oper', default=[], help='column_oper')

args = parser.parse_args()

print("input_path              : %s" % args.input_path)
print("input_files             : %s" % args.input_files)
print("input_read_mode         : %s" % args.input_read_mode)
print("combined_file_name      : %s" % args.combined_file_name)
print("output_path             : %s" % args.output_path)
print("output_files_divide_col : %s" % args.output_files_divide_col)
print("output_sep_char         : \"%s\"" % args.output_sep_char)
print("date                    : %s" % args.date)
print("msg_type                : %s" % args.msg_type)
print("column_name_prefix      : %s" % args.column_name_prefix)
print("columns                 : %s" % args.columns)
print("regexps                 : %s" % args.regexps)
print("column_oper             : %s" % args.column_oper)

print(".....")

# Muodostetaan input-tiedostojen lista polkuineen
logfile_name_list = []
input_files_list = args.input_files.split(",")
#print("input_files_list=%s" % input_files_list)
for input_file in input_files_list:
	#print("input_file=%s" % input_file)
	input_file_path_name_list = glob.glob(args.input_path + input_file)
	#print("input_file_path_name_list=%s" % input_file_path_name_list)
	for input_file_path_name in input_file_path_name_list:
		print("input_file_path_name = %s" % input_file_path_name)
		logfile_name_list.append(input_file_path_name) 

print(".....")

#print("logfile_name_list = %s" % logfile_name_list)
print("\n")

date = args.date

# Käydään läpi input-tiedosto(t)
for logfile_name in logfile_name_list:

	variables = {}

	msg_type = args.msg_type
	#print("msg_type = \"%s\"" % msg_type)
	
	print("logfile_name = \"%s\"" % logfile_name)
	
	# Output-file path and name
	head, tail = os.path.split(logfile_name)
	#print("head=%s, tail=%s" % (head,tail))
	file_name, file_ext =tail.split(".")
	
	logfile_new_name = args.output_path + file_name + "_" + msg_type + ".csv"

	print("logfile_new_name = \"%s\"" % logfile_new_name)
	
	#state_search_string = state_search_strings[msg_type]
	regexps = args.regexps
	
	#columns_list = state_search_string_variables[msg_type]

	log_file = LogFile(msg_type)

	# Jos sarakenimet on annettu komentoriviltä
	if len(args.columns) > 0:
		columns_list = args.columns.split(",")

	# Muuten haetaan sarakenimet tiedoston ekalta riviltä 
	else:
		# Haetaan tiedoston ekalta riviltä sarakenimet
		columns_list = log_file.read_column_names(logfile_name,args.output_sep_char)

	if len(columns_list) == 0:
		print("ERR: Not found column names from parameter or file")
		sys.exit()

	#print("regexps = \"%s\"" % regexps)
	#print("columns_list = \"%s\"" % columns_list)
	
	log_file.set_columns_conversions(columns_list,args.column_oper)

	#log_file.read(logfile_name,regexps,columns_list)
	log_file.read(logfile_name,regexps,args.output_sep_char,args.input_read_mode,args.output_files_divide_col)
	
	# Haetaan uusi sarakelista (jos tullut uusia tai jotain poistettu)
	columns_new_list = log_file.get_columns()
	
	#print("columns_new_list = %s" % columns_new_list)
	
	if args.input_read_mode == None:

		# Luetaan lokien tiedot, ei tarvita enää ?
		output_lines = log_file.get()

		# Kirjoitetaan tiedostoon		
		write_output_file(args.output_path,logfile_new_name,args.column_name_prefix,
			args.output_sep_char,args.output_files_divide_col,args.combined_file_name,args.msg_type)

	elif args.input_read_mode == "COMBINE":
		print("COMBINE")
		output_lines += log_file.get()

	else:
		print("ERR: Unknown read mode: %s" % args.input_read_mode)
		sys.exit()

if args.input_read_mode == "COMBINE":

	logfile_new_name = args.output_path + args.combined_file_name + "_" + args.msg_type + ".csv"

	# Kirjoitetaan tiedostoon
	write_output_file(args.output_path,logfile_new_name,args.column_name_prefix,
		args.output_sep_char,args.output_files_divide_col,args.combined_file_name,args.msg_type)

print(" Total execution time: %.3f seconds\n" % (time.time() - start_time))
