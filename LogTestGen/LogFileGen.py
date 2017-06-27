# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	LogFileGen.py

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

		self.trace_blocks = {}
		self.event_table = {}

		self.test_name=args.test_name
		self.log_path=args.log_path
		#self.date
		self.time_start=args.time_start
		self.time_ev_min=args.time_ev_min
		self.time_ev_max=args.time_ev_max

		# Luodaan lokitiedostojen tiedot
		self.log_files = self.LogFiles(args.lver,args.lsnoe,args.lsnof,args.lcnoi,args.lcmis,args.lcinc,args.lsrc,args.lmeta,
			args.btre_min,args.btre_max,args.bmer_min,args.bmer_max,args.bctype,
			args.tble_min,args.tble_max,args.tbnu_min,args.tbnu_max,args.tle_min,args.tle_max,args.tnu_min,args.tnu_max)

	def generate_logs(self):
		print("\ngenerate_logs\n")

		(lver,lsnoe,lsnof,lcnoi,lcmis,lcinc,lsrc,lmeta)=self.log_files.parameters_1
		print("lver=%s, lsnoe=%s, lsnof=%s, lcnoi=%s, lcmis=%s, lcinc=%s, lsrc=%s, lmeta=%s" % (lver,lsnoe,lsnof,lcnoi,lcmis,lcinc,lsrc,lmeta))

		(btre_min,btre_max,bmer_min,bmer_max,bctype) = self.log_files.parameters_2
		(tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max) = self.log_files.parameters_3

		# Lisäksi matriisin kompleksisimman 3,3 elementin analyysitiedot
		#(btre_min,btre_max,bmer_min,bmer_max,bctype) = self.test_matrix.test_pattern_blocks[2,2].b_parameters
		#(tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max) = self.test_matrix.test_pattern_blocks[2,2].t_parameters

		# Luodaan lokin trace pattern
		self.create_trace_pattern("Generating",btre_min,btre_max,bmer_min,bmer_max,bctype,
							tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max)

		# Tulostetaan trace pattern graafina
		self.print_trace_pattern(tble_max,tbnu_max,tle_max,tnu_max,btre_max,"logs")

		# Tulostetaan lokit trace patternin perusteella
		self.write_trace_pattern_logs(tble_max,tbnu_max,tle_max,tnu_max,btre_max,"gen")


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

	def write_trace_pattern_logs(self,tble_max,tbnu_max,tle_max,tnu_max,btre_max,file_info):
		
		print("\nwrite_trace_pattern_logs -- ")

		# Lasketaan trace patternin x,y maksimikoko
		x_max = tble_max * tle_max
		y_max = tbnu_max * tnu_max * btre_max
		#print (" x_max=%s ,y_max=%s" % (x_max,y_max))

		fw={}

		print("Inits logs and writes headers")
		# Lokitiedostot ja niiden headerit
		for x in range(x_max):

			# Alustetaan muut lokitiedostot
			log_file_name = "Log_%s_%s_track_%s" % (self.test_name,file_info,x)
			login_file_path_name = self.log_path + self.test_name + "/" + log_file_name + ".csv"
			print("write_file: %s" % login_file_path_name)

			self.make_dir_if_no_exist(login_file_path_name)
			fw[x] = open(login_file_path_name, 'w')

			header = "%s,%s,%s,%s,%s,%s\n" % ("TIME","ID","SOURCES","TARGETS","ATTR","DATA")
			fw[x].write(header)			

		print("Writes data")

		# Lokitiedostojen rivit
		for x in range(x_max):
			for y in range(y_max):

				# Event ja sen tiedot
				try:

					track = self.event_table[x,y].event_id.track
					number = self.event_table[x,y].event_id.id
					time = self.event_table[x,y].time
					attr = self.event_table[x,y].attr
					data = self.event_table[x,y].data

					sources = ""
					for i in range(1,self.event_table[x,y].source_id_cnt+1):
						str = "%s.%s;" % (self.event_table[x,y].source_ids[i].track,
										self.event_table[x,y].source_ids[i].id)
						sources += str
					targets = ""
					for i in range(1,self.event_table[x,y].target_id_cnt+1):
						str = "%s.%s;" % (self.event_table[x,y].target_ids[i].track,
										self.event_table[x,y].target_ids[i].id)
						targets += str

					line = "%s,%s.%s,%s,%s,%s,%s\n" % (time,track,number,sources,targets,attr,data)
					fw[x].write(line)

				except:
					print("Not found: x=%s ,y=%s" % (x,y))
					continue	

			fw[x].close()	
	
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

	class LogFiles:

		def __init__(self,lver,lsnoe,lsnof,lcnoi,lcmis,lcinc,lsrc,lmeta,
			btre_min,btre_max,bmer_min,bmer_max,bctype,
			tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max):

			print("LogFiles")
			print("lver=%s,lsnoe=%s,lsnof=%s,lcnoi=%s,lcmis=%s,lcinc=%s,lsrc=%s,lmeta=%s" % (lver,lsnoe,lsnof,lcnoi,lcmis,lcinc,lsrc,lmeta))	
			self.parameters_1=(lver,lsnoe,lsnof,lcnoi,lcmis,lcinc,lsrc,lmeta)
			self.parameters_2=(btre_min,btre_max,bmer_min,bmer_max,bctype)
			self.parameters_3=(tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max)

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

def generate_logs():

	global test_model

	# Generoidaan lokit
	test_model.generate_logs()

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
	parser.add_argument('-log_path','--log_path', dest='log_path', help='log_path')

	# Lokitiedosto trace-parametrit
	parser.add_argument('-tble_min','--tble_min', dest='tble_min', type=int, default=1, help='tble_min')
	parser.add_argument('-tble_max','--tble_max', dest='tble_max', type=int, default=1, help='tble_max')
	parser.add_argument('-tbnu_min','--tbnu_min', dest='tbnu_min', type=int, default=1, help='tbnu_min')
	parser.add_argument('-tbnu_max','--tbnu_max', dest='tbnu_max', type=int, default=1, help='tbnu_max')
	parser.add_argument('-bctype','--bctype', dest='bctype', help='bctype')	

	parser.add_argument('-tnu_min','--tnu_min', dest='tnu_min', type=int, default=1, help='tnu_min')
	parser.add_argument('-tnu_max','--tnu_max', dest='tnu_max', type=int, default=1, help='tnu_max')
	parser.add_argument('-bmer_min','--bmer_min', dest='bmer_min', type=int, default=1, help='bmer_min')
	parser.add_argument('-bmer_max','--bmer_max', dest='bmer_max', type=int, default=1, help='bmer_max')
	parser.add_argument('-bmer_ctrl','--bmer_ctrl', dest='bmer_ctrl', type=int, default=1, help='bmer_ctrl')

	parser.add_argument('-tle_min','--tle_min', dest='tle_min', type=int, default=1, help='tle_min')
	parser.add_argument('-tle_max','--tle_max', dest='tle_max', type=int, default=1, help='tle_max')
	parser.add_argument('-btre_min','--btre_min', dest='btre_min', type=int, default=1, help='btre_min')
	parser.add_argument('-btre_max','--btre_max', dest='btre_max', type=int, default=1, help='btre_max')

	# Trace yleiset parametrit
	parser.add_argument('-branching_events_ctrl','--branching_events_ctrl', dest='branching_events_ctrl', type=int, help='branching_events_ctrl')

	# Lokitiedosto yleiset parametrit
	parser.add_argument('-lver','--lver', dest='lver', type=int, help='lver')
	parser.add_argument('-lsnoe','--lsnoe', dest='lsnoe', help='lsnoe')	
	parser.add_argument('-lsnof','--lsnof', dest='lsnof', type=int, help='lsnof')
	parser.add_argument('-lcnoi','--lcnoi', dest='lcnoi', type=int, help='lcnoi')
	parser.add_argument('-lcmis','--lcmis', dest='lcmis', type=int, help='lcmis')
	parser.add_argument('-lcinc','--lcinc', dest='lcinc', type=int, help='lcinc')
	parser.add_argument('-lsrc','--lsrc', dest='lsrc', help='lsrc')
	parser.add_argument('-lmeta','--lmeta', dest='lmeta', help='lmeta')

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
	print("log_path     : %s " % args.log_path)

	print("\nLog trace parameters ---" )
	print("tble_min  : %s" % args.tble_min)
	print("tble_max  : %s" % args.tble_max)
	print("tbnu_min  : %s" % args.tbnu_min)
	print("tbnu_max  : %s" % args.tbnu_max)
	print("bctype  : %s" % args.bctype)

	print("tnu_min  : %s" % args.tnu_min)
	print("tnu_max  : %s" % args.tnu_max)
	print("bmer_min  : %s" % args.bmer_min)
	print("bmer_max  : %s" % args.bmer_max)
	print("bmer_ctrl  : %s" % args.bmer_ctrl)

	print("tle_min  : %s" % args.tle_min)
	print("tle_max  : %s" % args.tle_max)
	print("btre_min  : %s" % args.btre_min)
	print("btre_max  : %s" % args.btre_max)

	print("\nTrace general parameters ---" )
	print("branching_events_ctrl   : %s" % args.branching_events_ctrl)

	print("\nLog files parameters ---" )
	print("lver         : %s" % args.lver)
	print("lsnoe        : %s" % args.lsnoe)
	print("lsnof        : %s" % args.lsnof)
	print("lcnoi        : %s" % args.lcnoi)
	print("lcmis        : %s" % args.lcmis)
	print("lcinc        : %s" % args.lcinc)
	print("lsrc         : %s" % args.lsrc)
	print("lmeta        : %s" % args.lmeta)

	print("\nTime parameters ---" )
	print("time_start   : %s" % args.time_start)
	print("time_ev_min  : %s" % args.time_ev_min)
	print("time_ev_max  : %s" % args.time_ev_max)

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
		#generate_analyzing()
		generate_logs()

	print("\n Total execution time: %.3f seconds" % (time.time() - start_time))

	# Jos GUI k�yt�ss� lopetetaan vasta enterin painamisen j�lkeen
	if args.gui_enable == 1:
		user_input = input("Press enter to stop")

if __name__ == '__main__':
    main()
