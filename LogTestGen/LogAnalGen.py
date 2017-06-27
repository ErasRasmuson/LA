# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	LogAnalGen.py

AUTHOR:     Esa Heikkinen
DATE:       13.1.2017
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
from datetime import datetime, timedelta
import glob
import math
import random
import configparser

lib_path = os.path.abspath(os.path.join('..', 'LogCom'))
sys.path.append(lib_path)
#from LogGUI import *
from TestGen_BML import *

g_version = "$Id$"
generate_counter = 0

#******************************************************************************
#
#	CLASS:	TestModel
#
#******************************************************************************
class TestModel:

	def __init__(self,args):
		print("TestModel")

		self.branch_complexity_level_params = {}
		self.trace_size_variation_level_params = {}
		self.branch_complexity_level_number = 3
		self.trace_size_variation_level_number = 3

		self.trace_blocks = {}
		self.event_table = {}

		self.test_name=args.test_name
		self.ana_path=args.ana_path
		self.ana_lang=args.ana_lang
		#self.log_path=args.log_path
		#self.date
		self.time_start=args.time_start
		self.time_ev_min=args.time_ev_min
		self.time_ev_max=args.time_ev_max

		self.branch_complexity_level_params[0] = self.Branch_complexity_params(args.b1_btre_min,args.b1_btre_max,
			args.b0_bmer_min,args.b0_bmer_max,args.b0_bctype)
		self.branch_complexity_level_params[1] = self.Branch_complexity_params(args.b2_btre_min,args.b2_btre_max,
			args.b0_bmer_min,args.b0_bmer_max,args.b0_bctype)
		self.branch_complexity_level_params[2] = self.Branch_complexity_params(args.b2_btre_min,args.b2_btre_max,
			args.b3_bmer_min,args.b3_bmer_max,args.b2_bctype)

		self.trace_size_variation_level_params[0] = self.Trace_size_variation_params(args.t1_tle_min,args.t1_tle_max,
			args.t0_tnu_min,args.t0_tnu_max,args.t1_tble_min,args.t1_tble_max,args.t0_tbnu_min,args.t0_tbnu_max)
		self.trace_size_variation_level_params[1] = self.Trace_size_variation_params(args.t2_tle_min,args.t2_tle_max,
			args.t0_tnu_min,args.t0_tnu_max,args.t2_tble_min,args.t2_tble_max,args.t0_tbnu_min,args.t0_tbnu_max)
		self.trace_size_variation_level_params[2] = self.Trace_size_variation_params(args.t2_tle_min,args.t2_tle_max,
			args.t3_tnu_min,args.t3_tnu_max,args.t2_tble_min,args.t2_tble_max,args.t3_tbnu_min,args.t3_tbnu_max)

		# Luodaan testi matriisi
		self.test_matrix = self.TestMatrix(
			self.branch_complexity_level_number,
			self.trace_size_variation_level_number,
			self.branch_complexity_level_params,
			self.trace_size_variation_level_params)

		# Luodaan lokitiedostojen tiedot
		#self.log_files = self.LogFiles(args.lver,args.lsnoe,args.lsnof,args.lcnoi,args.lcmis,args.lcinc,args.lsrc,args.lmeta)


	def generate_analyzing(self):
		print("\ngenerate_analyzing\n")

		for x in range(int(self.branch_complexity_level_number)):
			for y in range(int(self.trace_size_variation_level_number)): 

				(btre_min,btre_max,bmer_min,bmer_max,bctype) = self.test_matrix.test_pattern_blocks[x,y].b_parameters
				(tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max) = self.test_matrix.test_pattern_blocks[x,y].t_parameters

				# Luodaan kaksiulottoinen event-taulukko, jossa trackit X-akselilla ja (main)tracet y-akselilla
				self.create_trace_pattern("Analyzing",btre_min,btre_max,bmer_min,bmer_max,bctype,
									tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max)

				# Tulostetaan trace pattern graafina
				file_info = "matrix_%s_%s" % (x,y)
				self.print_trace_pattern(tble_max,tbnu_max,tle_max,tnu_max,btre_max,file_info)

				# Generoidaan testitapaukset halutulla analysointikielellä
				self.generate_analyzing_test_cases(x,y,btre_min,btre_max,bmer_min,bmer_max,bctype,
								 tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max,
								 self.event_table)

	def generate_analyzing_test_cases(self,matrix_x,matrix_y,btre_min,btre_max,bmer_min,bmer_max,bctype,
						 tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max,
					     event_table):

		print("\n -- generate_analyzing_test_cases for matrix: x=%s, y=%s -- " % (matrix_x,matrix_y))

		# Alustetaan analyysi-tiedostot KESKEN !!!
		#ana_file_name = "Ana_%s_%s_%s" % (self.test_name,matrix_x,matrix_y)
		#if self.ana_lang == "BML":
		#	ana_file_path_name = self.ana_path + self.test_name + "/" + ana_file_name + ".bml"
		#	print("write_file: %s" % login_file_path_name)

		#self.make_dir_if_no_exist(ana_file_path_name)
		#ana_fw = open(ana_file_path_name, 'w')
		#init_analy_file(ana_fw)

		self.event_count=0

		# Lasketaan trace patternin x,y maksimikoko
		track_max = tble_max * tle_max
		event_max = tbnu_max * tnu_max * btre_max

		# Käydään läpi jokainen merged-haara
		for bmer_cnt in range(bmer_max):

			event_track=0
			event_number=bmer_cnt

			# Rekusrsiivinen funktio, jolla haetaan kaikkien tree-haarojen eventit
			self.search_next_event(track_max,event_track,event_number)

		print("\n")

	def search_next_event(self,track_max,event_track,event_number):

		print(" *** track_max=%s, event_track=%s, event_number=%s, event_cnt=%s" % (track_max,event_track,event_number,self.event_count))

		if int(event_track) < track_max:

			event_data = self.get_event_data(int(event_track),int(event_number))
			#print(" *** event_data = %s" % event_data)

			# Generoidaan testitapauksen eventti halutulla kielellä
			if self.ana_lang == "BML":
				generate_BML_test_case_event(self.event_count,event_data,
							self.time_start,self.time_ev_min,self.time_ev_max)

			if event_data[0] == 1:
				# Käydään tree-haaran kaikki eventit läpi
				for target in event_data[5]:
					track,number = target.split(".")
					self.event_count += 1
					self.search_next_event(track_max,track,number)
			else:
				print(" *** Not found event!")
				return
		else:
			print(" *** Last track: %s, stops searching" % event_track)
			return


	def get_event_data(self,track,number):

		x=track
		y=number
		time=""
		attr=""
		data=""
		sources = []
		targets = []

		# Event ja sen tiedot
		try:
			#track2 = self.event_table[x,y].event_id.track
			#number2 = self.event_table[x,y].event_id.id
			time = self.event_table[x,y].time
			attr = self.event_table[x,y].attr
			data = self.event_table[x,y].data
			for i in range(1,self.event_table[x,y].source_id_cnt+1):
				str = "%s.%s" % (self.event_table[x,y].source_ids[i].track,
								self.event_table[x,y].source_ids[i].id)
				sources.append(str)
			for i in range(1,self.event_table[x,y].target_id_cnt+1):
				str = "%s.%s" % (self.event_table[x,y].target_ids[i].track,
								self.event_table[x,y].target_ids[i].id)
				targets.append(str)
			#print("Found: x=%s ,y=%s" % (x,y))
			ret = 1

		except:
			print("Not found: x=%s ,y=%s" % (x,y))
			ret = 0

		return [ret,time,attr,data,sources,targets]

	def create_trace_pattern(self,mode,btre_min,btre_max,bmer_min,bmer_max,bctype,
							tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max):

		self.trace_blocks = {}
		self.event_table = {}

		print("create_event_table: %s" % mode)
		print("tble_min=%s,tble_max=%s,tbnu_min=%s,tbnu_max=%s,tle_min=%s,tle_max=%s,tnu_min=%s,tnu_max=%s" % 
			(tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max))	
		print("btre_min=%s,btre_max=%s,bmer_min=%s,bmer_max=%s,bctype=%s" % 
			(btre_min,btre_max,bmer_min,bmer_max,bctype))

		# Event-taulukko, jossa trackit x-akselilla ja (main)tracet y-akselilla
		for x in range(tble_max):
			print("\n ### Trace block x: %s / %s ----------------------------------- " % (x,tble_max-1))
			for y in range(tbnu_max):
				print("\n ### Trace block y: %s / %s ----------------------------------- " % (y,tbnu_max-1))
				self.trace_blocks[x,y]=self.TraceBlock(x,y,tle_min,tle_max,tnu_min,tnu_max,
					btre_min,btre_max,bmer_min,bmer_max,self.event_table,self.time_ev_max)

		# Tehdään horisontaalisten blockien väliset event-liitokset event-taulukkoon ?
		if tble_max > 1:
			print("\nConnect horizontal traceblocks -- ")
			for x in range(1,tble_max):
				x_prev = x - 1
				prev_outputs = []
				curr_inputs = []

				for y in range(tbnu_max):
					print("x_prev=%s ,x=%s ,y=%s" % (x_prev,x,y))
					if bctype == "All":
						prev_outputs.extend(self.trace_blocks[x_prev,y].get_output_events("A"))
					else:
						prev_outputs.extend(self.trace_blocks[x_prev,y].get_output_events("M"))

					curr_inputs.extend(self.trace_blocks[x,y].get_input_events())

				curr_input_len = len(curr_inputs)
				curr_input_cnt=0

				for event in prev_outputs:

					curr_track=curr_inputs[curr_input_cnt].event_id.track
					curr_id=curr_inputs[curr_input_cnt].event_id.id
					curr_time=curr_inputs[curr_input_cnt].time

					print("Event: %s.%s, Time: %s --> %s.%s, Time: %s" % (
						event.event_id.track,event.event_id.id,event.time,
						curr_track,curr_id,curr_time))

					# Kytketään eventit
					self.event_table[curr_track,curr_id].add_source_id(event.event_id.track,event.event_id.id)
					# Myös toisin päin (helpottaa testianalysointien generointia ?)
					self.event_table[event.event_id.track,event.event_id.id].add_target_id(curr_track,curr_id)

					curr_input_cnt+=1
					if curr_input_cnt >= curr_input_len:
						break

	def print_trace_pattern(self,tble_max,tbnu_max,tle_max,tnu_max,btre_max,file_info):

		# http://www.graphviz.org/content/switch
		
		print("\nprint_trace_pattern -- ")

		# Lasketaan trace patternin x,y maksimikoko
		x_max = tble_max * tle_max
		y_max = tbnu_max * tnu_max * btre_max

		print (" x_max=%s ,y_max=%s" % (x_max,y_max))

		# Graphviz-tiedosto, johon tulostetaan graafit (tracet) visuaalisesti
		graphviz_file = "LogTestGen_%s_%s.gv" % (self.test_name,file_info)
		print("write_file: %s" % graphviz_file)
		fw = open(graphviz_file, 'w')
		fw.write("digraph G {\n")		
		fw.write("\tgraph [center=1 rankdir=LR bgcolor=\"#E0E0E0\"]\n")
		#fw.write("\tedge [dir=none]\n")
		#fw.write("\tnode [width=0.1 height=0.1 label=\"\"]\n")
		fw.write("\tnode [width=0.05 height=0.05]\n")
		fw.write("\n")

		# Käydään event-taulukon eventit läpi
		for x in range(1,x_max):
			fw.write("\n")
			for y in range(y_max):

				#Eventti
				try:
					track = self.event_table[x,y].event_id.track
					number = self.event_table[x,y].event_id.id
					attr = self.event_table[x,y].attr
				except:
					print("Not found: x=%s ,y=%s" % (x,y))
					# Kirjoitetaan trace graphviz-tiedostoon
					#fw.write("{%s} -> %s [node style=invis]\n" % (node_prevs,node))
					continue

				node="%s.%s" % (track,number)

				# Eventin lähde-eventit
				node_prevs = ""
				for i in range(1,self.event_table[x,y].source_id_cnt+1):
					track_prev = self.event_table[x,y].source_ids[i].track
					number_prev = self.event_table[x,y].source_ids[i].id
					attr_prev = self.event_table[x,y].attr
					node_prevs += "%s.%s " % (track_prev,number_prev)

				# Main- ja sivuhaarat eri väreillä 
				color="#000000"
				if attr=="M" and attr_prev=="M":
					color="#0000ff"

				# Blokien väliset yhteys-tracet eri värillä
				if (x % tle_max) == 0:
					color="#ff0000"

				# Kirjoitetaan trace graphviz-tiedostoon
				#fw.write("{%s} -> %s\n" % (node_prevs,node))
				fw.write("{ edge [color=\"%s\"]\n {%s} -> %s\n}\n" % (color,node_prevs,node))

		fw.write("}\n")
		fw.close()	


	def make_dir_if_no_exist(self,file_path_name):
		# Python3
		#os.makedirs(os.path.dirname(file_path_name), exist_ok=True)

		# Python2
		if not os.path.exists(os.path.dirname(file_path_name)):
			try:
				os.makedirs(os.path.dirname(file_path_name))
			except OSError as exc:
				if exc.errno != errno.EEXIST:
					raise

	class Branch_complexity_params:
		def __init__(self,btre_min,btre_max,bmer_min,bmer_max,bctype):
			print("Branch_complexity_params:")
			self.btre_min=btre_min
			self.btre_max=btre_max
			self.bmer_min=bmer_min
			self.bmer_max=bmer_max
			self.bctype=bctype

	class Trace_size_variation_params:
		def __init__(self,tle_min,tle_max,tnu_min,tnu_max,tble_min,tble_max,tbnu_min,tbnu_max):
			print("Trace_size_variation_params:")
			self.tle_min=tle_min
			self.tle_max=tle_max
			self.tnu_min=tnu_min
			self.tnu_max=tnu_max
			self.tble_min=tble_min
			self.tble_max=tble_max
			self.tbnu_min=tbnu_min
			self.tbnu_max=tbnu_max

	class TestMatrix:

		test_pattern_blocks={}

		def __init__(self,matrix_x,matrix_y,branch_complexity_level_params,trace_size_variation_level_params):
			print("TestMatrix")

			# Luodaan matriisin elementit (patternit)
			for x in range(int(matrix_x)):

				btre_min = branch_complexity_level_params[x].btre_min
				btre_max = branch_complexity_level_params[x].btre_max
				bmer_min = branch_complexity_level_params[x].bmer_min
				bmer_max = branch_complexity_level_params[x].bmer_max
				bctype = branch_complexity_level_params[x].bctype

				for y in range(int(matrix_y)): 

					tle_min = trace_size_variation_level_params[y].tle_min
					tle_max = trace_size_variation_level_params[y].tle_max
					tnu_min = trace_size_variation_level_params[y].tnu_min
					tnu_max = trace_size_variation_level_params[y].tnu_max
					tble_min = trace_size_variation_level_params[y].tble_min
					tble_max = trace_size_variation_level_params[y].tble_max
					tbnu_min = trace_size_variation_level_params[y].tbnu_min
					tbnu_max = trace_size_variation_level_params[y].tbnu_max

					self.test_pattern_blocks[x,y] = self.TracePatternBlocks(x,y,
						tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max,
						btre_min,btre_max,bmer_min,bmer_max,bctype)			

		class TracePatternBlocks:

			def __init__(self,x,y,tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max,btre_min,btre_max,bmer_min,bmer_max,bctype):
				print("TracePatternBlocks: x=%d, y=%d" % (x,y))	
				print("tble_min=%s,tble_max=%s,tbnu_min=%s,tbnu_max=%s,tle_min=%s,tle_max=%s,tnu_min=%s,tnu_max=%s" % 
					(tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max))	
				print("btre_min=%s,btre_max=%s,bmer_min=%s,bmer_max=%s,bctype=%s" % 
					(btre_min,btre_max,bmer_min,bmer_max,bctype))	

				self.b_parameters = (btre_min,btre_max,bmer_min,bmer_max,bctype)
				self.t_parameters = (tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max)

	class LogFiles:

		def __init__(self,lver,lsnoe,lsnof,lcnoi,lcmis,lcinc,lsrc,lmeta):
			print("LogFiles")
			print("lver=%s,lsnoe=%s,lsnof=%s,lcnoi=%s,lcmis=%s,lcinc=%s,lsrc=%s,lmeta=%s" % (lver,lsnoe,lsnof,lcnoi,lcmis,lcinc,lsrc,lmeta))	
			self.parameters=(lver,lsnoe,lsnof,lcnoi,lcmis,lcinc,lsrc,lmeta)

	class TraceBlock:

		def __init__(self,tb_x,tb_y,tle_min,tle_max,tnu_min,tnu_max,btre_min,btre_max,bmer_min,bmer_max,
			event_table,time_ev_max):
	
			self.input_event_list=[]
			self.output_event_list=[]
			self.output_main_event_list=[]
			self.time_ev_max=time_ev_max

			# Generoidaan trace blockin eventit event-taulukko, jossa trackit x-akselilla ja (main)tracet y-akselilla
			# Käydään blockin trackit läpi
			for x in range(tle_max):
				track = x  + tb_x * tle_max
				track_prev = track-1

				# Jos ensimmäinen track
				if x == 0:
					print("\n First track")
					# Käydään eventit läpi
					for y in range(tnu_max):
						number_y = y + tb_y * tnu_max
						attr="-" 
						data="D%s-%s" % (track,number_y)
						#timestamp = 1 + track*10 + number_y
						timestamp = 1 + track*self.time_ev_max + number_y
						event_table[track,number_y] = self.Event(track,number_y,attr,data,timestamp)
						event_table[track,number_y].set_attr("M")	# Main-haaran eventti
						self.input_event_list.append(event_table[track,number_y])

				# Jos toinen track
				elif x == 1: 
					number_z=0 + tb_y * tnu_max * btre_max
					print("\n Second track: %s" % number_z)

					for y in range(tnu_max):
						number_y = y + tb_y * tnu_max
						# Käydään tree-haarat läpi
						for z in range(btre_max):
							attr="-" 
							data="D%s-%s" % (track,number_z)
							#timestamp = 1 + track*10 + number_z
							timestamp = 1 + track*self.time_ev_max + number_z
							event_table[track,number_z] = self.Event(track,number_z,attr,data,timestamp)

							event_table[track,number_z].add_source_id(track_prev,number_y)
							# Myös toisin päin (helpottaa testianalysointien generointia ?)
							event_table[track_prev,number_y].add_target_id(track,number_z)

							# Eventit tyyppi
							if (number_z % btre_max) == 0:
								event_table[track,number_z].set_attr("M")
							else:
								event_table[track,number_z].set_attr("B")

							number_z += 1

				# Jos viimeinen track
				elif x == int(tle_max)-1:
					number_z=0 + tb_y * tnu_max * btre_max
					# Lasketaan viimeisen trackin lohkon eventtien lkm 
					# (ei toimi aina ? jos lohkossa useita merged-haaroja ?)
					last_track_max=tnu_max*btre_max - bmer_max + 1
					#print(" last_track_max=%s" % last_track_max)
					number_last = 0 + tb_y * last_track_max
					print("\n Last track: %s, last:%s" % (number_z,number_last))

					number_z_list = []
					number_z_cnt = 0
					for y in range(tnu_max):
						main_trace=1
						for z in range(btre_max):
							if main_trace == 1:

								print(" Main trace: number_z_cnt=%s, number_z=%s, bmer_max=%s" % (number_z_cnt,number_z,bmer_max))

								number_z_list.append(number_z)
								if number_z_cnt >= bmer_max-1:
									print(" Merged events:")
									data="D%s-%s" % (track,number_last)
									#timestamp = 1 + track*10 + number_last
									timestamp = 1 + track*self.time_ev_max + number_last
									event_table[track,number_last] = self.Event(track,number_last,attr,data,timestamp)
									event_table[track,number_last].set_attr("M")
									self.output_event_list.append(event_table[track,number_last])
									self.output_main_event_list.append(event_table[track,number_last])

									for number_z_old in number_z_list:
										event_table[track,number_last].add_source_id(track_prev,number_z_old)
										# Myös toisin päin (helpottaa testianalysointien generointia ?)
										event_table[track_prev,number_z_old].add_target_id(track,number_last)
											
									number_last += 1
									number_z_list = []
									number_z_cnt = 0
								else:
									number_z_cnt += 1
							else:
								
								print(" No main trace ")

								data="D%s-%s" % (track,number_last)
								#timestamp = 1 + track*10 + number_last
								timestamp = 1 + track*self.time_ev_max + number_last
								event_table[track,number_last] = self.Event(track,number_last,attr,data,timestamp)

								event_table[track,number_last].add_source_id(track_prev,number_z)
								# Myös toisin päin (helpottaa testianalysointien generointia ?)
								event_table[track_prev,number_z].add_target_id(track,number_last)

								event_table[track,number_last].set_attr("B")
								self.output_event_list.append(event_table[track,number_last])
								number_last += 1					
							number_z += 1
							main_trace=0

				# Muuten väli-trackit
				else:
					number_z=0 + tb_y * tnu_max * btre_max
					print("\n Inter tracks: %s" % number_z)
					for y in range(tnu_max):
						for z in range(btre_max):
							attr="-" 
							data="D%s-%s" % (track,number_z)
							#timestamp = 1 + track*10 + number_z
							timestamp = 1 + track*self.time_ev_max + number_z

							event_table[track,number_z] = self.Event(track,number_z,attr,data,timestamp)

							event_table[track,number_z].add_source_id(track_prev,number_z)
							# Myös toisin päin (helpottaa testianalysointien generointia ?)
							event_table[track_prev,number_z].add_target_id(track,number_z)

							event_table[track,number_z].set_attr(event_table[track_prev,number_z].get_attr())
							number_z += 1


		def get_output_events(self,type):
			print("get_output_events: %s" % type)
			if type == "M":
				return self.output_main_event_list
			else:
				return self.output_event_list

		def get_input_events(self):
			print("get_input_events")
			return self.input_event_list

		class Event:

			def __init__(self,track,number,attr,data,time):
				print("      Event:    Track: %s, Number: %s,   Attr: %s, Data: %s, Time: %s" % (track,number,attr,data,time))
				self.event_id=self.Id(track,number)

				# Relationship by membership (aggregation ?)
				# Tieto on eventin ulkopuolella ?
				self.attr=attr
				self.data=data

				# Relationship by timing
				self.time=time

				self.source_ids={}
				self.target_ids={}
				self.source_id_cnt=0
				self.target_id_cnt=0

			# Relationship by cause ? (vain edelliset eventit, ei koko ketjua ?)
			def add_source_id(self,track,number):
				self.source_id_cnt+=1
				self.source_ids[self.source_id_cnt]=self.Id(track,number)
				print("       add sid: %s.%s for event: %s.%s" % (track,number,self.event_id.track,self.event_id.id))

			# Tarviiko tätä, koska tämä ennustaa ? (tarvii ainakin testianalyysien generointiin ?)
			def add_target_id(self,track,number):
				self.target_id_cnt+=1
				self.target_ids[self.target_id_cnt]=self.Id(track,number)
				print("        add tid: %s.%s for event: %s.%s" % (track,number,self.event_id.track,self.event_id.id))

			def set_attr(self,attr):
				print("        set_attr: %s" % attr)
				self.attr=attr

			def get_attr(self):
				#print("get_attr")
				return self.attr

			class Id:
				def __init__(self,track,id):
					#print(" ++ Event Id: Track: %s, Id: %s" % (track,id))
					self.track=track
					self.id=id

def set_test_model(args):

	global test_model

	# Luodaan testimalli
	test_model = TestModel(args)

def generate_analyzing():

	global test_model

	# Generoidaan analyysit
	test_model.generate_analyzing()


#******************************************************************************
#
#	FUNCTION:	main
#
#******************************************************************************
def main():

	print("version: %s" % g_version)

	print("Python sys: %s\n" % sys.version)
	#print("Modules   : %s\n" % sys.modules.keys())

	start_time = time.time()

	parser = argparse.ArgumentParser()
	parser.add_argument('-test_name','--test_name', dest='test_name', help='test_name')
	parser.add_argument('-ana_path','--ana_path', dest='ana_path', help='ana_path')
	parser.add_argument('-ana_lang','--ana_lang', dest='ana_lang', help='ana_lang')

	# Branch complexity parametrit
	# Oletusarvot
	parser.add_argument('-b0_bmer_min','--b0_bmer_min', dest='b0_bmer_min', type=int, default=1, help='b0_bmer_min')
	parser.add_argument('-b0_bmer_max','--b0_bmer_max', dest='b0_bmer_max', type=int, default=1, help='b0_bmer_max')
	parser.add_argument('-b0_bmer_ctrl','--b0_bmer_ctrl', dest='b0_bmer_ctrl', type=int, default=1, help='b0_bmer_ctrl')
	parser.add_argument('-b0_bctype','--b0_bctype', dest='b0_bctype', help='b0_bctype')
	# Tason 1 parametrit
	parser.add_argument('-b1_btre_min','--b1_btre_min', dest='b1_btre_min', type=int, help='b1_btre_min')
	parser.add_argument('-b1_btre_max','--b1_btre_max', dest='b1_btre_max', type=int, help='b1_btre_max')
	# Tason 2 parametrit
	parser.add_argument('-b2_btre_min','--b2_btre_min', dest='b2_btre_min', type=int, help='b2_btre_min')
	parser.add_argument('-b2_btre_max','--b2_btre_max', dest='b2_btre_max', type=int, help='b2_btre_max')
	parser.add_argument('-b2_bctype','--b2_bctype', dest='b2_bctype', help='b2_bctype')	
	# Tason 3 parametrit
	parser.add_argument('-b3_bmer_min','--b3_bmer_min', dest='b3_bmer_min', type=int, help='b3_bmer_min')
	parser.add_argument('-b3_bmer_max','--b3_bmer_max', dest='b3_bmer_max', type=int, help='b3_bmer_max')
	parser.add_argument('-b3_bmer_ctrl','--b3_bmer_ctrl', dest='b3_bmer_ctrl', type=int, default=1, help='b3_bmer_ctrl')

	# Traces size variation parametrit
	# Oletusarvot
	parser.add_argument('-t0_tbnu_min','--t0_tbnu_min', dest='t0_tbnu_min', type=int, default=1, help='t0_tbnu_min')
	parser.add_argument('-t0_tbnu_max','--t0_tbnu_max', dest='t0_tbnu_max', type=int, default=1, help='t0_tbnu_max')
	parser.add_argument('-t0_tnu_min','--t0_tnu_min', dest='t0_tnu_min', type=int, default=3, help='t0_tnu_min')
	parser.add_argument('-t0_tnu_max','--t0_tnu_max', dest='t0_tnu_max', type=int, default=3, help='t0_tnu_max')
	# Tason 1 parametrit
	parser.add_argument('-t1_tle_min','--t1_tle_min', dest='t1_tle_min', type=int, help='t1_tle_min')
	parser.add_argument('-t1_tle_max','--t1_tle_max', dest='t1_tle_max', type=int, help='t1_tle_max')
	parser.add_argument('-t1_tble_min','--t1_tble_min', dest='t1_tble_min', type=int, help='t1_tble_min')
	parser.add_argument('-t1_tble_max','--t1_tble_max', dest='t1_tble_max', type=int, help='t1_tble_max')
	# Tason 2 parametrit
	parser.add_argument('-t2_tle_min','--t2_tle_min', dest='t2_tle_min', type=int, help='t2_tle_min')
	parser.add_argument('-t2_tle_max','--t2_tle_max', dest='t2_tle_max', type=int, help='t2_tle_max')
	parser.add_argument('-t2_tble_min','--t2_tble_min', dest='t2_tble_min', type=int, help='t2_tble_min')
	parser.add_argument('-t2_tble_max','--t2_tble_max', dest='t2_tble_max', type=int, help='t2_tble_max')
	# Tason 3 parametrit
	parser.add_argument('-t3_tnu_min','--t3_tnu_min', dest='t3_tnu_min', type=int, help='t3_tnu_min')
	parser.add_argument('-t3_tnu_max','--t3_tnu_max', dest='t3_tnu_max', type=int, help='t3_tnu_max')
	parser.add_argument('-t3_tbnu_min','--t3_tbnu_min', dest='t3_tbnu_min', type=int, help='t3_tbnu_min')
	parser.add_argument('-t3_tbnu_max','--t3_tbnu_max', dest='t3_tbnu_max', type=int, help='t3_tbnu_max')

	# Trace yleiset parametrit
	parser.add_argument('-branching_events_ctrl','--branching_events_ctrl', dest='branching_events_ctrl', type=int, help='branching_events_ctrl')

	# Trace searching parameters
	parser.add_argument('-trace_search_start','--trace_search_start', dest='trace_search_start', help='trace_search_start')
	parser.add_argument('-trace_search_stop','--trace_search_stop', dest='trace_search_stop', help='trace_search_stop')
	parser.add_argument('-trace_search_direction_mode','--trace_search_direction_mode', dest='trace_search_direction_mode', help='trace_search_direction_mode')

	# Aika parameterit
	parser.add_argument('-time_start','--time_start', dest='time_start', type=int, help='time_start')
	parser.add_argument('-time_ev_min','--time_ev_min', dest='time_ev_min', type=int, help='time_ev_min')
	parser.add_argument('-time_ev_max','--time_ev_max', dest='time_ev_max', type=int, help='time_ev_max')
	parser.add_argument('-time_etc','--time_etc', dest='time_etc', type=int, help='time_etc')
	parser.add_argument('-time_ttc','--time_ttc', dest='time_ttc', type=int, help='time_ttc')
	parser.add_argument('-time_wtc','--time_wtc', dest='time_wtc', type=int, help='time_wtc')

	# Muut
	parser.add_argument('-gui_enable','--gui_enable', dest='gui_enable', type=int, help='gui_enable')	

	args = parser.parse_args()

	print("test_name    : %s " % args.test_name)
	print("ana_path     : %s " % args.ana_path)
	print("ana_lang     : %s " % args.ana_lang)

	print("\nBranch complexity level ---" )
	print("Default values:" )
	print("b0_bmer_min  : %s" % args.b0_bmer_min)
	print("b0_bmer_max  : %s" % args.b0_bmer_max)
	print("b0_bmer_ctrl  : %s" % args.b0_bmer_ctrl)
	print("b0_bctype    : %s" % args.b0_bctype)

	print("Level 1:" )
	print("b1_btre_min  : %s" % args.b1_btre_min)
	print("b1_btre_max  : %s" % args.b1_btre_max)

	print("Level 2:" )
	print("b2_btre_min  : %s" % args.b2_btre_min)
	print("b2_btre_max  : %s" % args.b2_btre_max)
	print("b2_bctype    : %s" % args.b2_bctype)

	print("Level 3:" )
	print("b3_bmer_min  : %s" % args.b3_bmer_min)
	print("b3_bmer_max  : %s" % args.b3_bmer_max)
	print("b3_bmer_ctrl  : %s" % args.b3_bmer_ctrl)

	print("\nTraces size variation level ---" )
	print("Default values:" )
	print("t0_tbnu_min  : %s" % args.t0_tbnu_min)
	print("t0_tbnu_max  : %s" % args.t0_tbnu_max)
	print("t0_tnu_min   : %s" % args.t0_tnu_min)
	print("t0_tnu_max   : %s" % args.t0_tnu_max)

	print("Level 1:" )
	print("t1_tle_min   : %s" % args.t1_tle_min)
	print("t1_tle_max   : %s" % args.t1_tle_max)
	print("t1_tble_min  : %s" % args.t1_tble_min)
	print("t1_tble_max  : %s" % args.t1_tble_max)

	print("Level 2:" )
	print("t2_tle_min   : %s" % args.t2_tle_min)
	print("t2_tle_max   : %s" % args.t2_tle_max)
	print("t2_tble_min  : %s" % args.t2_tble_min)
	print("t2_tble_max  : %s" % args.t2_tble_max)

	print("Level 3:" )
	print("t3_tnu_min   : %s" % args.t3_tnu_min)
	print("t3_tnu_max   : %s" % args.t3_tnu_max)
	print("t3_tbnu_min  : %s" % args.t3_tbnu_min)
	print("t3_tbnu_max  : %s" % args.t3_tbnu_max)

	print("\nTrace general parameters ---" )
	print("branching_events_ctrl   : %s" % args.branching_events_ctrl)

	print("\nTrace searching parameters ---" )
	print("trace_search_start   : %s" % args.trace_search_start)
	print("trace_search_stop   : %s" % args.trace_search_stop)
	print("trace_search_direction_mode   : %s" % args.trace_search_direction_mode)

	print("\nTime parameters ---" )
	print("time_start   : %s" % args.time_start)
	print("time_ev_min  : %s" % args.time_ev_min)
	print("time_ev_max  : %s" % args.time_ev_max)
	print("time_etc  : %s" % args.time_etc)
	print("time_ttc  : %s" % args.time_ttc)
	print("time_wtc  : %s" % args.time_wtc)

	print("\nOther parameters ---" )
	print("gui_enable   : %s" % args.gui_enable)

	config = configparser.ConfigParser()
	config.read('LogTestGen.ini')
	testarea_x = int(config['GEOMETRY']['Testarea_x'])
	testarea_y = int(config['GEOMETRY']['Testarea_y'])
	logarea_x = int(config['GEOMETRY']['Logarea_x'])
	logarea_y = int(config['GEOMETRY']['Logarea_y'])

	print("Testarea_x = %s" % testarea_x)
	print("Testarea_y = %s" % testarea_y)
	print("Logarea_x = %s" % logarea_x)
	print("Logarea_y = %s" % logarea_y)

	# K�ynnistet��n tarvittaessa GUI
	if args.gui_enable == 1:
		print("GUI enabled\n")

		area_x,area_y = args.area_size.split("x")
		bstop_size_x,bstop_size_y = args.busstop_size.split("x")

		zoom_factor = args.gui_zoom

		area_x_int = int(area_x)
		area_y_int = int(area_y)
		bstop_size_x_int = int(bstop_size_x)
		bstop_size_y_int = int(bstop_size_y)

		x_width = area_x_int + bstop_size_x_int
		x_width_new = int(x_width * zoom_factor)
		y_height = area_y_int + bstop_size_y_int
		y_height_new = int(y_height * zoom_factor)
		x_offset = int(bstop_size_x_int / 2)
		y_offset = int(bstop_size_y_int / 2)
		x_offset_new = int(x_offset * zoom_factor)
		y_offset_new = int(y_offset * zoom_factor)

		print("zoom_factor  = %s" % zoom_factor)
		print("x_width      = %s" % x_width)
		print("y_height     = %s" % y_height)
		print("x_width_new  = %s" % x_width_new)
		print("y_height_new = %s" % y_height_new)
		print("x_offset     = %s" % x_offset)
		print("y_offset     = %s" % y_offset)
		print("x_offset_new = %s" % x_offset_new)
		print("y_offset_new = %s" % y_offset_new)

		app = QApplication(sys.argv)

		#gui = GUI_TestArea(args,"Testarea",testarea_x,testarea_y,x_width_new,y_height_new,
		#						x_offset_new,y_offset_new,zoom_factor,generate_testarea)
		#gui2 = GUI_LogArea(args,"Logarea",logarea_x,logarea_y,700,1050,0,0,1.0,generate_bus_run_logs)

		#gui.show()
		#gui2.show()

		sys.exit(app.exec_())

	else:
		self_value = ""
		set_test_model(args)
		generate_analyzing()
		#generate_logs()

	print("\n Total execution time: %.3f seconds" % (time.time() - start_time))

	# Jos GUI k�yt�ss� lopetetaan vasta enterin painamisen j�lkeen
	if args.gui_enable == 1:
		user_input = input("Press enter to stop")

if __name__ == '__main__':
    main()
