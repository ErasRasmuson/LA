# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	LogFilesData.py    

AUTHOR:     Esa Heikkinen
DATE:       04.07.2018
DOCUMENT:   - 
VERSION:    "$Id$"
REFERENCES: -
PURPOSE:    
CHANGES:    "$Log$"
###############################################################################
"""

import os.path
import os
import psutil
import sys
import time
import re
from datetime import datetime

# Luokka siirretty tahan tiedostoon LogDig.py:sta

#******************************************************************************
#       
#	CLASS:	LogFilesData
#
#******************************************************************************
class LogFilesData:

	logfile_already_read = {}
	logfile_lines = {}
	logfile_type = {} # UNKONWN, DIRECT or INDIRECT, 5.7.2018 Esa
	logfile_indirect_file = {} # 5.7.2018 Esa
	logline_index = {}
	logline_times = {}
	log_column_names_list = {}
	log_column_numbers = {}
	log_data_line_counter = {}
	logfile_keyby_line_indices = {}

	def __init__(self):
		print(" >>>> LogFilesData: init")
		self.logfile_already_read = {}

	# Muutettu aika paljon 5.7.2018 Esa
	def read(self,logfile_name,time_column):

		start_time = time.time()

		# Tarkistetaan onko loki jo luettu (muistiin)
		log_already_read = 0
		try:
			log_already_read = self.logfile_already_read[logfile_name]
			log_type = self.logfile_type[logfile_name]
		except:
			log_already_read = 0
			log_type = "UNKNOWN"

		print("\n >>>> LogFilesData read: log_already_read = %s, type = %s" % (log_already_read,log_type))

		if log_already_read == 0 and log_type != "INDIRECT":

			time_column_index = 0

			if os.path.isfile(logfile_name):

				print(" >>>> LogFilesData read: logfile: %s" % (logfile_name))
				process = psutil.Process(os.getpid())
				memory_usage_before = process.memory_info().rss
				print(" >>>> LogFilesData read: memory usage before: %s bytes" % memory_usage_before)
				print(" >>>> LogFilesData read: file size: %s bytes" % os.path.getsize(logfile_name))

				self.logfile_lines[logfile_name] = []
				log_lines = []
				f = open(logfile_name, 'r')
				log_lines = f.readlines()
				f.close()

				file_line_counter = 0
				line_counter = 0
				self.log_data_line_counter[logfile_name] = 0

				# Esa 28.6.2018
				line_timestamp_old = 0
				same_time_counter = 0

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
						print(" >>>> LogFilesData read: time column: %s index = %s" % (time_column,time_column_index))

						# Ei käydä enempää rivejä läpi ?
						#break

					# Muut rivit, haetaan aikaleimat riveille, jotta "takaisinpäin hakeminen"
					# on myöhemmin helppoa ja nopeaa.
					else:

						timestamp_str = line_list[time_column_index]
						line_timestamp = datetime.strptime(timestamp_str,"%Y-%m-%d %H:%M:%S")

						# Lasketaan samat perakkaiset aikaleimat. Esa 28.6.2018
						if line_timestamp_old != line_timestamp:
							same_time_counter = 0
						else:
							same_time_counter += 1
						line_timestamp_old = line_timestamp

						# Otetaan rivien aikaleimat talteen. Vai pitäisikö käyttää alkup. tiedoston logfile_lines-taulukkoa ?
						#self.logline_times[logfile_name,self.log_data_line_counter[logfile_name]] = line_timestamp

						# Esa 28.6.2018
						self.logline_times[logfile_name,self.log_data_line_counter[logfile_name]] = (line_timestamp,same_time_counter)
						#print(" >>>> cnt = %s, time = %s, cnt = %d" % (self.log_data_line_counter[logfile_name],line_timestamp,same_time_counter))

						self.log_data_line_counter[logfile_name] += 1

						self.logfile_lines[logfile_name].append(line_list)

				#self.logfile_lines[logfile_name] = log_lines

				self.logline_index[logfile_name] = 0
				self.logfile_type[logfile_name] = "DIRECT" # 5.7.2018 Esa

				print(" >>>> LogFilesData read: file_line_counter = %s, line_counter = %s" % (file_line_counter,line_counter))

				# Merkitään loki luetuksi (että myöhemmin ei tarvise lukea tiedostosta uudestaan)
				self.logfile_already_read[logfile_name] = 1

				memory_usage_after = process.memory_info().rss
				print(" >>>> LogFilesData read: memory usage after: %s, diff: %s bytes" %
					  (memory_usage_after,memory_usage_after-memory_usage_before))
				print(" >>>> LogFilesData read: Execution time: %.3f seconds\n" % (time.time() - start_time))

				return False,True
			else:
				print(" >>>> LogFilesData read: Not found logfile: %s" % logfile_name)
				return True,False

		return False,False

	# Muutettu 5.7.2018 Esa
	def get_lines(self,logfile_name):

		#print(" >>>> LogFilesData: get_lines: Logfile: %s" % (logfile_name))

		log_lines = []

		try:
			log_type = self.logfile_type[logfile_name]
			print(" >>>> LogFilesData: get_lines: Type: %s for logfile: %s" % (log_type,logfile_name))
		except:
			print(" >>>> LogFilesData: get_lines: ERR: Not found type for: %s" % logfile_name)
			return log_lines

		if log_type == "INDIRECT":
			# Alkuperainen tiedosto
			indirect_logfile_name = self.logfile_indirect_file[logfile_name]

			# Kopiodaan otsikotiedot alkuperaisesta
			self.log_column_names_list[logfile_name] = self.log_column_names_list[indirect_logfile_name]
			self.log_column_numbers[logfile_name] = self.log_column_numbers[indirect_logfile_name]

			# Kopioidaan data alkuperaisesta
			#print(" >>>> LogFilesData: get_lines: indirect_logfile_name: %s" % indirect_logfile_name)
			line_cnt = 0
			for line_num in self.logfile_keyby_line_indices[logfile_name]:
				#print(" >>>> LogFilesData: get_lines: line_num: %s" % line_num)
				line_list = self.logfile_lines[indirect_logfile_name][line_num]
				#print(" >>>> LogFilesData: get_lines: line: %s" % line_list)
				log_lines.append(line_list)

				# Myos aikaleima alkuperaisesta, ei toimi
				#self.logline_times[logfile_name,line_cnt] = self.logline_times[indirect_logfile_name,line_num]
				#line_cnt += 1

		else:
			try:
				log_lines = self.logfile_lines[logfile_name]
			except:
				print(" >>>> LogFilesData: get_lines: ERR: Not found log lines for: %s" % logfile_name)

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
			#current_line_timestamp = self.logline_times[logfile_name,current_line_index]
			# Esa 28.6.2018
			(current_line_timestamp,same_time_counter) = self.logline_times[logfile_name,current_line_index]
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

				#new_line_timestamp = self.logline_times[logfile_name,index]
				# Esa 28.6.2018
				(new_line_timestamp,same_time_counter) = self.logline_times[logfile_name,index]
				#print(" >>> index = %s, new_line_timestamp = %s, same_time_cnt = %d" % (index,new_line_timestamp,same_time_counter))
				#if new_line_timestamp <= start_time:

				# Toimiiko INDIRECT-lokeilla ??
				#if new_line_timestamp <= start_time and same_time_counter == 0:
				
				# 29.11.2018 Esa. Toimii myos, jos taytyy peruuttaa tiedoston ensimmaiseen riviin asti.
				if index == 0 or (new_line_timestamp <= start_time and same_time_counter == 0):

					print(" >>>> LogFilesData: search_line_index: Backward: cur_ind=%s, cur_time=%s, new_ind=%s, new_time=%s, same_time_cnt=%s, search_count=%s" %
							(current_line_index,current_line_timestamp,index,new_line_timestamp,same_time_counter,search_count))

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

	# 5.7.2018 Esa
	def transform_operation_keyby(self,logfile_name,keyby_column):

		print("\n >>>> transform_operation_keyby: logfile_name = %s" % logfile_name)

		start_time = time.time()

		process = psutil.Process(os.getpid())
		memory_usage_before = process.memory_info().rss
		print(" >>>> transform_operation_keyby: memory usage before: %s bytes" % memory_usage_before)

		log_line_counter = 0
		try:
			logfile_lines = self.logfile_lines[logfile_name]
			log_line_counter = self.log_data_line_counter[logfile_name]

			col_name_list = self.log_column_names_list[logfile_name] 
			#line_list_len = self.log_column_numbers[logfile_name]

			keyby_column_index = col_name_list.index(keyby_column)

		except:
			print(" >>>> transform_operation_keyby: ERR: Reading lines from: %s" % logfile_name)
			return False

		print(" >>>> transform_operation_keyby: is starting, lines=%s" % log_line_counter)

		#sys.exit(1)	

		log_keyby_values = {}
		keyby_logfile_name = ""
		for log_line_index in range(1,log_line_counter):
			line_list = logfile_lines[log_line_index]
			keyby_col_value = line_list[keyby_column_index]

			#print(" >>>> transform_operation_keyby: keyby_col_value = %s" % keyby_col_value)

			keyby_logfile_name = "%s_%s" % (logfile_name,keyby_col_value) 

			# Lasketaan keyby-sarakkeiden arvot ja tehdaan lista niista
			try:
				log_keyby_values[keyby_col_value] += 1
			except:
				log_keyby_values[keyby_col_value] = 1
				self.logfile_keyby_line_indices[keyby_logfile_name] = []
				#print(" >>>> transform_operation_keyby: keyby_logfile_name = %s" % keyby_logfile_name)

				# Merkitaan luetuksi, koska tiedostot generoidaan suoraan muistiin
				self.logfile_already_read[keyby_logfile_name] = 1

				self.logfile_type[keyby_logfile_name] = "INDIRECT"
				self.logfile_indirect_file[keyby_logfile_name] = logfile_name
				self.logline_index[keyby_logfile_name] = 0

			# Aikaleima kopioidaan jo tassa vaiheessa
			self.logline_times[keyby_logfile_name,log_keyby_values[keyby_col_value] - 1] = \
				self.logline_times[logfile_name,log_line_index]

			# keyby-tiedoston rivien maara
			self.log_data_line_counter[keyby_logfile_name] = log_keyby_values[keyby_col_value]

			# Muodostetaan keyby-sarakkeiden "tiedostot" (muistiin) viittauksina alkuperaiseen tiedostoon
			self.logfile_keyby_line_indices[keyby_logfile_name].append(log_line_index)
			#print(" >>>> transform_operation_keyby: keyby_logfile_name = %s, indices = %s" %
				# (keyby_logfile_name,self.logfile_keyby_line_indices[keyby_logfile_name]))

		keyby_values_len = len(log_keyby_values.keys())
		print(" >>>> transform_operation_keyby: is done, found %s keys " % keyby_values_len)

		#sys.exit(1)	

		# Tulostetaan loydetyt keyby-sarakkeen arvot ja niiden tiedot
		"""
		print(" >>>> transform_operation_keyby: keyby values for column: %s" % keyby_column)	
		cnt = 0
		for keyby_value in sorted(log_keyby_values.keys()):
			cnt += 1
			keyby_value_cnt = log_keyby_values[keyby_value]
			print(" >>>> transform_operation_keyby: %5d, %s: %s" % (cnt,keyby_value,keyby_value_cnt))

		print("\n >>>> transform_operation_keyby: logfile_keyby_line_indices")	
		cnt = 0
		for logfile_keyby in sorted(self.logfile_keyby_line_indices.keys()):
			cnt += 1
			keyby_line_indices = self.logfile_keyby_line_indices[logfile_keyby]
			print(" >>>> transform_operation_keyby: %5d, %s: %s" % (cnt,logfile_keyby,keyby_line_indices))
		"""
		#sys.exit(1)

		memory_usage_after = process.memory_info().rss
		print(" >>>> transform_operation_keyby: memory usage after: %s, diff: %s bytes" %
			  (memory_usage_after,memory_usage_after-memory_usage_before))
		print(" >>>> transform_operation_keyby: Execution time: %.3f seconds\n" % (time.time() - start_time))

		return True
