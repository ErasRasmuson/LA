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
from MapGEkml import *

g_version = "$Id$"
analyze_run_counter = 0

#******************************************************************************
#       
#	CLASS:	LogFilesData
#
#******************************************************************************
class LogFilesData:

	logfile_already_read = {}
	logfile_lines = {}
	logline_index = {}
	logline_times = {}
	log_column_names_list = {}
	log_column_numbers = {}
	log_data_line_counter = {}

	def __init__(self):
		print(" >>>> LogFilesData: init")
		self.logfile_already_read = {}

	def read(self,logfile_name,time_column):
		#print(" >>>> LogFilesData: read_logfile: %s" % logfile_name)

		if os.path.isfile(logfile_name):
			
			# Tarkistetaan onko loki jo luettu (muistiin)
			log_already_read = 0
			try:
				log_already_read = self.logfile_already_read[logfile_name]
			except:
				log_already_read = 0

			print(" >>>> LogFilesData: log_already_read = %s" % log_already_read)

			time_column_index = 0

			if log_already_read == 0:

				self.logfile_lines[logfile_name] = []
				log_lines = []
				f = open(logfile_name, 'r')
				log_lines = f.readlines()
				f.close()
				
				file_line_counter = 0
				line_counter = 0
				self.log_data_line_counter[logfile_name] = 0
				# Käydään rivit läpi
				for line in log_lines:

					file_line_counter += 1 

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
					
					# Otsikkorivi (1. oikea rivi)
					if line_counter == 1:
												
						# Otsikon sarakkeiden nimet ja lukumäärä talteen
						self.log_column_names_list[logfile_name] = line_list
						self.log_column_numbers[logfile_name] = line_list_len
						#print(" >>>> LogFilesData: columns = %s" % line_list)

						# Aika-sarake talteen
						time_column_index = line_list.index(time_column)
						print(" >>>> LogFilesData: time column: %s index = %s" % (time_column,time_column_index))

						# Ei käydä enempää rivejä läpi ?
						#break
			
					# Muut rivit, haetaan aikaleimat riveille, jotta "takaisinpäin hakeminen"
					# on myöhemmin helppoa ja nopeaa.
					else:

						timestamp_str = line_list[time_column_index]
						line_timestamp = datetime.strptime(timestamp_str,"%Y-%m-%d %H:%M:%S")

						# Otetaan rivien aikaleimat talteen. Vai pitäisikö käyttää alkup. tiedoston logfile_lines-taulukkoa ?
						self.logline_times[logfile_name,self.log_data_line_counter[logfile_name]] = line_timestamp
						#print(" >>>> cnt = %s, time = %s" % (self.log_data_line_counter[logfile_name],line_timestamp))
						self.log_data_line_counter[logfile_name] += 1

						self.logfile_lines[logfile_name].append(line_list)

				#self.logfile_lines[logfile_name] = log_lines

				self.logline_index[logfile_name] = 0

				print(" >>>> LogFilesData: file_line_counter = %s, line_counter = %s" % (file_line_counter,line_counter))

				# Merkitään loki luetuksi (että myöhemmin ei tarvise lukea tiedostosta uudestaan)
				self.logfile_already_read[logfile_name] = 1

				return False,True
		else:
			print(" >>>> LogFilesData: Not found logfile: %s" % logfile_name)
			return True,False

		return False,False

	def get_lines(self,logfile_name):

		log_lines = []
		try:
			log_lines = self.logfile_lines[logfile_name]
		except:
			print(" >>>> LogFilesData: ERR: Not found log lines for: %s" % logfile_name)

		return log_lines

	def get_line_index(self,logfile_name):

		logline_index = 0
		try:
			logline_index = self.logline_index[logfile_name]
		except:
			print(" >>>> LogFilesData: ERR: Not found log line index for: %s" % logfile_name)

		print(" >>>> LogFilesData: get_line_index: %s" % logline_index)

		return logline_index

	def search_line_index(self,logfile_name,start_time):

		print(" >>>> LogFilesData: search_line_index: start_time=%s" % start_time)

		# Käytetään viimeistä (ei seuraavaa) luetun rivin indeksiä uudestaan 
		current_line_index = self.logline_index[logfile_name] - 1
		if current_line_index < 0:
			current_line_index = 0

		log_data_size = self.log_data_line_counter[logfile_name]

		#print(" >>>> LogFilesData: cur index: %s, max index: %s" % (current_line_index,log_data_size))

		if current_line_index > log_data_size - 1:
			print(" >>>> LogFilesData: ERR: current_line_index: %s > %s" % (current_line_index,log_data_size-1))
			return 0

		try:
			current_line_timestamp = self.logline_times[logfile_name,current_line_index]
		except:
			print(" >>>> LogFilesData: ERR: Not found timestamp for: %s and index: %s" % (logfile_name,current_line_index))
			return 0

		#print(" >>>> LogFilesData: search_line_index:   cur_time=%s, cur_ind=%s" % (current_line_timestamp,current_line_index))

		# Jos lokin viimeisen luetun rivin aikaleima on suurempi, kuin uuden haun alku-aikaleima
		if current_line_timestamp > start_time:

			#print(" >>>> LogFilesData: search_line_index: cur_time > start_time")

			# Haetaan taaksepäin uusi rivin indeksi, jonka aikaleima pienempi, kuin uuden haun alkuaika
			search_count = 0
			for index in range(current_line_index,-1,-1):

				#print(" >>> index = %s" % index)
				search_count += 1
				new_line_timestamp = self.logline_times[logfile_name,index]
				#print(" >>> index = %s, new_line_timestamp = %s" % (index,new_line_timestamp))
				if new_line_timestamp <= start_time:

					print(" >>>> LogFilesData: search_line_index: Backward: cur_ind=%s, cur_time=%s, new_ind=%s, new_time=%s, search_count=%s" % 
							(current_line_index,current_line_timestamp,index,new_line_timestamp,search_count))

					return index

		print(" >>>> LogFilesData: search_line_index: cur_ind=%s, cur_time=%s" % 
							(current_line_index,current_line_timestamp))
		return current_line_index


	def get_header_data(self,logfile_name):

		col_num = 0
		col_names = []
		try:
			col_names = self.log_column_names_list[logfile_name]
			col_num = self.log_column_numbers[logfile_name]
		except:
			print(" >>>> LogFilesData: ERR: Not found log column data for: %s" % logfile_name)

		return col_names,col_num

	def set_line_index(self,logfile_name,value):

		self.logline_index[logfile_name] = value


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
	log_lines = []
	#log_line_index = 1
	line_counter = 0
	line_sel_counter = 0
	line_found_counter = 0
	error_counter = 0
	last_line = ""
	logfile_already_read = {}
	esu_run_counter = 0

	def __init__(self,name,logfiles_data,gui_enable,gui,state_GUI_line_num,ge_kml_enable):

		self.name=name

		self.logfiles = logfiles_data

		self.gui_enable = gui_enable
		self.gui = gui

		self.state_GUI_line_num = state_GUI_line_num
		#print("ESU: state_GUI_line_num = %s" % self.state_GUI_line_num)

		self.ge_kml_enable = ge_kml_enable
		#print("ESU: ge_kml_enable = %s" % self.ge_kml_enable)

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
			#if self.gui_enable == 1:
			#	self.draw_event(self.name,self.line_found_timestamp,str(self.line_found_timestamp))

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
		
		# Lasketaan koordinaatin etäisyys alueen keskipisteeseen. Tämä vain lisätietoa !!
		lon_dist = self.position_area_center_lon - lon
		lat_dist = self.position_area_center_lat - lat
		
		#print("check_position_in_area: lon=%s, lat=%s" % (lon,lat))

		# Pitäisikö olla asetus, jolla laatikon koko voidaan ylikirjoittaa ?! 

		# Tarkistetaan onko koordinaatti suorakaiteen muotoisen alueen sisällä
		inside = False
		if lon < float(self.position_area_right_up_lon):
			if lon > float(self.position_area_left_down_lon):
				if lat < float(self.position_area_right_up_lat):
					if lat > float(self.position_area_left_down_lat):
						inside = True
						#return True

		#print("lon_dist = %.5f, lat_dist = %0.5f, inside = %s" % (lon_dist,lat_dist,inside))
		#return False
		return inside

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

			lat = self.last_found_new_variables[self.position_lat_variable_name]
			lon = self.last_found_new_variables[self.position_lon_variable_name]
			pos_time = self.last_found_new_variables[self.state_log_time_column]

			ana.variables["INT-LATITUDE-NEW"] = lat
			ana.variables["INT-LONGITUDE-NEW"] = lon
			ana.variables["INT-LOCAT-TIME-NEW"] = pos_time

			pos_old_in_area = self.check_position_in_area(ana.variables["INT-LONGITUDE-OLD"],ana.variables["INT-LATITUDE-OLD"])
			pos_new_in_area = self.check_position_in_area(ana.variables["INT-LONGITUDE-NEW"],ana.variables["INT-LATITUDE-NEW"])
				
			#print("%5d: pos_old_in_area=%s, pos_new_in_area=%s" % (self.position_counter,pos_old_in_area,pos_new_in_area))

			if state_type_param == "Leaving":
				#print("check_position_event: Leaving")
				
				# Tarkistetaan position-datasta ollaanko lähdetty alueelta
				if pos_old_in_area == True and pos_new_in_area == False:
					self.line_found_timestamp  = datetime.strptime(ana.variables["INT-LOCAT-TIME-NEW"],"%Y-%m-%d %H:%M:%S")
					print("Leaving ok: time: %s" % ana.variables["INT-LOCAT-TIME-NEW"])
					self.print_pos_event_data()
					return True

				# Jos jo ollaan jo valmiiksi alueen ulkopuolella. 
				# Periaatteessa tämä virhetapaus, mutta sallitaan koska alkuperäinen lokidata voi olla puutteellinen.
				# Pitäisi tehdä oma moodi: Outside ?
				elif pos_old_in_area == False and pos_new_in_area == False:

					ana.variables["INT-LATITUDE-NEW"] = ana.variables["INT-LATITUDE-OLD"] 
					ana.variables["INT-LONGITUDE-NEW"] = ana.variables["INT-LONGITUDE-OLD"]
					ana.variables["INT-LOCAT-TIME-NEW"] = ana.variables["INT-LOCAT-TIME-OLD"] 

					self.line_found_timestamp  = datetime.strptime(ana.variables["INT-LOCAT-TIME-NEW"],"%Y-%m-%d %H:%M:%S")
					print("Leaving: Already outside warning: time: %s" % ana.variables["INT-LOCAT-TIME-NEW"])
					self.print_pos_event_data()
					return True
					
			elif state_type_param == "Entering":
				#print("check_position_event: Entering")
				
				# Tarkistetaan position-datasta ollaanko tultu alueelle
				if pos_old_in_area == False and pos_new_in_area == True:
					self.line_found_timestamp  = datetime.strptime(ana.variables["INT-LOCAT-TIME-OLD"],"%Y-%m-%d %H:%M:%S")
					print("Entering ok: time: %s" % ana.variables["INT-LOCAT-TIME-OLD"])
					self.print_pos_event_data()
					return True

				# Jos ollaan valmiiksi alueen sisällä
				# Periaatteessa tämä virhetapaus, mutta sallitaan koska alkuperäinen lokidata voi olla puutteellinen.
				# Pitäisi tehdä oma moodi: Inside ?
				elif pos_old_in_area == True and pos_new_in_area == True:

					ana.variables["INT-LATITUDE-OLD"] = ana.variables["INT-LATITUDE-NEW"] 
					ana.variables["INT-LONGITUDE-OLD"] = ana.variables["INT-LONGITUDE-NEW"]
					ana.variables["INT-LOCAT-TIME-OLD"] = ana.variables["INT-LOCAT-TIME-NEW"] 

					self.line_found_timestamp  = datetime.strptime(ana.variables["INT-LOCAT-TIME-OLD"],"%Y-%m-%d %H:%M:%S")
					print("Entering: Already inside warning: time: %s" % ana.variables["INT-LOCAT-TIME-OLD"])
					self.print_pos_event_data()
					return True				
			else:
				print("check_position_event: Unknown")
				return False
		else:
			for column_name in self.log_column_names_list:
				self.last_found_new_variables[column_name] = self.last_found_variables[column_name]

		# Kirjoitetaan piste Google Earth kml-tiedostoon
		if self.ge_kml_enable == 1:
			lat = self.last_found_new_variables[self.position_lat_variable_name]
			lon = self.last_found_new_variables[self.position_lon_variable_name]
			pos_time = self.last_found_new_variables[self.state_log_time_column]
			coord_list = [[lon,lat]]
			write_mark_to_kml_file(self.klm_file_path_name,self.position_counter,coord_list,pos_time,200)

		return False
		
	def print_pos_event_data(self):

		print("POS OLD: %s, %s, %s" % (ana.variables["INT-LATITUDE-OLD"],ana.variables["INT-LONGITUDE-OLD"],ana.variables["INT-LOCAT-TIME-OLD"]))
		print("POS NEW: %s, %s, %s" % (ana.variables["INT-LATITUDE-NEW"],ana.variables["INT-LONGITUDE-NEW"],ana.variables["INT-LOCAT-TIME-NEW"]))

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

		# 14.6.2016 HUOM! Pitäisi vielä lisätä seuraavat moodit:
		# - 3: regexp
		# - (4: Toisen muuttujan arvon sijoitus, on jo !)
		# - 5: Integer (float) vertailu (<>=)
		# - 6: Integer (float) vertailu annetulla lukualueella (esim. 100-200)
		# - 7: Lista vertailu. Listassa sallitut arvot (String tai myös 5- ja 6-kohdan tietoja ?).
		# - 8: Haetaan arvo jostain taulukosta
		# - 9: SSD-haut vielä erikseen (ne ei kuulu tähän funktioon?) ?
		#		- Time window
		#		- "index" window (esim. paikkaikkuna)
		#		- Time + "index" window
		#		- "First" ?
		#		- "Last" ?
		#		- "External" ?

		print(" %5d: mode:%s, \"%s\": \"%s\" \"%s\"" % (cnt,var_oper_mode,var_name1,var_oper_right_part,ana.variables[var_name1]))

		return var_oper_mode,var_name1,var_value1,var_name2

	def read_datafile(self,datafile_name):
	
		# Luetaan datatiedosto (jos se annettu)
		#if len()
		if os.path.isfile(datafile_name):
		
			f = open(datafile_name, 'r')
			lines = f.readlines()
			f.close()
			data_line_counter = 0
			# Kaydaan lapi loki-tiedoston rivit
			for line in lines:
				data_line_counter += 1
				
				# Poistetaan rivinvaihdot riviltä
				line = line.replace("\n","")
				
				#print("%5d: %s" % (data_line_counter,line))
				
				if "\t" in line:
					line_list = line.split("\t")
				elif "," in line:
					line_list = line.split(",")
				line_list_len = len(line_list)
				#print("ESU: line_list: %5d: %s" % (data_line_counter,line_list))
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
					
			# Lasketaan alueen keskipiste (voisi tulla valmiinakin jostain ?)
			pos_area_width = float(self.position_area_right_up_lon) - float(self.position_area_left_down_lon) 
			pos_area_height = float(self.position_area_right_up_lat) - float(self.position_area_left_down_lat)
			self.position_area_center_lon = pos_area_width / 2 + float(self.position_area_left_down_lon)
			self.position_area_center_lat = pos_area_height / 2 + float(self.position_area_left_down_lat)

			#print("position_area_center_lon = %s" % self.position_area_center_lon)
			#print("position_area_center_lat = %s" % self.position_area_center_lat)

			#print("position_area_left_down_lon = %s" % self.position_area_left_down_lon)
			#print("position_area_left_down_lat = %s" % self.position_area_left_down_lat)
			#print("position_area_right_up_lon  = %s" % self.position_area_right_up_lon)
			#print("position_area_right_up_lat  = %s" % self.position_area_right_up_lat)

			# Kirjoitetaan alue Google Earth kml-tiedostoon
			if self.ge_kml_enable == 1:
				coord_list = []
				coord_list.append([self.position_area_left_down_lon,self.position_area_left_down_lat])
				coord_list.append([self.position_area_left_down_lon,self.position_area_right_up_lat])
				coord_list.append([self.position_area_right_up_lon,self.position_area_right_up_lat])
				coord_list.append([self.position_area_right_up_lon,self.position_area_left_down_lat])
				coord_list.append([self.position_area_left_down_lon,self.position_area_left_down_lat])	
				#write_area_to_kml_file(klm_file_path_name,stop_id,coord_list,200)
				write_area_to_kml_file(self.klm_file_path_name,datafile_name,coord_list,200)

		else:
			return False

		return True
		
		#else:
		#	print("ESU: ERR: Not found datafile: %s" % datafile_name)
		#	return self.onexit(-1)
		
	def read_logfile(self,logfile_name,start_time,stop_time,state_type_param,state_type_param2,serial_found_cnt):
		
		last_read_variables = {}
		self.last_found_variables = {}
		
		#print("state_type_param: %s, state_type_param2: %s, serial_found_cnt: %s" % (state_type_param,state_type_param2,serial_found_cnt))

		# Jos ei sarja-moodi tai sarja-moodi 1. kertaa, luetaan loki
		read_log = False
		if state_type_param2 != "Serial":
			read_log = True
		elif serial_found_cnt == -1:
			read_log = True

		if read_log == True:

			# Luetaan lokitiedostosta rivit muistiin (jos ei jo luettu)
			# Haetaan myös lokin otsikkorivi
			err,ret = self.logfiles.read(logfile_name,self.state_log_time_column)
			if err == True:
				print("ESU: ERR: Not found logfile: %s" % logfile_name)
				return self.onexit(-1)

			# jos lokitiedosto luettiin muistiin
			if ret == True:		
				self.line_counter = 0
				self.line_sel_counter = 0
				self.line_found_counter = 0
				self.error_counter = 0
				self.last_line = []
				self.position_counter = 0

				# Haetaan lokitiedosto luvun alkurivi (indeksi)
				#self.log_line_index = self.logfiles.get_line_index(logfile_name)
				
		# Haetaan lokitiedosto luvun alkurivi (indeksi)
		#log_line_index = self.logfiles.get_line_index(logfile_name)

		# Haetaan alkuajan lokirivin indeksi (nopeuttaa hakemista, jos ei tarvii aina lukea kaikkia rivejä lokin alusta)
		# TÄMÄ EI TOIMI OIKEIN !!!? KORJATTU ? 21.6.2016 Esa
		log_line_index = self.logfiles.search_line_index(logfile_name,start_time)

		# Luetaan lokirivit muistista
		self.log_lines = self.logfiles.get_lines(logfile_name)

		print(" --- ESU: log_line_index = %s" % log_line_index )

		# Haetaan otsikon sarakkeiden nimet ja lukumäärä
		self.log_column_names_list,self.log_column_numbers = self.logfiles.get_header_data(logfile_name)
		
		# Muodostetaan muuttujat
		for column_name in self.log_column_names_list:

			# Poistetaan mahdolliset spacet alusta ja lopusta
			#column_name = column_name.lstrip().rstrip()
			last_read_variables[column_name]=""

		# Käydään lokirivit läpi alkaen tietystä rivistä (indeksistä)
		# Ei saa sisältää otsikko riviä !
		lines_len = len(self.log_lines)
		print(" === lines_len = %s" % lines_len)
		while log_line_index < lines_len:

			#line = self.log_lines[self.log_line_index]
			line_list = self.log_lines[log_line_index]
			line_list_len = len(line_list)

			#print(" === line_list = %s" % line_list)

			log_line_index += 1
			self.logfiles.set_line_index(logfile_name,log_line_index)
		
			self.line_counter += 1
			
			#print("ESU: line_list: %5d: %s" % (self.line_counter,line_list))
			#print("ESU: line_list_len: %d" % (line_list_len))
		
			# Jos rivilla ei ollut sarakkeita saman verran kuin otsikossa,
			# hylätään rivi
			if line_list_len != self.log_column_numbers:
				print(" --- ESU: Number of columns are illegal: %s - %s" % (line_list_len,self.log_column_numbers))
				continue
			
			self.line_sel_counter += 1
			
			# Luetaan rivin sarakkeiden arvot luettujen muuttujiin
			col_index = 0
			for column_name in self.log_column_names_list:
				var_value = line_list[col_index]

				# Poistetaan mahdolliset spacet alusta ja lopusta
				#var_value = var_value.lstrip().rstrip()

				last_read_variables[column_name] = var_value
				#print("ESU: %5d: Var name: %-20s value: \"%s\"" % (col_index,column_name,last_read_variables[column_name]))
				col_index += 1

			timestamp_str = last_read_variables[self.state_log_time_column]
			line_timestamp = datetime.strptime(timestamp_str,"%Y-%m-%d %H:%M:%S")
			
			#print("line_timestamp = %s, start_time = %s, stop_time = %s" % (line_timestamp,start_time,stop_time))

			# Piirretään löydetty tapahtuma GUI:hin
			#if self.gui_enable == 1:
			#	self.draw_event(self.name,line_timestamp,"")

			# Tarkistetaan aikaväli
			if line_timestamp >= start_time:
				if line_timestamp < stop_time:
					self.line_sel_counter += 1
					#print("ESU: Line %s in time-gap: %s -- %s" % (line,ana.variables["START-TIMESTAMP"],ana.variables["STOP-TIMESTAMP"]))
					#print("ESU: Line %s in time-gap: %s -- %s" % (line,start_time,stop_time))
					
					# Piirretään löydetty tapahtuma GUI:hin
					#if self.gui_enable == 1:
					#	self.draw_event(self.name,line_timestamp,"")

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
					
						self.line_found_counter += 1

						# Viimeiset löydetyt muuttujat talteen
						for column_name in self.log_column_names_list:
							self.last_found_variables[column_name] = last_read_variables[column_name]
							#self.last_line = line
							self.last_line = line_list
							self.line_found_timestamp = line_timestamp
					
						# Jos oli ensimmäisen tapahtuman haku
						if state_type_param == "First":
							print("ESU: %s: First event was found" % (self.name))
							print("ESU: line      : \n%s" % (line_list))
							
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

				else:
					# Ei löytynyt aikaväliltä, lopetetaan haku. Ei lueta turhaan loppua !
					print(" *** ESU: Stops searching: stop time is exceeded: %s" % line_timestamp)
					print(" *** ESU: Last line: %s" % line_list)
					#return self.onexit(0)
					break

		print("ESU: line_counter       = %d" % self.line_counter)
		print("ESU: line_found_counter = %d" % self.line_found_counter)
		print("ESU: line_sel_counter   = %d" % self.line_sel_counter)
		
		# Jos oli viimeisen tapahtuman haku
		if state_type_param == "Last":
			if self.line_found_counter == 0:
				return self.onexit(0)
			else:
				
				print("ESU: %s: Last event was found" % (self.name))
				print("ESU: line      : \n%s" % (self.last_line))
				return self.onexit(1)
						
		return self.onexit(0)
		
	def run(self,state_counter,start_time,stop_time,logfile_name,datafile_name,state_log_time_column,
			state_log_variables,state_data_variables,state_position_variables,state_type,output_files_path):


		self.esu_run_counter += 1

		print("")
		print("----------------------------------------------------------------")
		print("ESU: Type: %s" % state_type)
		print("ESU: Name: %s, cnt = %s" % (self.name,self.esu_run_counter))
		print("ESU: Start_time = %s" % (start_time))
		print("ESU: Stop_time  = %s" % (stop_time))
		print("ESU: read orig logfile_name  : %s" % logfile_name)
		if len(datafile_name) > 0:
			print("ESU: read orig datafile_name : %s" % datafile_name)
		
		# Alustetaan Google Earthin kml-tiedosto (vain tarkistusta varten ?!)
		if self.ge_kml_enable == 1:
			self.klm_file_path_name = output_files_path + self.name + "_" + str(state_counter) + ".kml"
			print("ESU: GE kml file_name : %s" % self.klm_file_path_name )
			init_kml_file(self.klm_file_path_name,"","")

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
		
		# Jos haetaan monta samanlaista sarja-tapahtumaa peräkkäin
		ana.variables["INT-SERIAL-FOUND-COUNTER"] = 0
		if state_type_param2 == "Serial":

			try:
				serial_values = ana.variables[state_data_variables]
				#print("serial_values = %s" % serial_values)
			except KeyError:
				print("ESU: ERR: Not found data variable in state: %s" % (self.name))
				return (False)

			serial_vars_list = serial_values.split(",")

			serial_found_cnt = -1

			print("ESU: names of serial areas: %s" % serial_vars_list)
			for serial_var in serial_vars_list:

				print("\nESU: Start to serial search for area:  %5d, %s, start: %s stop: %s --------" % (serial_found_cnt,serial_var,start_time,stop_time))

				state_data_variables = "SERIAL-ID"
				ana.variables["SERIAL-ID"] = serial_var
				ret = self.run_esu_state(state_log_variables,state_data_variables,state_position_variables,
							logfile_name,datafile_name,start_time,stop_time,
							state_type_param,state_type_param2,serial_found_cnt)

				if ret == "Found":
					serial_found_cnt += 1

				if serial_found_cnt > -1:
					start_time = ana.variables["INT-FOUND-TIMESTAMP"]

					# Löydetty sarja-tapahtuma talteen
					ser_var_name = "INT-SERIAL-FOUND-TIMESTAMP-%s" % (serial_found_cnt)
					ana.variables[ser_var_name] = start_time,serial_var

					# Jos jotain seuraavaa sarja-tapahtumaa ei löytynyt, lopetetaan haku,
					# mutta merkitään koko haku löydetyksi (jotta BMU:ssa voidaan piirtää löydetyt tapahtumat)
					if ret == "Not found":
						ret = "Found"
						break	

			# Lopputekstit klm-tiedostoon
			if self.ge_kml_enable == 1:
				finalize_kml_file(self.klm_file_path_name)

			print("## Stops serial searching, found: %s" % serial_found_cnt)

			# Löydettyjen sarja-tapahtumien lukumäärä talteen
			ana.variables["INT-SERIAL-FOUND-COUNTER"] = serial_found_cnt
			return ret

		# Muuten haetaan vain yksi tapahtuma
		else:
			ret =  self.run_esu_state(state_log_variables,state_data_variables,state_position_variables,
							logfile_name,datafile_name,start_time,stop_time,
							state_type_param,state_type_param2,0)

			# Lopputekstit klm-tiedostoon
			if self.ge_kml_enable == 1:
				finalize_kml_file(self.klm_file_path_name)

			return ret
		
	def run_esu_state(self,state_log_variables,state_data_variables,state_position_variables,
					logfile_name,datafile_name,start_time,stop_time,
					state_type_param,state_type_param2,serial_found_cnt):

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
		print("ESU: read logfile_name  : %s" % logfile_name)

		if len(datafile_name) > 0:
			#ret, datafile_name = self.get_variable_value(datafile_name,self.state_data_variables_list)			
			ret, datafile_name = self.get_variable_value(datafile_name,all_variables_list)
			if ret == False:
				print("ESU: ERR: Getting data-variables")
				self.onexit(-1)
			print("ESU: read datafile_name : %s" % datafile_name)
		
			# Luetaan datatiedosto (jos käytössä) ja haetaan sieltä tiedot data-muuttujilla
			ret = self.read_datafile(datafile_name)
			if ret == False:
				print("ESU: WARN: Reading datafile (or it is not exist)")
				self.onexit(-1)
		
		# Luetaan lokitiedosto ja haetaan sieltä tiedot log-muuttujilla halutulla aikavälillä
		return self.read_logfile(logfile_name,start_time,stop_time,state_type_param,state_type_param2,serial_found_cnt)

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
	state_found_metadata = {}
	state_found_serial_metadata = {}
	state_found_serial_metadata_counter = {}
	state_found_counter = 0
	state_event_num = {}
	event_last_stop_timestamp = {}
	bmu_run_counter = 0

	color_list_counter = 0
	color_list = [QColor(255,0,0,127),
				  QColor(0,255,0,127),
				  QColor(0,0,255,127),
				  QColor(255,0,255,127),
				  QColor(0,255,255,127),
				  QColor(0,0,0,127)]

	state_found_counter_array = {}
	state_not_found_counter_array = {}
	state_exit_counter_array = {}
	state_counter_array = {}

	state_counter_array_all = 0
	state_found_counter_array_all = 0
	state_not_found_counter_array_all = 0
	state_exit_counter_array_all = 0

	states_found_id_list = []
	states_not_found_id_list = []
	states_exit_id_list = []

	states_found_id_array = {}
	states_not_found_id_array = {}
	states_exit_id_array = {}

	def __init__(self,name,analyze_file_mode,states,state_order,transition_names,start_state_name,transition,transition_function,
				 state_onentry_function,state_onexit_function,end_state_name,state_logfiles,
				 state_datafiles,state_settings,state_log_time_column,state_log_variables,state_data_variables,
				 state_position_variables,state_type,state_start_time_limit,state_stop_time_limit,
				 gui_enable,gui_seq_draw_mode,ge_kml_enable,gui,state_GUI_line_num,analyzing_mode,output_files_path,
				 logfiles_data):
				 
		self.analyze_file_mode=analyze_file_mode
		#print("self.analyze_file_mode = %s\n" % self.analyze_file_mode)		
		self.name=name
		#print("self.name = %s\n" % self.name)
		self.states=states
		#print("self.states = %s\n" % self.states)
		self.state_order=state_order
		#print("self.state_order = %s\n" % self.state_order)
		self.transition_names=transition_names
		#print("self.transition_names = %s\n" % self.transition_names)
		self.start_state_name=start_state_name
		#print("self.start_state_name = %s\n" % self.start_state_name)
		self.transition=transition
		#print("self.transition = %s\n" % self.transition)
		self.transition_function=transition_function
		#print("self.transition_function = %s\n" % self.transition_function)
		self.state_onentry_function=state_onentry_function
		#print("self.state_onentry_function = %s\n" % self.state_onentry_function)
		self.state_onexit_function=state_onexit_function
		#print("self.state_onexit_function = %s\n" % self.state_onexit_function)
		self.end_state_name=end_state_name
		#print("self.end_state_name = %s\n" % self.end_state_name)
		self.state_logfiles=state_logfiles
		#print("self.state_logfiles = %s\n" % self.state_logfiles)
		self.state_datafiles=state_datafiles
		#print("self.state_datafiles = %s\n" % self.state_datafiles)
		self.state_settings=state_settings
		#print("self.state_settings = %s\n" % self.state_settings)
		self.state_log_time_column=state_log_time_column
		#print("self.state_log_time_column = %s\n" % self.state_log_time_column)
		self.state_log_variables=state_log_variables
		#print("self.state_log_variables = %s\n" % self.state_log_variables)
		self.state_data_variables=state_data_variables
		#print("self.state_data_variables = %s\n" % self.state_data_variables)
		self.state_position_variables=state_position_variables
		#print("self.state_position_variables = %s\n" % self.state_position_variables)
		self.state_type=state_type
		#print("self.state_type = %s\n" % self.state_type)
		self.state_start_time_limit=state_start_time_limit
		#print("self.state_start_time_limit = %s\n" % self.state_start_time_limit)
		self.state_stop_time_limit=state_stop_time_limit
		#print("self.state_stop_time_limit = %s\n" % self.state_stop_time_limit)
		
		self.gui_enable = gui_enable
		#print("self.gui_enable = %s\n" % self.gui_enable)
		self.gui = gui		

		self.state_GUI_line_num = state_GUI_line_num
		#print("self.state_GUI_line_num = %s\n" % self.state_GUI_line_num)

		self.gui_seq_draw_mode = gui_seq_draw_mode
		#print("self.gui_seq_draw_mode = %s\n" % self.gui_seq_draw_mode)

		self.ge_kml_enable = ge_kml_enable
		#print("self.ge_kml_enable = %s\n" % self.ge_kml_enable)

		#print("variables = %s" % variables)
		
		self.variables_list = ana.variables.keys()
		
		self.trace_cnt = 0

		self.analyzing_mode,self.analyzing_col_num = analyzing_mode.split(":")
		print("self.analyzing_mode = %s, col =%s\n" % (self.analyzing_mode,self.analyzing_col_num ))

		self.output_files_path = output_files_path

		self.logfiles_data = logfiles_data

		print("")
		
	def draw_event(self,state_name,offset,timestamp,text,override_mode):
		try:
			new_event_num = self.state_GUI_line_num[state_name]
			#print("      ESU: GUI-line number: %s" % new_event_num)
			self.gui.drawEvent(self.gui.qp,new_event_num,offset,timestamp,text,"circle",override_mode)
		except:
			print("BMU: ERR: Not found state: \"%s\" for GUI-line" % (state_name))

	def drawEventSequence(self):

		#print(" ******* drawEventSequence: trace-counter: %s" % self.trace_cnt)

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
		# Jos GUI:n mukaisessa järjestyksessä
		elif self.gui_seq_draw_mode == "order":
			sorted_state_list = sorted(self.state_found_metadata.keys(), 
				key=lambda tila: self.state_found_metadata[tila][2])
			#print("  Time-order: %s" % sorted_state_list)
		# Muuten, hakujärjestyksessä "search"
		else:
			sorted_state_list = sorted(self.state_found_metadata.keys(), 
				key=lambda tila: self.state_found_metadata[tila][1])
			#print("  Search-order: %s" % sorted_state_list)

		# Lasketaan sekvenssin tietoja COMPARE-modea varten
		for state_name in sorted_state_list:
			#state_time,state_order = self.state_found_metadata[state_name]	
			state_time,state_order,state_gui_order = self.state_found_metadata[state_name]	

			# Referenssiaika talteen COMPARE-modea (kun piirretään tracet päällekkäin) varten
			# Määritetään mitä saraketta käytetään refenenssinä
			if state_cnt == int(self.analyzing_col_num):
				if self.trace_cnt == 0:
					self.gui.setReferenceTime(state_time,state_cnt)
				self.gui.setTraceReferenceTime(state_time)
			state_cnt += 1

		state_cnt = 0

		# Piirretään sekvenssi
		for state_name in sorted_state_list:
			#state_time = self.state_found_time[state_name]

			# Luetaan tilan metadata: aika ja suoritusjärjestys
			#state_time,state_order = self.state_found_metadata[state_name]
			state_time,state_order,state_gui_order = self.state_found_metadata[state_name]

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

				# Jos tilassa sarjahaun tuloksia, piirretään niiden linkit tähän väliin
				state_ser_counter = self.state_found_serial_metadata_counter[state_name]

				if state_ser_counter > 0:
					print("drawEventSequence: state: %s ser_counter: %s" % (state_name,state_ser_counter))
					old_ser_time = old_time
					old_ser_offset = 0
					old_ser_event_num = old_event_num 
					new_ser_event_num = new_event_num 
					for i in range(state_ser_counter):

						new_ser_time,ser_name,ind = self.state_found_serial_metadata[state_name,i]

						new_ser_offset = i * 40
						#print("drawEventSequence: ser_time_found: %s, ind: %s" % (new_ser_time,ind))
						
						event_str = ""
						if i == 0:
							event_str = str(new_ser_time)
						self.draw_event(state_name,new_ser_offset,new_ser_time,event_str,0)

						self.gui.drawTraceLine(self.gui.qp,old_ser_event_num,old_ser_offset,old_ser_time,
												new_ser_event_num,new_ser_offset,new_ser_time,color)

						self.gui.drawVerticalLine(self.gui.qp,int(new_ser_event_num),new_ser_offset,1)
						ser_str = str(i+1) + "." 
						self.gui.drawVerticalText(self.gui.qp,int(new_ser_event_num),new_ser_offset,ser_str,22)
						ser_str = ser_name
						self.gui.drawVerticalText(self.gui.qp,int(new_ser_event_num),new_ser_offset,ser_str,10)

						old_ser_time = new_ser_time
						old_ser_offset = new_ser_offset
						old_ser_event_num = new_ser_event_num 

					#self.gui.drawVerticalLine(self.gui.qp,int(new_ser_event_num),new_ser_offset,"SERIAL STOP",2)

					#self.gui.drawTraceLine(self.gui.qp,old_ser_event_num,old_ser_offset,old_ser_time,
					#					new_event_num,0,new_time,color)
					#self.draw_event(state_name,0,new_time,str(new_time))
					#self.draw_event(state_name,new_ser_offset,new_ser_time,"",1)

				# Muuten piirretään vain yksi linkki
				else:					
					self.gui.drawTraceLine(self.gui.qp,old_event_num,0,old_time,
										new_event_num,0,new_time,color)

			#else:
			
			#self.draw_event(state_name,0,new_time,str(new_time),0)
			self.draw_event(state_name,0,new_time,str(self.trace_cnt+1),0)

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

		event_offset = 1
		if line_num in self.event_last_stop_timestamp.keys():

			event_offset,last_stop_time = self.event_last_stop_timestamp[line_num]
			#print("  event_offset=%s, last_stop=%s, timestamp=%s" % (event_offset,last_stop_time,timestamp_start))

			if timestamp_start < last_stop_time:
				event_offset += 1
				if event_offset > 10:
					event_offset = 1
		
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
					#print("var_name = %s, var_value = %s" % (var_name,var_value))
					
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
		
		#print("time_limit_str_with_values = %s" % time_limit_str_with_values)
		
		time_limit_list = time_limit_str_with_values.split(",")
		time_limit_list_len = len(time_limit_list)
		
		if time_limit_list_len == 2:
		
			time_value_str = time_limit_list[0]
			
			# Pitää muuttaa stringistä takaisin datetime-muotoon, että voidaan laskea
			time_value_str = time_value_str[:19]
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
		
		self.bmu_run_counter += 1
		print("bmu_run_counter = %s" % self.bmu_run_counter)

		# Luodaan tilat ja tehdään niistä taulukko, johon viitataan tilan nimellä
		for state in self.states:
			self.state_array[state] = ESU(state,self.logfiles_data,self.gui_enable,self.gui,self.state_GUI_line_num,self.ge_kml_enable)
			#print("BMU: ESU: %s : %s" % (state,self.state_array[state]))

			# Nollataan myös tilakohtaiset tuloslaskurit
			self.state_found_counter_array[state] = 0
			self.state_not_found_counter_array[state] = 0
			self.state_exit_counter_array[state] = 0
			self.state_counter_array[state] = 0
			
		# Nollataan yleiset laskurit
		self.state_counter_array_all = 0
		self.state_found_counter_array_all = 0
		self.state_not_found_counter_array_all = 0
		self.state_exit_counter_array_all = 0

		# Nollataan tilojen paluuarvojen ID-listat
		self.states_found_id_list = []
		self.states_not_found_id_list = []
		self.states_exit_id_list = []

		# Nollataan tilojen tilakohtaiset paluuarvojen ID-listat
		self.states_found_id_array = {}
		self.states_not_found_id_array = {}
		self.states_exit_id_array = {}

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
						self.state_found_serial_metadata = {}
						self.state_found_serial_metadata_counter = {}

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
						self.state_found_serial_metadata = {}
						self.state_found_serial_metadata_counter = {}

						# Tulostetaan tämänhetkiset muuttujat ja niiden arvot
						#self.print_variables()

					# Seuraava piirtoväri listalta
					self.color_list_counter += 1
					if self.color_list_counter >= len(self.color_list):
						self.color_list_counter = 0

					print("  color_list_counter = %s" % self.color_list_counter)

				# Tilan olio
				new_esu_state = self.state_array[self.current_state_name]

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
				#print("\nBMU: start_time = %s stop_time = %s" % (self.start_time,self.stop_time))
				
				# Piiretään GUI:hin aikaraja-janat
				if self.gui_enable == 1:
					self.draw_timelimits(self.current_state_name,self.start_time,self.stop_time)

				# Käynnistetään ESU-tila
				ret = new_esu_state.run(self.state_counter,
									self.start_time,
									self.stop_time,
									logfile_name,
									datafile_name,
									state_log_time_column,
									state_log_variables,
									state_data_variables,
									state_position_variables,
									state_type,
									self.output_files_path)
							
				print("\n---------------------------------------------------------------------------")	

				# Tilan mahdollisen onexit-funktion haku ja ajo tilan ajon jälkeen
				try:
					onexit_function_name = self.state_onexit_function[self.current_state_name]
					if len(onexit_function_name) > 0:
						print("BMU: Found new onexit-function: %s" % (onexit_function_name))

						# Ajetaan funktio
						self.run_function(onexit_function_name)
						
				except KeyError:
					print("BMU: No onexit_function for state: %s" % self.current_state_name)
					
				print("BMU: ESU: %s return: %s" % (self.current_state_name,ret))

				if ret == "Found":

					self.state_found_counter += 1
					time_found = ana.variables["INT-FOUND-TIMESTAMP"]
					self.state_found_serial_metadata_counter[self.current_state_name] = 0

					# Huom! sarjahaku piirretään vaikka tulisi "Not found"
					# Jos käytetty sarjahakua ja myös löydetty tapahtumia
					serial_found_cnt = int(ana.variables["INT-SERIAL-FOUND-COUNTER"])
					if serial_found_cnt > 0:

						for i in range(serial_found_cnt):
							ser_var_name = "INT-SERIAL-FOUND-TIMESTAMP-%s" % (i)
							ser_time_found,ser_name = ana.variables[ser_var_name]
							self.state_found_serial_metadata[self.current_state_name,i] = ser_time_found,ser_name,i
							time_found = ser_time_found

						self.state_found_serial_metadata_counter[self.current_state_name] = serial_found_cnt

					#self.state_found_metadata[self.current_state_name] = time_found,self.state_found_counter
					state_gui_order = self.state_GUI_line_num[self.current_state_name]
					self.state_found_metadata[self.current_state_name] = time_found,self.state_found_counter,state_gui_order

				# Päivitetään tämänhetken tilanne lopputuloksiin
				self.update_results(ret,self.current_state_name)

			except KeyError:
				print("BMU: ERR: Not found transitions for state: %s" % self.current_state_name)
				return 0

	def update_results(self,ret,state_name):

		self.state_counter_array_all += 1
		self.state_counter_array[state_name] += 1

		if ret == "Found":
			self.state_found_counter_array[state_name] += 1
			self.state_found_counter_array_all += 1

			# Lisätään tilan ID (järjestysnumero) listaan
			self.states_found_id_list.append(self.state_counter_array_all)
			self.states_found_id_array.setdefault(state_name,list()).append(self.state_counter_array_all)


		if ret == "Not found":
			self.state_not_found_counter_array[state_name] += 1
			self.state_not_found_counter_array_all += 1

			# Lisätään tilan ID (järjestysnumero) listaan
			self.states_not_found_id_list.append(self.state_counter_array_all)
			self.states_not_found_id_array.setdefault(state_name,list()).append(self.state_counter_array_all)

		if ret == "Exit":
			self.state_exit_counter_array[state_name] += 1
			self.state_exit_counter_array_all += 1

			# Lisätään tilan ID (järjestysnumero) listaan
			self.states_exit_id_list.append(self.state_counter_array_all)
			self.states_exit_id_array.setdefault(state_name,list()).append(self.state_counter_array_all)

		print("\n#### BMU Counters: State: %10s, F =%4d, N =%4d, E =%4d | A =%4d (ID=%d)\n" % (state_name,
			self.state_found_counter_array[state_name],
			self.state_not_found_counter_array[state_name],
			self.state_exit_counter_array[state_name],
			self.state_counter_array[state_name],
			self.state_counter_array_all))


	def stop(self):	

		print("")
		print("#### -----------------------------------------------------------------------------")

		# Tulostetaan lopputulksia ja poistetaan ESU-tilat
		for state in self.states:

			print("#### BMU Counters: State: %-20s F =%4d, N =%4d, E =%4d | A =%4d" % (state,
				self.state_found_counter_array[state],
				self.state_not_found_counter_array[state],
				self.state_exit_counter_array[state],
				self.state_counter_array[state]))

			del self.state_array[state]

		print("#### -----------------------------------------------------------------------------")
		print("#### BMU Counters: State: %-20s F =%4d, N =%4d, E =%4d | A =%4d" % ("All",
			self.state_found_counter_array_all,
			self.state_not_found_counter_array_all,
			self.state_exit_counter_array_all,
			self.state_counter_array_all ))

		#print("States IDs:")
		#print(" Found     : %s" % self.states_found_id_list) 
		#print(" Not found : %s" % self.states_not_found_id_list) 
		#print(" Exit      : %s" % self.states_exit_id_list) 

		print("\n#### States \"Found\" IDs:")
		for state in self.states_found_id_array.keys():
			print("  %-20s: %s" % (state,self.states_found_id_array[state]))
		print("#### States \"Not found\" IDs:")
		for state in self.states_not_found_id_array.keys():
			print("  %-20s: %s" % (state,self.states_not_found_id_array[state]))
		print("#### States \"Exit\" IDs:")
		for state in self.states_exit_id_array.keys():
			print("  %-20s: %s" % (state,self.states_exit_id_array[state]))


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
	global analyze_run_counter
	#global legal_state_types

	analyze_run_counter += 1
	print("\n ~~~ analyze_run_counter = %s\n" % analyze_run_counter)

	start_time = time.time()

	# Alustetaan lokitiedostojen data (muistissa)
	logfiles_data = LogFilesData()

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
						args.ge_kml_enable,
						gui,
						ana.state_GUI_line_num,
						args.analyzing_mode,
						args.output_files_path,
						logfiles_data)

	print("SM name = %s" % SM.name)

	# Käynnistetään tilakone ja ajetaan analysoinnit
	SM.run()	

	# Pysäytetään tilakone
	SM.stop()	
	del SM

	print("\n ~~~ analyze_run_counter = %s\n" % analyze_run_counter)
	print("Total execution time: %.3f seconds\n" % (time.time() - start_time))

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
		
		file_name = ana.state_datafiles[state_datafile_name]
		if len(file_name) > 0:
			#ana.state_datafiles[state_datafile_name] = args.input_ssd_path + ana.state_datafiles[state_datafile_name]
			ana.state_datafiles[state_datafile_name] = args.input_ssd_path + file_name
		else:
			ana.state_datafiles[state_datafile_name] = ""

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
	parser.add_argument('-ge_kml_enable','--ge_kml_enable', dest='ge_kml_enable', type=int, help='ge_kml_enable')

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
	print("ge_kml_enable     : %s" % args.ge_kml_enable)
	print("\n")

	#sys.exit()

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
		gui2 = GUI_AnalyzeArea(args,"LOGDIG: TRACES OF LOGS",analyze_area_x,analyze_area_y,1100,1000,0,0,1.0,
				analyze_logs,ana.state_GUI_line_num)

		sys.exit(app.exec_())

	else:
		analyze_logs(args,"","Ana","")

	print("\n Total execution time: %.3f seconds" % (time.time() - start_time))

if __name__ == '__main__':
    main()