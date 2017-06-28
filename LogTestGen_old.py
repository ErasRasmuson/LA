# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	LogTestGen.py

AUTHOR:     Esa Heikkinen
DATE:       13.10.2016
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

	#Event_dict = { 'Id': '0', 'Addr': '0', 'Data': '0', 'Time': '0', 'Source_ids': '0', 'Targer_ids': '0', 'Source_id_cnt': '0', 'Target_id_cnt': '0'}

	branch_complexity_level_params = {}
	trace_size_variation_level_params = {}
	branch_complexity_level_number = 3
	trace_size_variation_level_number = 3

	trace_blocks = {}
	event_table = {}

	track_event_count = {}

	def __init__(self,args):
		print("TestModel")

		self.test_name=args.test_name
		self.ana_path=args.ana_path
		#self.date
		#self.start_time

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
		self.log_files = self.LogFiles(args.lver,args.lsnoe,args.lsnof,args.lcnoi,args.lcmis,args.lcinc,args.lsrc,args.lmeta)


	def generate_analyzing(self):
		print("\ngenerate_analyzing\n")

		for x in range(int(self.branch_complexity_level_number)):
			for y in range(int(self.trace_size_variation_level_number)): 

				(btre_min,btre_max,bmer_min,bmer_max,bctype) = self.test_matrix.test_pattern_blocks[x,y].b_parameters
				(tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max) = self.test_matrix.test_pattern_blocks[x,y].t_parameters

				# Luodaan kaksiulottoinen event-taulukko, jossa trackit X-akselilla ja (main)tracet y-akselilla
				#self.create_trace_pattern("Analyzing",btre_min,btre_max,bmer_min,bmer_max,bctype,
				#					tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max)

	def generate_logs(self):
		print("\ngenerate_logs\n")

		(lver,lsnoe,lsnof,lcnoi,lcmis,lcinc,lsrc,lmeta)=self.log_files.parameters
		print("lver=%s, lsnoe=%s, lsnof=%s, lcnoi=%s, lcmis=%s, lcinc=%s, lsrc=%s, lmeta=%s" % (lver,lsnoe,lsnof,lcnoi,lcmis,lcinc,lsrc,lmeta))

		# Lisäksi matriisin kompleksisimman 3,3 elementin analyysitiedot
		(btre_min,btre_max,bmer_min,bmer_max,bctype) = self.test_matrix.test_pattern_blocks[2,2].b_parameters
		(tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max) = self.test_matrix.test_pattern_blocks[2,2].t_parameters

		# Luodaan lokin trace pattern
		self.create_trace_pattern("Generating",btre_min,btre_max,bmer_min,bmer_max,bctype,
							tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max)

		# Tulostetaan trace pattern graafina
		self.print_trace_pattern(tble_max,tbnu_max,tle_max,tnu_max,btre_max)

	def create_trace_pattern(self,mode,btre_min,btre_max,bmer_min,bmer_max,bctype,
							tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max):
		print("create_event_table: %s" % mode)
		print("tble_min=%s,tble_max=%s,tbnu_min=%s,tbnu_max=%s,tle_min=%s,tle_max=%s,tnu_min=%s,tnu_max=%s" % 
			(tble_min,tble_max,tbnu_min,tbnu_max,tle_min,tle_max,tnu_min,tnu_max))	
		print("btre_min=%s,btre_max=%s,bmer_min=%s,bmer_max=%s,bctype=%s" % 
			(btre_min,btre_max,bmer_min,bmer_max,bctype))

		# Event-taulukko, jossa trackit x-akselilla ja (main)tracet y-akselilla
		for x in range(tble_max):
			print("\n ### Trace block x: %s / %s" % (x,tble_max-1))
			for y in range(tbnu_max):
				print(" ### Trace block y: %s / %s" % (y,tbnu_max-1))
				self.trace_blocks[x,y]=self.TraceBlock(x,y,tle_min,tle_max,tnu_min,tnu_max,
					btre_min,btre_max,bmer_min,bmer_max,
					self.event_table,self.track_event_count)

		# Tehdään horisontaalisten blockien väliset event-liitokset event-taulukkoon ?
		if tble_max > 1:
			for x in range(1,tble_max):
				for y in range(tbnu_max):
					if bctype == "All":
						prev_outputs = self.trace_blocks[x-1,y].get_output_events("A")
					else:
						prev_outputs = self.trace_blocks[x-1,y].get_output_events("M")

					curr_inputs = self.trace_blocks[x,y].get_input_events()
					curr_input_len = len(curr_inputs)
					curr_input_cnt=0
					for event in prev_outputs:
						curr_track=curr_inputs[curr_input_cnt].event_id.track
						curr_id=curr_inputs[curr_input_cnt].event_id.id
						curr_time=curr_inputs[curr_input_cnt].time
						# Kytketään eventit
						self.event_table[curr_track,curr_id].add_source_id(event.event_id.track,event.event_id.id)

						print("Event: t%si%s, Time: %s --> t%si%s, Time: %s" % (
							event.event_id.track,event.time,event.event_id.id,
							curr_track,curr_id,curr_time))

						curr_input_cnt+=1
						if curr_input_cnt >= curr_input_len:
							break

	def print_trace_pattern(self,tble_max,tbnu_max,tle_max,tnu_max,btre_max):

		# http://www.graphviz.org/content/switch
		
		print("print_trace_pattern:")

		# Lasketaan trace patternin x,y maksimikoko
		x_max = tble_max * tle_max
		y_max = tbnu_max * tnu_max * btre_max

		print (" x_max=%s ,y_max=%s" % (x_max,y_max))

		# Graphviz-tiedosto, johon tulostetaan graafit (tracet) visuaalisesti
		graphviz_file = "LogTestGen_%s.gv" % self.test_name
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
					id = self.event_table[x,y].event_id.id
				except:
					print("Not found: x=%s ,y=%s" % (x,y))

					# Kirjoitetaan trace graphviz-tiedostoon
					#fw.write("{%s} -> %s [node style=invis]\n" % (node_prevs,node))

					continue

				node="t%si%s" % (track,id)

				# Eventin lähde-eventit
				node_prevs = ""
				for i in range(1,self.event_table[x,y].source_id_cnt+1):
					track = self.event_table[x,y].source_ids[i].track
					id = self.event_table[x,y].source_ids[i].id
					node_prevs += "t%si%s " % (track,id)

				# Kirjoitetaan trace graphviz-tiedostoon
				fw.write("{%s} -> %s\n" % (node_prevs,node))

		fw.write("}\n")
		fw.close()	

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

		#event_table = {}
		#track_event_count = {}

		input_event_list=[]
		output_event_list=[]
		output_main_event_list=[]

		def __init__(self,tb_x,tb_y,tle_min,tle_max,tnu_min,tnu_max,btre_min,btre_max,bmer_min,bmer_max,
			event_table,track_event_count):
	
			# Generoidaan trace blockin eventit event-taulukko, jossa trackit x-akselilla ja (main)tracet y-akselilla
			# Käydään blockin trackit läpi
			for x in range(int(tle_max)):

				print("")

				y_num=int(tnu_max)
				# Toisen trackin ja sen jälkeiset mahdolliset tree haarat
				if x>0 and btre_max > 1:
					y_num=int(tnu_max)*btre_max
					print(" Tree branch: %s events" % y_num)
				track=x+tb_x*tle_max

				print(" Traceblock: x=%s, track=%s" % (x,track))

				# Viimeisen trackin mahdolliset merged haarat
				if x==int(tle_max)-1 and bmer_max > 1:
					# Jos useita haaroja. Ei toimi vielä täysin ?
					bmer_count=int(tnu_max/bmer_max)
					print(" bmer_count: %s" % bmer_count)
					y_num=y_num-(bmer_max-1)*bmer_count
					print(" Merged branch: %s events" % y_num)
					if y_num<1:
						print("  *** ERROR: Merged branches is too big ! *** ")

				print(" Events: %s in track: %s" % (y_num,track))

				#track_event_count[x]=y_num
				track_event_count[track]=y_num

				bmer_add_value = 1
				# Käydään trackin eventit läpi
				for y in range(y_num):
					
					# Luodaan eventit
					#number=y+tb_y*tnu_max
					number=y + tb_y*y_num
					
					print("    Traceblock: y=%s, number=%s" % (y,number))
					attr="-" 
					data="D%s-%s" % (track,number)
					timestamp = 1 + track*10 + number
					event_table[track,number] = self.Event(track,number,attr,data,timestamp)

					# Jos ensimmäinen track
					if x == 0:
						event_table[track,number].set_attr("M")	# Main-haaran eventti
						self.input_event_list.append(event_table[track,number])

					# Jos ei ensimmäinen track, tehdään eventtien väliset kytkennät, 
					elif x > 0:
						track_prev = track-1
						# Jos toinen track, tehdään mahdolliset tree branchet
						if x == 1 and btre_max > 1:
							number_prev = int(number / btre_max)
							event_table[track,number].add_source_id(track_prev,number_prev)
							if ((y+1) % btre_max) == 0:
								event_table[track,number].set_attr("B")
							else:
								event_table[track,number].set_attr("M")
								self.output_main_event_list.append(event_table[track,number])					

						# Jos viimeinen track ja pitää muodostaa merged haaroja 
						elif x == int(tle_max)-1 and bmer_max > 1:
							self.output_event_list.append(event_table[track,number])

							# Tehdään mahdolliset merged branchet (main tracesta)
							y_mod = ((y+1) % bmer_max)
							if y_mod == 0:
								event_table[track,number].set_attr("M")
								self.output_main_event_list.append(event_table[track,number])
								for z in range(bmer_max):
									#number_prev = z+tb_y*tnu_max * btre_max
									number_prev = z*btre_max + tb_y * (y_num + bmer_max -1)
									event_table[track,number].add_source_id(track_prev,number_prev)
							else:
								event_table[track,number].set_attr("B")
								# Tämä vähän viristys ! Toimiiko kaikissa tapaukissa ?
								#if y==0:
								#	number_prev = y+1
								#else:
								#	number_prev = y+1 * btre_max
								number_prev = y + bmer_add_value
								number_prev2 = number_prev + tb_y * (y_num + bmer_max -1)
								
								event_table[track,number].add_source_id(track_prev,number_prev2)


						# Muuten kytketään edellisen ja nykyisen trackin eventit suoraan toisiinsa
						else:
							event_table[track,number].add_source_id(track_prev,number)
							event_table[track,number].set_attr(event_table[track_prev,number].get_attr())
					else:
						print("ERROR: Illegal x: %s " % x)


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
				print("       add sid: Track: %s, Number: %s" % (track,number))
				self.source_id_cnt+=1
				self.source_ids[self.source_id_cnt]=self.Id(track,number)

			# Tarviiko tätä, koska tämä ennustaa ?
			def add_target_id(self,track,number):
				print("        add tid: Track: %s, Number: %s" % (track,number))
				self.target_id_cnt+=1

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
	parser.add_argument('-ana_path','--ana_path', dest='ana_path', help='ana_path')
	parser.add_argument('-ana_lang','--ana_lang', dest='ana_lang', help='ana_lang')

	# Branch complexity parametrit
	# Oletusarvot
	parser.add_argument('-b0_bmer_min','--b0_bmer_min', dest='b0_bmer_min', type=int, default=1, help='b0_bmer_min')
	parser.add_argument('-b0_bmer_max','--b0_bmer_max', dest='b0_bmer_max', type=int, default=1, help='b0_bmer_max')
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

	# Lokitiedosto parametrit
	parser.add_argument('-lver','--lver', dest='lver', type=int, help='lver')
	parser.add_argument('-lsnoe','--lsnoe', dest='lsnoe', help='lsnoe')	
	parser.add_argument('-lsnof','--lsnof', dest='lsnof', type=int, help='lsnof')
	parser.add_argument('-lcnoi','--lcnoi', dest='lcnoi', type=int, help='lcnoi')
	parser.add_argument('-lcmis','--lcmis', dest='lcmis', type=int, help='lcmis')
	parser.add_argument('-lcinc','--lcinc', dest='lcinc', type=int, help='lcinc')
	parser.add_argument('-lsrc','--lsrc', dest='lsrc', help='lsrc')
	parser.add_argument('-lmeta','--lmeta', dest='lmeta', help='lmeta')

	parser.add_argument('-gui_enable','--gui_enable', dest='gui_enable', type=int, help='gui_enable')	

	args = parser.parse_args()

	print("test_name    : %s " % args.test_name)
	print("log_path     : %s " % args.log_path)
	print("ana_path     : %s " % args.ana_path)
	print("ana_lang     : %s " % args.ana_lang)

	print("\nBranch complexity level ---" )
	print("Default values:" )
	print("b0_bmer_min  : %s" % args.b0_bmer_min)
	print("b0_bmer_max  : %s" % args.b0_bmer_max)
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

	print("\nLog files parameters ---" )
	print("lver         : %s" % args.lver)
	print("lsnoe        : %s" % args.lsnoe)
	print("lsnof        : %s" % args.lsnof)
	print("lcnoi        : %s" % args.lcnoi)
	print("lcmis        : %s" % args.lcmis)
	print("lcinc        : %s" % args.lcinc)
	print("lsrc         : %s" % args.lsrc)
	print("lmeta        : %s" % args.lmeta)

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
		generate_logs()

	print("\n Total execution time: %.3f seconds" % (time.time() - start_time))

	# Jos GUI k�yt�ss� lopetetaan vasta enterin painamisen j�lkeen
	if args.gui_enable == 1:
		user_input = input("Press enter to stop")

if __name__ == '__main__':
    main()
