# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	LogDig.py    

AUTHOR:     Esa Heikkinen
DATE:       26.02.2016
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
from datetime import datetime
import configparser

lib_path = os.path.abspath(os.path.join('..', 'LogCom'))
sys.path.append(lib_path)
from LogGUI import *

g_version = "$Id$"

#******************************************************************************
#       
#	CLASS:	ESU
#
#******************************************************************************
class ESU:

	#global variables
	global legal_state_types
	
	name = "Unknown"
	mode = ""
	start_time = ""
	stop_time = ""
	log_file_name = ""
	data_file_name = ""
	settings = []
	in_variables = []
	out_variables = []
	script_name = ""
	log_column_names_list = []
	last_found_variables = {}
	last_found_new_variables = {}
	last_found_old_variables = {}
	state_log_time_column = ""
	state_log_variables_list = []
	state_data_variables_list = []
	state_position_variables_list = []
	position_counter = 0
	position_area_left_down_lon = 0
	position_area_left_down_lat = 0
	position_area_right_up_lon = 0
	position_area_right_up_lat = 0
	log_variables = {}
	data_variables = {}
	position_variables = {}
	log_column_numbers = 0
	position_lon_variable_name = ""
	position_lat_variable_name = ""

	def __init__(self,name,gui_enable,gui,state_GUI_line_num):

		self.name=name
		self.gui_enable = gui_enable
		self.gui = gui

		self.state_GUI_line_num = state_GUI_line_num
		print("ESU: state_GUI_line_num = %s" % self.state_GUI_line_num)

	#def onentry(self,):
		# Tarviiko ?
		
	def draw_event(self,state_name,timestamp,text):

		try:
			new_event_num = self.state_GUI_line_num[state_name]
			#print("      ESU: GUI-line number: %s" % new_event_num)
			self.gui.drawEvent(self.gui.qp,new_event_num,timestamp,text,"circle")
		except:
			print("ESU: ERR: Not found state: \"%s\" for GUI-line" % (state_name))

	def onexit(self,ret_value):
		
		if ret_value == 0:
			#sys.exit()
			print("ESU: %s: Return: Not found" % self.name)
			return "Not found"
		elif ret_value == 1:
		
			print("ESU: Found variables in state: %s: time: %s:" % (self.name,self.line_found_timestamp))
			
			# Talteen myös muuttujiin
			ana.variables["INT-FOUND-TIMESTAMP"] = self.line_found_timestamp

			# Piirretään löydetty tapahtuma GUI:hin
			if self.gui_enable == 1:
				self.draw_event(self.name,self.line_found_timestamp,str(self.line_found_timestamp))

			# Kopioidaan löydetyn rivin muuttujat globaaleihin muuttujiin
			cnt = 0
			for column_name in self.log_column_names_list:
				cnt += 1
				ana.variables[column_name] = self.last_found_variables[column_name]
				print(" %5d: %-20s: %s" % (cnt,column_name,ana.variables[column_name]))
		
			#sys.exit()
			print("ESU: %s: Return: Found" % self.name)
			return "Found"
		else:
			#sys.exit()
			print("ESU: %s: Return: Exit" % self.name)
			return "Exit"
			
	def get_variable_value(self,var_string,var_list):
	
		# Haetaan muuttujista merkkijonossa käytetyä muuttujaa
		#for var_name in self.state_log_variables_list:
		#print("get_variable_value: var_list = %s" % var_list)
		for var_name in var_list:
			var_name_ext = "<" + var_name + ">"
			
			# Jos löytyi, korvataan muuttujan nimi sen arvolla
			if var_name_ext in var_string:
			
				try:
					var_value = ana.variables[var_name]
				except KeyError:
					print("ESU: ERR: Not found variable: %s in state: %s (get_variable_value)" % (var_name,self.name))
					return (False,var_string)
				
				var_string = var_string.replace(var_name_ext,var_value)
		
		return (True,var_string)
		
	def check_position_in_area(self,lon,lat):
	
		lon = float(lon)
		lat = float(lat)
		
		# Tarkistetaan onko koordinaatti suorakaiteen muotoisen alueen sisällä
		if lon < float(self.position_area_right_up_lon):
			if lon > float(self.position_area_left_down_lon):
				if lat < float(self.position_area_right_up_lat):
					if lat > float(self.position_area_left_down_lat):
						return True
		return False
		
	def check_position_event(self,state_type_param):
		
		#print("check_position_event: %s" % state_type_param)
		
		self.position_counter += 1
		
		if self.position_counter > 1:
		
			#print("position_counter = %d" % self.position_counter)
			
			for column_name in self.log_column_names_list:
				self.last_found_old_variables[column_name] = self.last_found_new_variables[column_name]

			for column_name in self.log_column_names_list:
				self.last_found_new_variables[column_name] = self.last_found_variables[column_name]

			try:
				ana.variables["INT-LATITUDE-OLD"] = self.last_found_old_variables[self.position_lat_variable_name]
				ana.variables["INT-LONGITUDE-OLD"] = self.last_found_old_variables[self.position_lon_variable_name]
			except:
				print("ESU: ERR: Not found longitude or latitude names from columns")
				sys.exit()
			
			try:
				ana.variables["INT-LOCAT-TIME-OLD"] = self.last_found_old_variables[self.state_log_time_column]
			except:
				print("ESU: ERR: Not found time column")
				sys.exit()
			
			ana.variables["INT-LATITUDE-NEW"] = self.last_found_new_variables[self.position_lat_variable_name]
			ana.variables["INT-LONGITUDE-NEW"] = self.last_found_new_variables[self.position_lon_variable_name]
			
			ana.variables["INT-LOCAT-TIME-NEW"] = self.last_found_new_variables[self.state_log_time_column]
						
			pos_old_in_area = self.check_position_in_area(ana.variables["INT-LONGITUDE-OLD"],ana.variables["INT-LATITUDE-OLD"])
			pos_new_in_area = self.check_position_in_area(ana.variables["INT-LONGITUDE-NEW"],ana.variables["INT-LATITUDE-NEW"])
				
			if state_type_param == "Leaving":
				#print("check_position_event: Leaving")
				
				# Tarkistetaan position-datasta ollaanko lähdetty alueelta
				if pos_old_in_area == True and pos_new_in_area == False:
					#self.line_found_timestamp = ana.variables["INT-LOCAT-TIME-NEW"]
					self.line_found_timestamp  = datetime.strptime(ana.variables["INT-LOCAT-TIME-NEW"],"%Y-%m-%d %H:%M:%S")
					print("Leaving ok: time: %s" % ana.variables["INT-LOCAT-TIME-NEW"])
					print("POS OLD: %s, %s, %s" % (ana.variables["INT-LATITUDE-OLD"],ana.variables["INT-LONGITUDE-OLD"],ana.variables["INT-LOCAT-TIME-OLD"]))
					print("POS NEW: %s, %s, %s" % (ana.variables["INT-LATITUDE-NEW"],ana.variables["INT-LONGITUDE-NEW"],ana.variables["INT-LOCAT-TIME-NEW"]))
					return True
					
			elif state_type_param == "Entering":
				#print("check_position_event: Entering")
				
				# Tarkistetaan position-datasta ollaan tultu alueelle
				if pos_old_in_area == False and pos_new_in_area == True:
					#self.line_found_timestamp = ana.variables["INT-LOCAT-TIME-OLD"]
					self.line_found_timestamp  = datetime.strptime(ana.variables["INT-LOCAT-TIME-OLD"],"%Y-%m-%d %H:%M:%S")
					print("Entering ok: time: %s" % ana.variables["INT-LOCAT-TIME-OLD"])
					print("POS OLD: %s, %s, %s" % (ana.variables["INT-LATITUDE-OLD"],ana.variables["INT-LONGITUDE-OLD"],ana.variables["INT-LOCAT-TIME-OLD"]))
					print("POS NEW: %s, %s, %s" % (ana.variables["INT-LATITUDE-NEW"],ana.variables["INT-LONGITUDE-NEW"],ana.variables["INT-LOCAT-TIME-NEW"]))
					return True
					
			else:
				print("check_position_event: Unknown")
				return False
		else:
			for column_name in self.log_column_names_list:
				self.last_found_new_variables[column_name] = self.last_found_variables[column_name]
		return False
		
	def read_input_variables(self,state_log_variables,state_data_variables,state_position_variables):
	
		self.log_variables = {}
		self.data_variables = {}
		
		# Nykyiset globaalien loki-muuttujien arvot talteen
		# Vai pitäisikö arvokin tulla suoraan funktioparametrilla (vanha ?)

		var_oper_list = state_log_variables.split(",")
		self.state_log_variables_list = []
		print("ESU: log variables: %s" % var_oper_list)
		cnt = 0
		for var_oper in var_oper_list:
			cnt += 1

			# Tehdään mahdolliset muuttujan operaatiot, kuten sijoitus toisesta muuttujasta
			var_oper_mode,var_name1,var_value1,var_name2 = self.do_variable_operations(cnt,var_oper)

			try:

				var_value = var_value1
				if var_oper_mode == 0:
					print("ESU: ERR: Unknown variable mode: %s in state: %s" % (var_oper_mode,self.name))
					return False
				elif var_oper_mode == 1:
					var_value = ana.variables[var_name1]
				elif var_oper_mode == 4:
					var_value = ana.variables[var_name2]

				self.log_variables[var_name1] = var_value
				#print(" %5d: \"%s\": \"%s\"" % (cnt,var_name1,self.log_variables[var_name1]))
				self.state_log_variables_list.append(var_name1)

			except KeyError:
				print("ESU: ERR: Not found log-variable: %s in state: %s" % (var_oper,self.name))
				return False
				
		# Nykyiset globaalien data-muuttujien arvot talteen
		var_oper_list = state_data_variables.split(",")
		self.state_data_variables_list = []
		print("ESU: data variables: %s"  % var_oper_list)
		cnt = 0
		for var_oper in var_oper_list:

			if len(var_oper) > 1:
				cnt += 1

				# Tehdään mahdolliset muuttujan operaatiot, kuten sijoitus toisesta muuttujasta
				var_oper_mode,var_name1,var_value1,var_name2 = self.do_variable_operations(cnt,var_oper)

				try:

					var_value = var_value1
					if var_oper_mode == 0:
						print("ESU: ERR: Unknown variable mode: %s in state: %s" % (var_oper_mode,self.name))
						return False
					elif var_oper_mode == 1:
						var_value = ana.variables[var_name1]
					elif var_oper_mode == 4:
						var_value = ana.variables[var_name2]

					self.data_variables[var_name1] = var_value
					#print(" %5d: %-20s: \"%s\"" % (cnt,var_name1,self.data_variables[var_name1]))
					self.state_data_variables_list.append(var_name1)

				except KeyError:
					print("ESU: ERR: Not found data-variable: %s in state: %s" % (var_oper,self.name))
					return False
					
		# Paikkatieto-muuttujien nimet talteen (jos annettu)
		if len(state_position_variables) > 1:
			self.state_position_variables_list = state_position_variables.split(",")
			if len(self.state_position_variables_list) != 2:
				print("ESU: Incorrect position data: %s" % state_position_variables)
				return False
			cnt = 0
			self.position_lon_variable_name = ""
			self.position_lat_variable_name = ""
			print("ESU: position variables:")
			for var_name in self.state_position_variables_list:
				if len(var_name) > 1:
					cnt += 1
					self.position_variables[var_name] = ""
					print(" %5d: %s" % (cnt,var_name))
					
					if "LONGITUDE" in var_name or "ongitude" in var_name or "X" in var_name:
						self.position_lon_variable_name = var_name
						print("ESU: Found position LONGITUDE-name: %s" % (var_name))
					elif "LATITUDE" in var_name or "atitude" in var_name or "Y" in var_name:
						self.position_lat_variable_name = var_name
						print("ESU: Found position LATITUDE-name : %s" % (var_name))
			
			# Tarkistetaan löytyikö paikkatietomuuttujat
			if self.position_lon_variable_name == "":
				print("ESU: Not tound position LONGITUDE-name")
				return False
			if self.position_lat_variable_name == "":
				print("ESU: Not tound position LATITUDE-name")
				return False
			
		return True
		
	def do_variable_operations(self,cnt,variable_oper_string):

		var_name1 = variable_oper_string
		var_value1 = ""
		var_name2 = ""

		var_oper_mode = 0
		var_oper_right_part = ""

		#print("ESU: do_variable_operations")

		# Jos nimessä on sijoitus 
		if "=" in variable_oper_string:

			#print("ESU: do_variable_operations: = : %s" % variable_oper_string)

			var_oper_list = variable_oper_string.split("=")
			var_name1 = var_oper_list[0].lstrip().rstrip()
			var_value1 = var_oper_list[1].lstrip().rstrip()

			#print(" %5d: \"%s\" = \"%s\"" % (cnt,var_name1,var_value1))

			first_char = var_value1[0]
			last_char = var_value1[len(var_value1)-1]

			# Jos arvon sijoitus toisesta muuttujasta
			if first_char == "<" and last_char == ">":
				
				var_oper_mode = 4

				var_name2 = var_value1[1:-1]			
				#print("sets value from variable: %s" % var_name2)

				var_oper_right_part = var_value1
				try:
					# Kopioidaan arvo toisesta muuttujasta
					ana.variables[var_name1] = ana.variables[var_name2]
				except KeyError:
					print("ESU: do_variable_name_operations: ERR: Mode: %s, Not found variables: %s or %s in state: %s" % (var_oper_mode,var_name1,var_name3,self.name))
			else:

				var_oper_mode = 2
				var_oper_right_part = var_value1

				# Tähän vielä regexp ??
				# var_oper_mode = 3

				try:
					# Sijoitetaan arvo muuttujaan
					ana.variables[var_name1] = var_value1
				except KeyError:
					print("ESU: do_variable_name_operations: ERR: Mode: %s, Not found variable: %s in state: %s" % (var_oper_mode,var_name1,self.name))

		else:
			var_oper_mode = 1

		print(" %5d: mode:%s, \"%s\": \"%s\" \"%s\"" % (cnt,var_oper_mode,var_name1,var_oper_right_part,ana.variables[var_name1]))

		return var_oper_mode,var_name1,var_value1,var_name2

	def read_datafile(self,datafile_name):
	
		# Luetaan datatiedosto (jos se annettu)
		#if len()
		if os.path.isfile(datafile_name):
		
			f = open(datafile_name, 'r')
			lines = f.readlines()
			f.close()
			line_counter = 0
			# Kaydaan lapi loki-tiedoston rivit
			for line in lines:
				line_counter += 1
				
				# Poistetaan rivinvaihdot riviltä
				line = line.replace("\n","")
				
				#print("%5d: %s" % (line_counter,line))
				
				#line_list = line.split("\t")
				line_list = line.split(",")
				line_list_len = len(line_list)
				#print("ESU: line_list: %5d: %s" % (line_counter,line_list))
				if line_list_len > 2:
					
					counter = line_list[0]
					lon = line_list[1]
					lat = line_list[2]
					
					# Asetetaan position-data laatikon nurkkapisteiden koordinaateista
					if counter == "1":
						self.position_area_left_down_lon = lon
						self.position_area_left_down_lat = lat
					if counter == "3":
						self.position_area_right_up_lon = lon
						self.position_area_right_up_lat = lat
				else:
					print("ESU: ERR: Incorrect position data: %s" % (line))
					return False
					
			#print("position_area_left_down_lon = %s" % self.position_area_left_down_lon)
			#print("position_area_left_down_lat = %s" % self.position_area_left_down_lat)
			#print("position_area_right_up_lon  = %s" % self.position_area_right_up_lon)
			#print("position_area_right_up_lat  = %s" % self.position_area_right_up_lat)

		else:
			return False

		return True
		
		#else:
		#	print("ESU: ERR: Not found datafile: %s" % datafile_name)
		#	return self.onexit(-1)
		
	def read_logfile(self,logfile_name,start_time,stop_time,state_type_param):
	
		self.log_column_numbers = 0
		self.log_column_names_list = []
		
		last_read_variables = {}
		self.last_found_variables = {}
		
		if os.path.isfile(logfile_name):
		
			f = open(logfile_name, 'r')
			lines = f.readlines()
			f.close()
			
			line_counter = 0
			line_sel_counter = 0
			line_found_counter = 0
			error_counter = 0
			last_line = ""
			
			self.position_counter = 0
						
			# Kaydaan lapi loki-tiedoston rivit
			for line in lines:
			
				# Hylätään tyhjät rivit
				if len(line) < 2:
					continue
			
				# Poistetaan rivinvaihdot riviltä
				line = line.replace("\n","")
			
				line_counter += 1
				#line_list = line.split("\t")
				line_list = line.split(",")
				line_list_len = len(line_list)
				
				#print("ESU: line_list: %5d: %s" % (line_counter,line_list))
				#print("ESU: line_list_len: %d" % (line_list_len))
				
				# Otsikkorivi
				if line_counter == 1:

					# Tätä ei välttämättä tarvita ?!
					#if not "Counter" in line_list[0]:
					#	print("ESU: ERR: Illegal log-file: %s" % logfile_name)
					#	self.onexit(-1)
					#	return self.onexit(0)
						
					# Muodostetaan muuttujat
					for column_name in line_list:

						# Poistetaan mahdolliset spacet alusta ja lopusta
						#column_name = column_name.lstrip().rstrip()

						last_read_variables[column_name]=""
						
					# Otsikon sarakkeiden nimet ja lukumäärä talteen
					self.log_column_names_list = line_list
					self.log_column_numbers = line_list_len
				
					#print("ESU: Headerline: \n%s" % line)
					
				# Muuten data-rivi
				else:
				
					#if line_counter > 5:
					#	sys.exit()
				
					# Jos rivilla ei ollut sarakkeita saman verran kuin otsikossa,
					# hylätään rivi
					if line_list_len != self.log_column_numbers:
						continue
					
					line_sel_counter += 1
					
					# Luetaan rivin sarakkeiden arvot luettujen muuttujiin
					col_index = 0
					for column_name in self.log_column_names_list:
						var_value = line_list[col_index]

						# Poistetaan mahdolliset spacet alusta ja lopusta
						#var_value = var_value.lstrip().rstrip()

						last_read_variables[column_name] = var_value
						#print("ESU: %5d: Var name: %-20s value: \"%s\"" % (col_index,column_name,last_read_variables[column_name]))
						col_index += 1
						
					#timestamp_str = last_read_variables["TIMESTAMP"]
					timestamp_str = last_read_variables[self.state_log_time_column]
					line_timestamp = datetime.strptime(timestamp_str,"%Y-%m-%d %H:%M:%S")
					
					#print("line_timestamp = %s, start_time = %s, stop_time = %s" % (line_timestamp,start_time,stop_time))

					# Piirretään löydetty tapahtuma GUI:hin
					#if self.gui_enable == 1:
					#	self.draw_event(self.name,line_timestamp,"")

					# Tarkistetaan aikaväli
					if line_timestamp >= start_time and line_timestamp < stop_time:
						line_sel_counter += 1
						#print("ESU: Line %s in time-gap: %s -- %s" % (line,ana.variables["START-TIMESTAMP"],ana.variables["STOP-TIMESTAMP"]))
						#print("ESU: Line %s in time-gap: %s -- %s" % (line,start_time,stop_time))
						
						# Piirretään löydetty tapahtuma GUI:hin
						if self.gui_enable == 1:
							self.draw_event(self.name,line_timestamp,"")

						# Onko rivin muuttujien arvot samat kuin input-muuttujien arvot
						ok_count = 0
						var_count = 0
						for var_name in self.state_log_variables_list:
							var_count += 1
							try: 
								#print("   name = %-15s last var = %-15s var = %-15s" % (var_name,last_read_variables[var_name],self.log_variables[var_name]))
								if last_read_variables[var_name] == self.log_variables[var_name]:
									ok_count += 1
							except KeyError:
								print("ESU: ERR: Not found input-variable: %s" % (var_name))
								return self.onexit(-1)
								
						#print("ok_count=%s ,var_count=%s" % (ok_count,var_count))

						if ok_count == var_count:
						
							line_found_counter += 1

							# Viimeiset löydetyt muuttujat talteen
							for column_name in self.log_column_names_list:
								self.last_found_variables[column_name] = last_read_variables[column_name]
								last_line = line
								self.line_found_timestamp = line_timestamp
						
							# Jos oli ensimmäisen tapahtuman haku
							if state_type_param == "First":
								print("ESU: %s: First event was found" % (self.name))
								print("ESU: line      : \n%s" % (line))
								
								self.line_found_timestamp = line_timestamp
								return self.onexit(1)
							
							# Jos paikkatietoalueelta lähdön etsintä
							elif state_type_param == "Leaving":
								ret = self.check_position_event(state_type_param)
								if ret == True:
									return self.onexit(1)
								
							# Jos paikkatietoalueelle tulon etsintä
							elif state_type_param == "Entering":
								ret = self.check_position_event(state_type_param)
								if ret == True:
									return self.onexit(1)

						# Pitää myös "poistaa" käytetty viesti, että sitä ei oteta uudestaan !!??
			
			print("ESU: line_counter       = %d" % line_counter)
			print("ESU: line_found_counter = %d" % line_found_counter)
			print("ESU: line_sel_counter   = %d" % line_sel_counter)
			
			# Jos oli viimeisen tapahtuman haku
			if state_type_param == "Last":
				if line_found_counter == 0:
					return self.onexit(0)
				else:
					
					print("ESU: %s: Last event was found" % (self.name))
					print("ESU: line      : \n%s" % (last_line))
					return self.onexit(1)
			
		else:
			print("ESU: ERR: Not found logfile: %s" % logfile_name)
			return self.onexit(-1)
			
		return self.onexit(0)
		
	def run(self,state_counter,start_time,stop_time,logfile_name,datafile_name,state_log_time_column,
			state_log_variables,state_data_variables,state_position_variables,state_type):

		print("")
		print("----------------------------------------------------------------")
		print("ESU: %s is running: start_time = %s, stop_time = %s" % (self.name,start_time,stop_time))
		print("ESU: read orig logfile_name  : %s" % logfile_name)
		print("ESU: read orig datafile_name : %s" % datafile_name)
		print("ESU: Search type: %s" % state_type)
		
		#self.log_column_numbers = 0
		#self.log_column_names_list = []
		
		# Aikasarakkeen nimi talteen
		self.state_log_time_column = state_log_time_column
		
		state_type_list = state_type.split(":")
		state_type_list_len = len(state_type_list)
		if state_type_list_len < 2:
			print("ESU: ERR: Length %s is incorrect in type: %s" % (state_type_list_len,state_type))
			self.onexit(-1)
		
		# Tarkistetaan, että tyyppitiedot lailliset
		state_type_ok = False
		for legal_state_type in legal_state_types:
			if state_type == legal_state_type:
				state_type_ok = True
		if state_type_ok == False:
			print("ESU: ERR: ESU type: %s is illegal" % state_type)
			self.onexit(-1)
		
		state_type_name 	= state_type_list[0]
		state_type_param	= state_type_list[1]
		state_type_param2 = ""
		if state_type_list_len > 2:
			state_type_param2	= state_type_list[2]

		#print("ESU: state_type_name: %s : state_type_param : %s" % (state_type_name,state_type_param))
		
		# Jos haetaan monta samanlaista tapahtumaa peräkkäin
		if state_type_param2 == "Serial":

			try:
				serial_values = ana.variables[state_data_variables]
				#print("serial_values = %s" % serial_values)
			except KeyError:
				print("ESU: ERR: Not found data variable in state: %s" % (self.name))
				return (False)

			serial_vars_list = serial_values.split(",")

			print("ESU: names of serial areas: %s" % serial_vars_list)
			for serial_var in serial_vars_list:

				print("\nESU: Start to serial search for area:  %s ------------------ " % serial_var)

				state_data_variables = "SERIAL-ID"
				ana.variables["SERIAL-ID"] = serial_var
				ret = self.run_esu_state(state_log_variables,state_data_variables,state_position_variables,
							logfile_name,datafile_name,start_time,stop_time,state_type_param)

				if ret == "Found":
					start_time = ana.variables["INT-FOUND-TIMESTAMP"]
				else:
					return ret

			return ret

		# Muuten haetaan vain yksi tapahtuma
		else:
			return self.run_esu_state(state_log_variables,state_data_variables,state_position_variables,
							logfile_name,datafile_name,start_time,stop_time,state_type_param)
		
	def run_esu_state(self,state_log_variables,state_data_variables,state_position_variables,
					logfile_name,datafile_name,start_time,stop_time,state_type_param):

		# Luetaan inputtina saadut loki-, data- ja paikkatieto-muuttujat
		ret = self.read_input_variables(state_log_variables,state_data_variables,state_position_variables)
		if ret == False:
			print("ESU: ERR: Reading input variables")
			self.onexit(-1)
		
		# Jos lokitiedoston nimessä on muuttuja, pitää sen arvo "purkaa" nimeen
		# Näin on esim. bussilokiessa, jossa tiedoston nimessä on bussinumero. Esim. APO_304_LOCAT.csv)

		all_variables_list = ana.variables.keys()
		#ret, logfile_name = self.get_variable_value(logfile_name,self.state_log_variables_list)		
		ret, logfile_name = self.get_variable_value(logfile_name,all_variables_list)
		if ret == False:
			print("ESU: ERR: Getting log-variables")
			self.onexit(-1)

		#ret, datafile_name = self.get_variable_value(datafile_name,self.state_data_variables_list)			
		ret, datafile_name = self.get_variable_value(datafile_name,all_variables_list)
		if ret == False:
			print("ESU: ERR: Getting data-variables")
			self.onexit(-1)
			
		print("ESU: read logfile_name  : %s" % logfile_name)
		print("ESU: read datafile_name : %s" % datafile_name)
	
		# Luetaan datatiedosto (jos käytössä) ja haetaan sieltä tiedot data-muuttujilla
		ret = self.read_datafile(datafile_name)
		if ret == False:
			print("ESU: WARN: Reading datafile (or it is not exist)")
			self.onexit(-1)
		
		# Luetaan lokitiedosto ja haetaan sieltä tiedot log-muuttujilla halutulla aikavälillä
		return self.read_logfile(logfile_name,start_time,stop_time,state_type_param)

#******************************************************************************
#       
#	CLASS:	BMU
#
#******************************************************************************
class BMU:

	#global variables
	
	name="Unknown"
	states = []
	transition_names = {}
	start_state_name = ""
	transition = {}
	transition_function = {}
	state_onentry_function = {}
	state_onexit_function = {}
	end_state_name = ""
	current_state_name = ""
	state_array = {}
	state_counter = 0
	start_time = ""
	stop_time = ""
	state_logfiles = {}
	state_datafiles = {}
	state_settings = {}
	state_log_time_column = {}
	state_log_variables = {}
	state_data_variables = {}
	state_position_variables = {}
	state_type = ""
	state_start_time_limit = ""
	state_stop_time_limit = ""
	variables_list = []
	start_state_counter = 0
	#state_found_time = {}
	state_found_metadata = {}
	state_found_counter = 0
	#state_found_list = []
	state_event_num = {}
	event_last_stop_timestamp = {}

	color_list_counter = 0
	color_list = [QColor(255,0,0,127),
				  QColor(0,255,0,127),
				  QColor(0,0,255,127),
				  QColor(255,0,255,127),
				  QColor(0,255,255,127),
				  QColor(0,0,0,127)]

	def __init__(self,name,analyze_file_mode,states,state_order,transition_names,start_state_name,transition,transition_function,
				 state_onentry_function,state_onexit_function,end_state_name,state_logfiles,
				 state_datafiles,state_settings,state_log_time_column,state_log_variables,state_data_variables,
				 state_position_variables,state_type,state_start_time_limit,state_stop_time_limit,
				 gui_enable,gui_seq_draw_mode,gui,state_GUI_line_num,analyzing_mode):
				 
		self.analyze_file_mode=analyze_file_mode
		print("self.analyze_file_mode = %s\n" % self.analyze_file_mode)		
		self.name=name
		print("self.name = %s\n" % self.name)
		self.states=states
		print("self.states = %s\n" % self.states)
		self.state_order=state_order
		print("self.state_order = %s\n" % self.state_order)
		self.transition_names=transition_names
		print("self.transition_names = %s\n" % self.transition_names)
		self.start_state_name=start_state_name
		print("self.start_state_name = %s\n" % self.start_state_name)
		self.transition=transition
		print("self.transition = %s\n" % self.transition)
		self.transition_function=transition_function
		print("self.transition_function = %s\n" % self.transition_function)
		self.state_onentry_function=state_onentry_function
		print("self.state_onentry_function = %s\n" % self.state_onentry_function)
		self.state_onexit_function=state_onexit_function
		print("self.state_onexit_function = %s\n" % self.state_onexit_function)
		self.end_state_name=end_state_name
		print("self.end_state_name = %s\n" % self.end_state_name)
		self.state_logfiles=state_logfiles
		print("self.state_logfiles = %s\n" % self.state_logfiles)
		self.state_datafiles=state_datafiles
		print("self.state_datafiles = %s\n" % self.state_datafiles)
		self.state_settings=state_settings
		print("self.state_settings = %s\n" % self.state_settings)
		self.state_log_time_column=state_log_time_column
		print("self.state_log_time_column = %s\n" % self.state_log_time_column)
		self.state_log_variables=state_log_variables
		print("self.state_log_variables = %s\n" % self.state_log_variables)
		self.state_data_variables=state_data_variables
		print("self.state_data_variables = %s\n" % self.state_data_variables)
		self.state_position_variables=state_position_variables
		print("self.state_position_variables = %s\n" % self.state_position_variables)
		self.state_type=state_type
		print("self.state_type = %s\n" % self.state_type)
		self.state_start_time_limit=state_start_time_limit
		print("self.state_start_time_limit = %s\n" % self.state_start_time_limit)
		self.state_stop_time_limit=state_stop_time_limit
		print("self.state_stop_time_limit = %s\n" % self.state_stop_time_limit)
		
		self.gui_enable = gui_enable
		print("self.gui_enable = %s\n" % self.gui_enable)
		self.gui = gui		

		self.state_GUI_line_num = state_GUI_line_num
		print("self.state_GUI_line_num = %s\n" % self.state_GUI_line_num)

		self.gui_seq_draw_mode = gui_seq_draw_mode
		print("self.gui_seq_draw_mode = %s\n" % self.gui_seq_draw_mode)

		#print("variables = %s" % variables)
		
		self.variables_list = ana.variables.keys()
		
		self.trace_cnt = 0

		self.analyzing_mode,self.analyzing_col_num = analyzing_mode.split(":")
		print("self.analyzing_mode = %s, col =%s\n" % (self.analyzing_mode,self.analyzing_col_num ))

		print("")
		
	def drawEventSequence(self):

		#print(" ******* drawEventSequence")

		state_cnt = 0

		# Seuraava piirtoväri listalta
		#self.color_list_counter += 1
		#if self.color_list_counter >= len(self.color_list):
		#	self.color_list_counter = 0

		# Piirto-moodi
		# Jos aikajärjestyksessä
		if self.gui_seq_draw_mode == "time":
			sorted_state_list = sorted(self.state_found_metadata.keys(), 
				key=lambda tila: self.state_found_metadata[tila][0])
			#print("  Time-order: %s" % sorted_state_list)
		# Muuten, hakujärjestyksessä
		else:
			sorted_state_list = sorted(self.state_found_metadata.keys(), 
				key=lambda tila: self.state_found_metadata[tila][1])
			#print("  Search-order: %s" % sorted_state_list)

		# Lasketaan sekvenssin tietoja COMPARE-modea varten
		for state_name in sorted_state_list:
			state_time,state_order = self.state_found_metadata[state_name]	

			# Referenssiaika talteen COMPARE-modea (kun piirretään tracet päällekkäin) varten
			# Määritetään mitä saraketta käytetään refenenssinä
			if state_cnt == int(self.analyzing_col_num):
				if self.trace_cnt == 0:
					self.gui.setReferenceTime(state_time)
				self.gui.setTraceReferenceTime(state_time,state_cnt)
			state_cnt += 1

		state_cnt = 0

		# Piirretään sekvenssi
		for state_name in sorted_state_list:
			#state_time = self.state_found_time[state_name]

			# Luetaan tilan metadata: aika ja suoritusjärjestys
			state_time,state_order = self.state_found_metadata[state_name]

			#print(" *** drawEventSequence: state_cnt=%s, trace_cnt=%s" % (state_cnt,self.trace_cnt))

			#print("   %4d: state: %-20s : %s" % (state_cnt,state_name,str(state_time)))

			new_time = state_time
			try:
				new_event_num = self.state_GUI_line_num[state_name]
				#print("      BMU: GUI-line number: %s" % new_event_num)
			except:
				print("BMU: ERR: Not found state: %s for GUI-line" % state_name)

			if state_cnt > 0:

				color = QColor(255,0,0,127)
				try:
					color = self.color_list[self.color_list_counter]
					#print("BMU: Color: %s for cnt: %s " % (color,self.color_list_counter))					
				except:
					print("BMU: ERR: Not found color for cnt: %s" % self.color_list_counter)

				self.gui.drawTraceLine(self.gui.qp,old_event_num,old_time,new_event_num,new_time,color)

			old_time = new_time
			old_event_num = new_event_num
			state_cnt += 1

		self.trace_cnt += 1

	def draw_timelimits(self,state_name,timestamp_start,timestamp_stop):

		# Säädetään, että aikajanat eivät mene päällekkäin, vaan vierekkäin

		# Katsotaan GUI:n line kohtaisesti eikä vain tilakohtaisesti, koska yhdessä linjassa
		# voi olla useita tiloja !!
		try:
			line_num = self.state_GUI_line_num[state_name]
		except:
			print("BMU: ERR: Not found GUI-line for state: \"%s\"" % (state_name))
			return

		event_offset = 0
		if line_num in self.event_last_stop_timestamp.keys():

			event_offset,last_stop_time = self.event_last_stop_timestamp[line_num]
			#print("  event_offset=%s, last_stop=%s, timestamp=%s" % (event_offset,last_stop_time,timestamp_start))

			if timestamp_start < last_stop_time:
				event_offset += 1
				if event_offset > 4:
					event_offset = 0
		
		self.event_last_stop_timestamp[line_num] = event_offset,timestamp_stop

		# Piirretään aikajana
		color = self.color_list[self.color_list_counter]
		self.gui.drawTimeLine(self.gui.qp,line_num,event_offset,timestamp_start,timestamp_stop,color)


	def get_variable_value(self,var_string):
	
		# Huom! Tämä funktio samantyyppinen kuin ESU-luokassa. Voisi joskus yhdistää ?
	
		self.variables_list = ana.variables.keys()
	
		# Haetaan muuttujista merkkijonossa käytetyä muuttujaa
		for var_name in self.variables_list:
			var_name_ext = "<" + var_name + ">"
			
			# Jos löytyi, korvataan muuttujan nimi sen arvolla
			if var_name_ext in var_string:
			
				try:
					var_value = ana.variables[var_name]
					print("var_name = %s, var_value = %s" % (var_name,var_value))
					
				except KeyError:
					print("BMU: ERR: Not found variable: %s in state: %s (get_variable_value)" % (var_name,self.name))
					sys.exit()
				
				var_string = var_string.replace(var_name_ext,str(var_value))
		
		return var_string
		
	def print_variables(self):
		
		self.variables_list = ana.variables.keys()
	
		# Haetaan muuttujista merkkijonossa käytetyä muuttujaa
		cnt = 0
		for var_name in sorted(self.variables_list):
			cnt += 1
			var_value = ana.variables[var_name]
			print("%5d: Variable: %-25s = \"%s\"" % (cnt,var_name,var_value))
			
	def convert_time_limit_string(self,time_limit_str):
		#print("")
		
		# Haetaan muuttujien arvot
		time_limit_str_with_values = self.get_variable_value(time_limit_str)
		
		print("time_limit_str_with_values = %s" % time_limit_str_with_values)
		
		time_limit_list = time_limit_str_with_values.split(",")
		time_limit_list_len = len(time_limit_list)
		
		if time_limit_list_len == 2:
		
			time_value_str = time_limit_list[0]
			
			# Pitää muuttaa stringistä takaisin datetime-muotoon, että voidaan laskea
			time_value = datetime.strptime(time_value_str,"%Y-%m-%d %H:%M:%S")
			
			time_delta_value = int(time_limit_list[1])
			#print("time_value = %s" % time_value)
			#print("time_delta_value = %s" % time_delta_value)
			time_new = time_value + timedelta(seconds=time_delta_value)
			#print("time_new = %s" % time_new)
			
			return time_new
			
		else:
			print("BMU: Incorrect time-limit: %s" % time_limit_str_with_values)
			sys.exit()

	def run_function(self,function_name):

		# Ajetaan funktio
		if self.analyze_file_mode == "OLD":
			function_name  = "ana." + function_name + "()"
		else:
			function_name  = "ana_new." + function_name + "()"

		print("function_name = %s" % function_name)
		code_str = compile(function_name,"<string>","eval")
		eval(code_str)
			
	def run(self):
		
		# Luodaan tilat ja tehdään niistä taulukko, johon viitataan tilan nimellä
		for state in self.states:
			self.state_array[state] = ESU(state,self.gui_enable,self.gui,self.state_GUI_line_num)
			#print("BMU: ESU: %s : %s" % (state,self.state_array[state]))
			
		# Alkutilan nimi
		self.current_state_name=self.start_state_name
		
		# Ensimmäisen tila nimi
		self.first_state_name = self.transition[self.current_state_name][0]
		print("first_state_name = %s" % self.first_state_name)

		# Käytetään 1. tilasiirtymää
		ret = self.transition_names[0]
		
		# Nollataan GUI:n aikaraja-janat
		self.event_last_stop_timestamp = {}

		self.color_list_counter = 0
		self.start_state_counter = 0

		self.trace_cnt = 0

		# Ikiluuppi
		while 1:
			
			# Tulostetaan tämänhetkiset muuttujat ja niiden arvot
			#self.print_variables()
			
			# Käynnistetään seuraava tila
			try:

				new_state_list = self.transition[self.current_state_name]

				# Haetaan palautusarvon perusteella seuraavan tilan nimi
				try:
					new_state_index = self.transition_names.index(ret)
					new_state_name = new_state_list[new_state_index]
					print("BMU: Found new state: %s by transition: %s index: %s" % (new_state_name,ret,new_state_index))
				except ValueError:
					print("BMU: ERR: Not found state for transition: %s" % ret)
					return 0
				
				self.state_counter += 1
				
				# Mahdollisen tilasiirtymäfunktion haku ja ajo ennen uuteen tilaan menoa
				try:
					transition_function_list = self.transition_function[self.current_state_name]
					try:
						transition_function_name = transition_function_list[new_state_index]
						#print("transition_function_name = %s" % transition_function_name)
						if len(transition_function_name) > 0:
							print("BMU: Found new transition-function: %s by transition: %s index: %s" % (transition_function_name,ret,new_state_index))

							# Ajetaan funktio
							self.run_function(transition_function_name)

					except ValueError:
						print("BMU: ERR: Not found state for transition-function: %s" % ret)
						return 0
						
				except KeyError:
					print("BMU: No transition_function for state: %s" % self.current_state_name)
					
				# Uuden tilan nimi
				self.current_state_name=new_state_name
				
				# Uuden tilan mahdollisen onentry-funktion haku ja ajo ennen uuteen tilaan menoa
				try:
					onentry_function_name = self.state_onentry_function[self.current_state_name]
					if len(onentry_function_name) > 0:
						print("BMU: Found new onentry-function: %s" % (onentry_function_name))

						# Ajetaan funktio
						self.run_function(onentry_function_name)

				except KeyError:
					print("BMU: No onentry_function for state: %s" % self.current_state_name)
				
				# Jos oli lopputila, lopetetaan
				if new_state_name == self.end_state_name:
					print("BMU: ESU: %s end state\n" % (self.current_state_name))

					# Tulostetaan tilojen tapahtumasekvenssi GUI:hin
					if self.gui_enable == 1:
						self.drawEventSequence()
						self.state_found_counter = 0
						self.state_found_metadata = {}

					return 1

				# Jos aloitustila
				if self.first_state_name == self.current_state_name:
					self.start_state_counter += 1
					print("  start_state_counter = %s" % self.start_state_counter)

					# Jos aloitustila toisen kerran (tilojen sekvenssi on käyty läpi)
					if self.start_state_counter > 1 and self.gui_enable == 1:
						self.drawEventSequence()
						self.state_found_counter = 0
						self.state_found_metadata = {}

					# Seuraava piirtoväri listalta
					self.color_list_counter += 1
					if self.color_list_counter >= len(self.color_list):
						self.color_list_counter = 0

					print("  color_list_counter = %s" % self.color_list_counter)

				# Tilan olio
				new_state = self.state_array[self.current_state_name]
		
				# Tiedostojen nimet
				logfile_name = self.state_logfiles[self.current_state_name]

				datafile_name = self.state_datafiles[self.current_state_name]
				
				# Lokitiedoston aikasarakkeen nimi
				state_log_time_column=self.state_log_time_column[self.current_state_name]
				
				# Lokitiedoston (haku)muuttujat
				state_log_variables=self.state_log_variables[self.current_state_name]
				
				# Datatiedoston (haku)muuttujat
				state_data_variables=self.state_data_variables[self.current_state_name]
				
				# Lokitiedoston mahdolliset paikkatieto muuttujat
				try:
					state_position_variables=self.state_position_variables[self.current_state_name]
				except KeyError:
					state_position_variables = ""
				
				#Tyyppi
				state_type=self.state_type[self.current_state_name]
				
				# Aikarajat
				self.start_time  = self.convert_time_limit_string(self.state_start_time_limit[self.current_state_name])
				self.stop_time   = self.convert_time_limit_string(self.state_stop_time_limit[self.current_state_name])
				print("BMU: start_time = %s stop_time = %s" % (self.start_time,self.stop_time))
				
				# Piiretään GUI:hin aikaraja-janat
				if self.gui_enable == 1:
					self.draw_timelimits(self.current_state_name,self.start_time,self.stop_time)

				# Käynnistetään tila
				ret = new_state.run(self.state_counter,
									self.start_time,
									self.stop_time,
									logfile_name,
									datafile_name,
									state_log_time_column,
									state_log_variables,
									state_data_variables,
									state_position_variables,
									state_type)
								
				# Tilan mahdollisen onexit-funktion haku ja ajo tilan ajon jälkeen
				try:
					onexit_function_name = self.state_onexit_function[self.current_state_name]
					if len(onexit_function_name) > 0:
						print("BMU: Found new onentry-function: %s" % (onexit_function_name))

						# Ajetaan funktio
						self.run_function(onexit_function_name)
						
				except KeyError:
					print("BMU: No onexit_function for state: %s" % self.current_state_name)
					
				print("BMU: ESU: %s return: %s" % (self.current_state_name,ret))

				if ret == "Found":

					self.state_found_counter += 1
					self.state_found_metadata[self.current_state_name] = ana.variables["INT-FOUND-TIMESTAMP"],self.state_found_counter


			except KeyError:
				print("BMU: ERR: Not found transitions for state: %s" % self.current_state_name)
				return 0

		
def import_analyze_file(pathname,filename,mode):

	print("import_analyze_file: %s %s, mode: %s" % (pathname,filename,mode))

	#filename_full = pathname + filename

	sys.path.append(pathname)

	if mode == "OLD":

		# Käytetään alkuperäistä syntaksia
		from importlib import import_module
		ana = import_module(filename)
		ana_new = ""

	else:

		# Otetaan pohjaksi tyhjä alkuperäinen tiedosto
		from importlib import import_module
		ana = import_module("logdig_analyze_template")

		# Muutetaan uusi syntaksi alkuperäiseen syntaksiin
		from importlib import import_module
		ana_new = import_module(filename)

		#print("VARIABLE keys: %s" % ana_new.VARIABLES.keys())
		for var_key in ana_new.VARIABLES.keys():
			var_value = ana_new.VARIABLES[var_key]
			print("VAR: %s = %s" % (var_key,var_value))

			ana.variables[var_key] = var_value

		ana.states.append("START")
		ana.start_state_name = "START"
		for var_key in ana_new.START.keys():
			var_value = ana_new.START[var_key]
			print("START: %s = %s" % (var_key,var_value))

			if var_key == "state":
				ana.transition["START"] = [var_value,"",""]
			elif var_key == "func":
				ana.transition_function["START"] = [var_value,var_value,""] 
				#ana.state_onexit_function["START"] = var_value

		ana.ESU_counter = 0
		#print("ESU keys: %s" % ana_new.ESU.keys())
		for var_key in ana_new.ESU.keys():
			var_value = ana_new.ESU[var_key]
			#print("ESU: %s = %s" % (var_key,var_value))

			ana.ESU_counter += 1
			ana.state_order[var_key] = ana.ESU_counter

			print("ESU: %s, cnt: %s" % (var_key,ana.ESU_counter))

			ana.states.append(var_key)

			ana.state_position_variables[var_key] = ["",""]
			ana.transition[var_key] = ["","",""]
			ana.transition_function[var_key] = ["","",""] 

			# Alustetaan optionaaliset arvot
			state_position_lon_variable = ""
			state_position_lat_variable = ""			
			ana.state_datafiles[var_key] = ""
			ana.state_data_variables[var_key] = ""

			for var_key2 in var_value.keys():
				var_value2 = var_value[var_key2]
				print("    ESU: %s = %s" % (var_key2,var_value2))

				if var_key2 == "esu_mode":
					ana.state_type[var_key] = var_value2
				elif var_key2 == "log_filename_expr":
					ana.state_logfiles[var_key] = var_value2
				elif var_key2 == "log_varnames":
					ana.state_log_variables[var_key] = var_value2
				elif var_key2 == "log_timecol_name":
					ana.state_log_time_column[var_key] = var_value2				
				elif var_key2 == "log_start_time_expr":
					ana.state_start_time_limit[var_key] = var_value2				
				elif var_key2 == "log_stop_time_expr":
					ana.state_stop_time_limit[var_key] = var_value2

				elif var_key2 == "ssd_lat_col_name":
					state_position_lat_variable = var_value2
				elif var_key2 == "ssd_lon_col_name":
					state_position_lon_variable = var_value2
				elif var_key2 == "ssd_filename_expr":
					ana.state_datafiles[var_key] = var_value2
				elif var_key2 == "ssd_varnames":
					ana.state_data_variables[var_key] = var_value2

				elif var_key2 == "TF_state":
					ana.transition[var_key][0] = var_value2
				elif var_key2 == "TF_func":
					ana.transition_function[var_key][0] = var_value2
				elif var_key2 == "TN_state":
					ana.transition[var_key][1] = var_value2
				elif var_key2 == "TN_func":
					ana.transition_function[var_key][1] = var_value2
				elif var_key2 == "TE_state":
					ana.transition[var_key][2] = var_value2
				elif var_key2 == "TE_func":
					ana.transition_function[var_key][2] = var_value2

				elif var_key2 == "onentry_func":
					ana.state_onentry_function[var_key] = var_value2
				elif var_key2 == "onexit_func":
					ana.state_onexit_function[var_key] = var_value2

				elif var_key2 == "GUI_line_num":
					ana.state_GUI_line_num[var_key] = var_value2	

			# Optionaaliset arvot samaan stringiin. Voisi tehdä paremminkin ?
			ana.state_position_variables[var_key] = state_position_lon_variable + "," + state_position_lat_variable			

		ana.states.append("STOP")
		ana.end_state_name = "STOP"
		for var_key in ana_new.STOP.keys():
			var_value = ana_new.STOP[var_key]
			print("STOP: %s = %s" % (var_key,var_value))

			if var_key == "func":
				#ana.transition_function[var_key][2] = var_value
				ana.state_onentry_function["STOP"] = var_value

		# Functions ??

	return ana,ana_new

#******************************************************************************
#
#	FUNCTION:	analyze_logs
#
#******************************************************************************
def analyze_logs(args,gui,source,trace_mode):

	global ana
	global ana_new
	#global legal_state_types
		
	# Luodaan tilakone
	SM = BMU("LOGDIG",args.analyze_file_mode,
						ana.states,
						ana.state_order,
						ana.transition_names,
						ana.start_state_name,
						ana.transition,
						ana.transition_function,
						ana.state_onentry_function,
						ana.state_onexit_function,
						ana.end_state_name,
						ana.state_logfiles,
						ana.state_datafiles,
						ana.state_settings,
						ana.state_log_time_column,
						ana.state_log_variables,
						ana.state_data_variables,
						ana.state_position_variables,
						ana.state_type,
						ana.state_start_time_limit,
						ana.state_stop_time_limit,
						args.gui_enable,
						args.gui_seq_draw_mode,
						gui,
						ana.state_GUI_line_num,
						args.analyzing_mode)

	print("SM name = %s" % SM.name)

	# Käynnistetään tilakone ja ajetaan analysoinnit
	SM.run()	

#******************************************************************************
#
#	FUNCTION:	init_analyzing
#
#******************************************************************************
def init_analyzing(args):

	global ana
	global ana_new
	global legal_state_types

	# Luetaan analysointitiedosto
	ana,ana_new = import_analyze_file(args.analyze_file_path,args.analyze_file,args.analyze_file_mode)

	days,months,years=args.date.split(".")
	print("date old = %s %s %s" % (days,months,years))
	date2 = "%s-%s-%s" % (years,months,days)
	print("date new = %s" % (date2))

	#ana.variables["INT-START-DATE"]		= args.date
	ana.variables["INT-START-DATE"]		= date2
	ana.variables["INT-START-TIME"]		= args.start_time
	ana.variables["INT-STOP-TIME"]		= args.stop_time
	ana.output_files_path = args.output_files_path

	# Lailliset tilan tyypit ja parametrit
	legal_state_types = ["SEARCH_EVENT:First","SEARCH_EVENT:Last",
						 "SEARCH_POSITION:Leaving","SEARCH_POSITION:Entering",
						 "SEARCH_POSITION:Leaving:Serial","SEARCH_POSITION:Entering:Serial"]

	# Lisätään lokitiedostoihin polku
	for state_logfile_name in ana.state_logfiles.keys():
		ana.state_logfiles[state_logfile_name]		= args.input_logs_path +  ana.state_logfiles[state_logfile_name]
		print("ESU: %-15s Logfile: %s" % (state_logfile_name, ana.state_logfiles[state_logfile_name]))
		
	# Lisätään datatiedostoihin polku
	for state_datafile_name in ana.state_datafiles.keys():
		ana.state_datafiles[state_datafile_name]		= args.input_ssd_path + ana.state_datafiles[state_datafile_name]
		print("ESU: %-15s Datafile: %s" % (state_datafile_name, ana.state_datafiles[state_datafile_name]))


#******************************************************************************
#
#	FUNCTION:	main
#
#******************************************************************************
def main():

	global ana
	global ana_new
	global legal_state_types

	print("version: %s" % g_version)

	parser = argparse.ArgumentParser()
	parser.add_argument('-date','--date', dest='date', help='date')
	parser.add_argument('-start_time','--start_time', dest='start_time', help='start_time')
	parser.add_argument('-stop_time','--stop_time', dest='stop_time', help='stop_time')
	parser.add_argument('-input_logs_path','--input_logs_path', dest='input_logs_path', help='input_logs_path')
	parser.add_argument('-input_ssd_path','--input_ssd_path', dest='input_ssd_path', help='input_ssd_path')
	parser.add_argument('-output_files_path','--output_files_path', dest='output_files_path', help='output_files_path')
	parser.add_argument('-analyze_file_path','--analyze_file_path', dest='analyze_file_path', help='analyze_file_path')
	parser.add_argument('-analyze_file','--analyze_file', dest='analyze_file', help='analyze_file')
	parser.add_argument('-analyze_file_mode','--analyze_file_mode', dest='analyze_file_mode', help='analyze_file_mode')
	parser.add_argument('-analyzing_mode','--analyzing_mode', dest='analyzing_mode', help='analyzing_mode')
	parser.add_argument('-gui_enable','--gui_enable', dest='gui_enable', type=int, help='gui_enable')
	parser.add_argument('-gui_seq_draw_mode','--gui_seq_draw_mode', dest='gui_seq_draw_mode', help='gui_seq_draw_mode')

	args = parser.parse_args()

	print("date              : %s" % args.date)
	print("start_time        : %s" % args.start_time)
	print("stop_time         : %s" % args.stop_time)
	print("input_logs_path   : %s" % args.input_logs_path)
	print("input_ssd_path    : %s" % args.input_ssd_path)
	print("output_files_path : %s" % args.output_files_path)
	print("analyze_file_path : %s" % args.analyze_file_path)
	print("analyze_file      : %s" % args.analyze_file)
	print("analyze_file_mode : %s" % args.analyze_file_mode)
	print("analyzing_mode    : %s" % args.analyzing_mode)
	print("gui_enable        : %s" % args.gui_enable)
	print("gui_seq_draw_mode : %s" % args.gui_seq_draw_mode)
	print("\n")

	config = configparser.ConfigParser()
	config.read('LogDig.ini')
	analyze_area_x = int(config['GEOMETRY']['Area_x'])
	analyze_area_y = int(config['GEOMETRY']['Area_y'])

	print("Logarea_x = %s" % analyze_area_x)
	print("Logarea_y = %s" % analyze_area_y)

	start_time = time.time()

	# Luetaan analysointitiedosto ja tehdään alustuksia
	init_analyzing(args)

	# Käynnistetään tarvittaessa GUI
	if args.gui_enable == 1:
		print("GUI enabled\n")

		args.state_order = ana.state_order

		app = QApplication(sys.argv)
		gui2 = GUI_AnalyzeArea(args,"Analyze area",analyze_area_x,analyze_area_y,1100,1000,0,0,1.0,
				analyze_logs,ana.state_GUI_line_num)

		sys.exit(app.exec_())

	else:
		analyze_logs(args,"","Ana","")

	print("\n Total execution time: %.3f seconds" % (time.time() - start_time))

if __name__ == '__main__':
    main()