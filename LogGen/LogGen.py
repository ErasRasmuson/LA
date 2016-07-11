# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	LogGen.py

AUTHOR:     Esa Heikkinen
DATE:       5.3.2016
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
from LogGUI import *

g_version = "$Id$"
generate_counter = 0

#******************************************************************************
#
#	CLASS:	TestArea
#
#******************************************************************************
class TestArea:

	global date

	BS_A_coords = {}
	BS_B_coords = {}
	BS_M_coords = {}
	BS_coords = {}
	BS_area_coords = {}
	BS_list = {}
	BS_list_reverse = {}
	BS_links_len = {}
	line_locat_data = {}
	line_busstop_locat = {}
	line_locat_counter = {}
	line_number_list = []
	line_start_values = {}
	bus_locat_state = {}
	bus_BS_counter = {}
	BS_rtat_value = {}
	line_number_gui_offset = {}

	line_locat_reso = 5
	area_pixel_size = 10
	bus_speed_mpers = 0

	logs_size_counter = 0
	logs_event_counter = 0
	logs_event_login_counter = 0
	logs_event_logout_counter = 0
	logs_event_locat_counter = 0
	logs_event_rtat_counter = 0
	logs_event_ad_counter = 0

	color_list_counter = 0
	color_list = [QColor(255,0,0,127),
				  QColor(0,255,0,127),
				  QColor(0,0,255,127),
				  QColor(255,0,255,127),
				  QColor(0,255,255,127),
				  QColor(0,0,0,127)]

	def __init__(self,size,
				event_versatility,traces_max,
				busstops_matrix,busstops_area,
				busstops_A,busstops_B,busstop_size,
				line_locat_reso,line_route_list,
				output_path,log_name,gui_enable,gui):

		self.event_versatility = event_versatility
		self.traces_max = traces_max	
		self.output_path = output_path
		self.log_name = log_name
		self.gui_enable = gui_enable

		if gui_enable == 1:
			self.qp = gui.qp
			self.gui = gui

		print("")

		# Alustetaan p��te-pysakkien paikat
		area_x,area_y=size.split("x")

		# Piirret��n koko alue GUI:hin
		if self.gui_enable == 1:
			#self.gui.draw_box(self.qp,0,int(area_y),int(area_x),int(area_y),"Area")
			self.gui.draw_box(self.qp,"",0,0,int(area_x),int(area_y),Qt.yellow,"Area")

		matrix_x,matrix_y=busstops_matrix.split("x")
		self.matrix_x=matrix_x
		self.matrix_y=matrix_y

		busstops_x,busstops_y=busstops_area.split("x")
		#print("busstops_x=%s, busstops_y=%s" % (busstops_x,busstops_y))

		busstop_size_x,busstop_size_y=busstop_size.split("x")

		if busstops_A < 2:
			dist_y_A = int(area_y)
		else:	
			dist_y_A = int(area_y) / (busstops_A - 1)
		if busstops_B < 2:			
			dist_y_B = int(area_y)
		else:
			dist_y_B = int(area_y) / (busstops_B - 1)
		print("dist_y_A=%d, dist_y_B=%d" % (dist_y_A,dist_y_B) )
		print("")

		print("BS_A coordinates:")
		for i in range(0,busstops_A):
			y=int(i*dist_y_A)
			self.BS_A_coords[i] = [0,y]
			index = "A%d" % (i+1)
			self.BS_coords[index] = [0,y]

			# Lasketaan pys�kkialueiden nurkkapisteiden koordinaatit
			self.BS_area_coords[index] =  self.calculate_BS_area_coords(busstop_size,0,y,index )

			print("%d: %3s: %-15s: %s" % (i,index,self.BS_A_coords[i],self.BS_area_coords[index]))

		print("")
		print("BS_B coordinates:")
		for i in range(0,busstops_B):
			y=int(i*dist_y_B)
			self.BS_B_coords[i] = [int(area_x),y]
			index = "B%d" % (i+1)
			self.BS_coords[index] = [int(area_x),y]

			# Lasketaan pys�kkialueiden nurkkapisteiden koordinaatit
			self.BS_area_coords[index] =  self.calculate_BS_area_coords(busstop_size,int(area_x),y,index )

			print("%d: %3s: %-15s: %s" % (i,index,self.BS_B_coords[i],self.BS_area_coords[index]))

		print("")

		# Alustetaan monitori-pysakkien paikat

		area_center_x = int(area_x) / 2
		area_center_y = int(area_y) / 2
		print("area_center_x=%d, area_center_y=%d" % (area_center_x,area_center_y) )

		if int(matrix_x) < 2:
			dist_x_matrix = int(busstops_x)
		else:
			dist_x_matrix = int(busstops_x) / (int(matrix_x) - 1)

		if int(matrix_y) < 2:
			dist_y_matrix = int(busstops_y)
		else:
			dist_y_matrix = int(busstops_y) / (int(matrix_y) - 1)

		print("dist_x_matrix=%d, dist_y_matrix=%d" % (dist_x_matrix,dist_y_matrix) )

		matrix_x_start_coord = area_center_x - int(busstops_x) / 2
		matrix_y_start_coord = area_center_y - int(busstops_y) / 2
		print("matrix_x_start_coord=%d, matrix_y_start_coord=%d" % (matrix_x_start_coord,matrix_y_start_coord) )

		print("")
		print("BS_M coordinates:")
		BS_M_counter = 1
		for i in range(0,int(matrix_x)):
			x=int(i*dist_x_matrix) + matrix_x_start_coord
			for j in range(0,int(matrix_y)):
				y=int(j*dist_y_matrix) + matrix_y_start_coord
				self.BS_M_coords[BS_M_counter] = [x,y]
				index = "M%d" % BS_M_counter
				self.BS_coords[index] = [x,y]

				# Lasketaan pys�kkialueiden nurkkapisteiden koordinaatit
				self.BS_area_coords[index] =  self.calculate_BS_area_coords(busstop_size,x,y,index )

				print("%d: %3s: %-15s: %s" % (BS_M_counter,index,self.BS_M_coords[BS_M_counter],self.BS_area_coords[index]))
				BS_M_counter += 1

		# Lasketaan linjojen piirt�misen offset-arvot (ett� linjat ei mene p��llekk�in)
		if self.gui_enable == 1:
			self.calculate_gui_line_offsets(line_route_list)

		self.line_number_list = []

		# Lasketaan linjojen reitit ja linkkien pituudet
		for line_route in line_route_list:

			#print("line_route: %s" % line_route)
			line_number, line_color, line_start, line_busstops = line_route.split(":")
			self.line_number_list.append(line_number)
			print("line: %s start:%s bs:%s" % (line_number, line_start, line_busstops))
			self.line_start_values[line_number] = line_start
			self.BS_list[line_number] = line_busstops.split(",")
			self.BS_list_reverse[line_number] = line_busstops.split(",")
			self.BS_list_reverse[line_number].reverse()
			print("A: %s" % self.BS_list[line_number])
			#print("B: %s" % self.BS_list_reverse[line_number])
			BS_counter = 0
			line_BS_prev = ""
			line_total_len = 0
			self.line_locat_counter[line_number] = 0

			# K�yd��n linjan pys�kit l�pi
			for line_BS in self.BS_list[line_number] :
				if BS_counter > 0:
					# Lasketaan linkin data, kuten koordinaatit ja pituus
					link_len = int(self.calculate_link_data(line_number,line_color,line_locat_reso,line_BS_prev,line_BS))
					#print("  link_len = %s" % link_len)
					print("Link: %s - %s, link_len = %s" % (line_BS_prev,line_BS,link_len))
					line_total_len += link_len
					self.BS_links_len[line_BS_prev,line_BS]=link_len

				BS_counter += 1
				line_BS_prev = line_BS
				#print("  %s" % line_BS)

			print("line: %s total link_len = %s\n" % (line_number,line_total_len))
			print("")

	def calculate_gui_line_offsets(self,line_route_list):

		# Lasketaan offsetit linjoille, ett� v�ltet��n linjojen p��llekk�isyys samalla linkill�
		line_line_width = 4
		line_list_len = len(line_route_list)

		offset_shift = 0
		# Jos parillinen m��r� linjoja
		if line_list_len % 2 == 0:
			# Lis�t��n offsetti� puolella linjan paksuudella
			offset_shift = int(line_line_width / 2.0)

		lines_width = line_line_width * line_list_len
		offset_index = int(lines_width / 2.0) - lines_width + offset_shift
		print("line_list_len=%s, offset_index=%s" % (line_list_len,offset_index))
		for line_route in line_route_list:
			line_number, line_color, line_start, line_busstops = line_route.split(":")
			self.line_number_gui_offset[line_number] = offset_index
			print("offset_index=%s for line_number=%s" % (offset_index,line_number))
			offset_index += line_line_width

	def calculate_BS_area_coords(self,busstop_size,x,y,index):

		busstop_size_x,busstop_size_y=busstop_size.split("x")

		busstop_size_x_int = int(busstop_size_x)
		busstop_size_y_int = int(busstop_size_y)

		# Lasketaan pys�kkialueiden nurkkapisteiden (oikea alakulma ja vasen yl�kulma) koordinaatit
		x_right = x + int(busstop_size_x_int / 2)
		x_left  = x - int(busstop_size_x_int / 2)
		y_top   = y + int(busstop_size_y_int / 2)
		y_down  = y - int(busstop_size_y_int / 2)

		# Vaihdetaan tiedoston y-suunnan reunakoordinaatit, koska useimmiten origo on vasemmassa alanurkassa 
		# (toisin kuten tässä ohjelmassa PyQt:n QPainter:ssa)
		y_top_file   = y_down 
		y_down_file  = y_top

		# Kirjoitetaan tiedostoon
		file_name = "area_coords"
		datafile_name = self.output_path + self.log_name + "/" + file_name + "_" + index + ".csv"
		self.make_dir_if_no_exist(datafile_name)
		f = open(datafile_name, 'w')
		str = "Counter,Longitude,Latitude\n"
		f.writelines(str)
		str = "1,%s,%s\n" % (x_left,y_top_file)	
		f.writelines(str)
		str = "2,%s,%s\n" % (x_right,y_top_file)	
		f.writelines(str)
		str = "3,%s,%s\n" % (x_right,y_down_file)	
		f.writelines(str)
		str = "4,%s,%s\n" % (x_left,y_down_file)	
		f.writelines(str)
		f.close()

		# Piirret��n pys�kkialueet GUI:hin
		if self.gui_enable == 1:
			#draw_text = "Bus: x=%s, y=%s, ind=%s " % (x_right,y_down,index)
			draw_text = "%s " % (index)
			self.gui.draw_box(self.qp,"",x_left,y_down,int(busstop_size_x),int(busstop_size_y),Qt.yellow,draw_text)

		return [x_right,y_down,x_left,y_top]

	def check_BS_area_coords(self,BS,x,y):

		try:
			x_top,y_left,x_down,y_right = self.BS_area_coords[BS]
		except:
			print("ERR: check_BS_area_coords: Not found busstop: %s" % BS)
			sys.exit()

		#print("check_BS_area_coords: x=%d, y=%d: x_top=%s, y_left=%d, x_down=%d, y_right=%d" % (x,y,x_top,y_left,x_down,y_right))

		# Tarkistetaan onko koordinaatti alueen sis�ll�
		if x < x_top:
			if x > x_down:
				if y > y_left:
					if y < y_right:
						return True
		return False

	def calculate_link_data(self,line_number,line_color,line_locat_reso,line_BS_prev,line_BS):
		#print("calculate_link_data for busstops: %s %s " % (line_BS_prev,line_BS))

		# Haetaan edellisen pys�kin koordinaatit
		try:
			coords_prev = self.BS_coords[line_BS_prev]
		except:
			print("ERR: Not found coords for previous busstop: %s\n" % line_BS_prev)
			sys.exit()

		# Haetaan nykyisen pys�kin koordinaatit
		try:
			coords = self.BS_coords[line_BS]
		except:
			print("ERR: Not found coords for current busstop: %s\n" % line_BS)
			sys.exit()

		#print("Prev coords: %s, coords: %s" % (coords_prev,coords))

		# Lasketaan pys�kkien v�lisen linkin pituus
		x_prev = coords_prev[0]
		y_prev = coords_prev[1]
		x = coords[0]
		y = coords[1]
		#print("prev coords: %s %s, coords: %s %s" % (x_prev,y_prev,x,y))

		# Piirret��n pys�kin linjan linkki GUI:hin
		if self.gui_enable == 1:

			offset = self.line_number_gui_offset[line_number]
			str = "%s" % (line_number)

			line_x1 = x_prev + offset
			line_y1 = y_prev + offset
			line_x2 = x + offset
			line_y2 = y + offset
			#self.gui.draw_line(self.qp,x_prev,y_prev,x,y,str,line_color)

			if line_color == "green":
				self.gui.draw_line(self.qp,line_x1,line_y1,line_x2,line_y2,str,Qt.green)
			elif line_color == "red":
				self.gui.draw_line(self.qp,line_x1,line_y1,line_x2,line_y2,str,Qt.red)
			elif line_color == "magenta":
				self.gui.draw_line(self.qp,line_x1,line_y1,line_x2,line_y2,str,Qt.magenta)
			elif line_color == "black":
				self.gui.draw_line(self.qp,line_x1,line_y1,line_x2,line_y2,str,Qt.black)
			elif line_color == "yellow":
				self.gui.draw_line(self.qp,line_x1,line_y1,line_x2,line_y2,str,Qt.yellow)
			else:
				self.gui.draw_line(self.qp,line_x1,line_y1,line_x2,line_y2,str,Qt.blue)

			#self.gui.draw_line(self.qp,line_x1,line_y1,line_x2,line_y2,str,line_color)

		x_diff = x - x_prev
		y_diff = y - y_prev
		link_len = math.sqrt(math.pow(x_diff,2) + math.pow(y_diff,2))
		#print("link_len = %s" % link_len)

		# Lasketaan my�s linkin kaikki mahdolliset (bussin) koordinaatit valmiiksi
		link_locat_counter = 0
		for i in range(0,int(link_len),line_locat_reso):
			link_locat_counter += 1
			self.line_locat_counter[line_number] += 1
			x_bus = int(x_prev + ( x_diff / link_len ) * i)
			y_bus = int(y_prev + ( y_diff / link_len ) * i)

			#print("%4d: %4d: x:%5d y:%5d" % (self.line_locat_counter[line_number],link_locat_counter,x_bus,y_bus))

			# Talletaan linkin koordinaatit linjan dataan
			self.line_locat_data[line_number,self.line_locat_counter[line_number]] = [x_bus,y_bus]

			# Piirret��n pys�kin linjan piste GUI:hin
			if self.gui_enable == 1:
				str = "%5d,%s,%s\n" % (i,x_bus,y_bus)
				#self.gui.draw_point(self.qp,x_bus,y_bus,str,Qt.black)
				self.gui.draw_circle(self.qp,x_bus,y_bus,5,str,Qt.black)

		# Talletaan pys�kin paikka linjalla
		self.line_busstop_locat[line_number,line_BS] = self.line_locat_counter[line_number]
		print("line_busstop_locat: line: %s, busstop: %s, locat: %s" % (line_number,line_BS,self.line_busstop_locat[line_number,line_BS]))

		return link_len

	def generate_test_lines(self,file_name):

		#line_counter = 0
		for line in self.line_number_list:

			#line_counter += 1
			#print("print_line_coords for line: %s" % line)

			logfile_name = self.output_path + self.log_name + "/" + file_name + "_" + line + ".csv"
			#os.makedirs(os.path.dirname(logfile_name), exist_ok=True)
			self.make_dir_if_no_exist(logfile_name)
			f = open(logfile_name, 'w')

			try:
				locat_counter = self.line_locat_counter[line]
			except:
				print("ERR: Not found locat-counter for line: %s\n" % line)
				sys.exit()

			print("print_line_coords: for line: %s, %s" % (line,locat_counter))
			for i in range(1,locat_counter):
				try:
					coords = self.line_locat_data[line,i]
				except:
					print("ERR: Not found coords for index: %d and line: %s\n" % (i,line))
					sys.exit()

				x = coords[0]
				y = coords[1]
				str = "%5d,%s,%s\n" % (i,x,y)
				#print("%s" % str)
				f.writelines(str)

				# Piirret��n pys�kin linjan piste GUI:hin
				#if self.gui_enable == 1:
				#	self.gui.draw_point(self.qp,x,y,str,Qt.black)


			f.close()

	def generate_bus_runs(self,date,start_time,stop_time,line_locat_reso,area_pixel_size,
				 bus_msg_interval,bus_speed,bus_speed_variance,bus_amount,single_log,debug,gui,gui_info_enable,source,trace_mode):

		bus_line = {}
		bus_state = {}
		#bus_locat_state = {}
		bus_direction = {}
		bus_line_locat = {}
		logfile_name = {}
		f = {}
		line_for_bus = {}
		bus_stay_counter = {}
		bus_wait_counter = {}
		bus_wait_limit = {}
		trace_counter = 0

		self.color_list_counter = 0

		# Yhden tracen tiedot piirtämistä varten
		self.trace_pos_login = {}
		self.trace_pos_logout = {}
		self.trace_pos_locat_start = {}
		self.trace_pos_locat_bs = {}
		self.trace_pos_rtat = {}
		self.trace_pos_ad = {}

		self.trace_pos_rtat_counter = {}
		self.trace_pos_ad_counter = {}
		self.trace_pos_locat_bs_counter = {}
		self.trace_pos_locat_bs_last_ad = {}

		self.line_locat_reso = line_locat_reso
		self.area_pixel_size = area_pixel_size

		self.bus_color = {}

		self.trace_mode = trace_mode

		self.debug = debug
		self.gui_info_enable = gui_info_enable

		self.single_log = single_log

		if self.gui_enable == 1:
			self.qp = gui.qp
			self.gui = gui
			self.source = source


		self.logs_size_counter = 0
		self.logs_event_counter = 0
		self.logs_event_login_counter = 0
		self.logs_event_logout_counter = 0
		self.logs_event_locat_counter = 0
		self.logs_event_rtat_counter = 0
		self.logs_event_ad_counter = 0

		self.logs_event_locat_bus_counter = {}

		print("")
		print("Starts generate")
		generate_start_time = time.time()

		self.bus_speed_mpers = bus_speed / 3.6
		bus_speed_variance_mpers = bus_speed_variance / 3.6
		print("Bus speed = %.1f km/h = %.1f m/s" % (bus_speed,self.bus_speed_mpers))
		print("Bus speed variance = %.1f km/h = %.1f m/s" % (bus_speed_variance,bus_speed_variance_mpers))
		print("")

		print("")
		print("bus_amount: %s" % (bus_amount))

		# M��ritet��n bussien m��r�t linjoille
		bus_counter = 0
		for line in self.line_number_list:
			for bus in range(1,bus_amount+1):
				bus_counter += 1
				line_for_bus[bus_counter] = line
				print("Line: %s: bus: %s" % (line,bus_counter))
		print("")

		# Jos kaikki kirjoitetaan samaan lokiin
		if single_log == 1:

			single_log_name = self.output_path + self.log_name + "/" + "single_log" + ".csv"
			self.make_dir_if_no_exist(single_log_name)
			print("SINGLE log file: %s" % (single_log_name))
			f_single_log = open(single_log_name, 'w')

		# Alustetaan bussien tiedot ja lokitiedostot
		print("Bus log files:")
		for bus in range(1,bus_counter+1):
			bus_line[bus] = line_for_bus[bus]
			#bus_state[bus] = "LOGIN"
			bus_state[bus] = "WAIT_START"
			bus_stay_counter[bus] = 0
			bus_wait_counter[bus] = 0

			if self.gui_enable == 1 and self.source == "Log":

				# Värin valinta listalta
				color = self.color_list[self.color_list_counter]
				self.bus_color[bus] = color
				self.color_list_counter += 1
				if self.color_list_counter >= len(self.color_list):
					self.color_list_counter = 0

			# Bussin haarautuvien tapahtumien laskurien nollaus
			self.trace_pos_rtat_counter[bus] = 0
			self.trace_pos_ad_counter[bus] = 0
			self.trace_pos_locat_bs_counter[bus] = 0

			# Linjakohtainen odotusaika päätepysäkillä
			bus_wait_limit[bus] = int(self.line_start_values[bus_line[bus]]) 

			# Alitilakoneen muuttujat
			self.bus_locat_state[bus] = "START_TBS"
			self.bus_BS_counter[bus] = 0

			bus_direction[bus] = "A"
			bus_line_locat[bus] = 0
			if single_log == 1:
				f[bus] = f_single_log
			else:
				logfile_name[bus] = self.output_path + self.log_name + "/" + "bus_coords_" + str(bus) + ".csv"
				self.make_dir_if_no_exist(logfile_name[bus])
				print("%4d: %s" % (bus,logfile_name[bus]))
				f[bus] = open(logfile_name[bus], 'w')

			self.logs_event_locat_bus_counter[bus] = 0

		# Alustetaan muut lokitiedostot
		login_file_name = self.output_path + self.log_name + "/" + "bus_login" + ".csv"
		self.make_dir_if_no_exist(login_file_name)
		print("LOGIN log file : %s" % login_file_name)
		rtat_file_name = self.output_path + self.log_name + "/" + "ccs_rtat" + ".csv"
		self.make_dir_if_no_exist(rtat_file_name)
		print("RTAT log file  : %s" % rtat_file_name)
		ad_file_name = self.output_path + self.log_name + "/" + "ccs_ad" + ".csv"
		self.make_dir_if_no_exist(ad_file_name)
		print("AD log file  : %s" % ad_file_name)
		if single_log == 1:
			f_login = f_single_log
			f_rtat = f_single_log
			f_ad = f_single_log
		else:
			f_login = open(login_file_name, 'w')
			f_rtat = open(rtat_file_name, 'w')
			f_ad = open(ad_file_name, 'w')

		print("")

		self.bus_msg_interval = bus_msg_interval
		t1,t2,loop_counter_max = convert_datetime(date,start_time,stop_time,bus_msg_interval)
		self.t1 = t1

		# P��silmukka
		loop_counter = 0
		while (loop_counter < loop_counter_max):

			loop_counter += 1
			#print("loop: %s" % loop_counter)
			#time.sleep(0.2)

			loop_time,loop_seconds = self.calculate_loop_time(loop_counter,self.bus_msg_interval)

			if debug > 1:
				print("loop_seconds = %s, time = %s" % (loop_seconds,loop_time))

			# K�yd��n bussit l�pi
			for bus in range(1,bus_counter+1):

				# Bussin tilakone

				# Bussi odottaa päätepysäkillä lähtöä
				if bus_state[bus] == "WAIT_START":

					bus_wait_counter[bus] += 1
					if bus_wait_counter[bus] > bus_wait_limit[bus]:
						bus_state[bus] = "LOGIN"				

				# LOGIN-viestit
				elif bus_state[bus] == "LOGIN":

					self.generate_login_message(loop_time,bus,loop_counter,bus_line[bus],bus_direction[bus],f_login)

					bus_state[bus] = "LOCAT"
					self.bus_locat_state[bus] = "OUTSIDE"
					bus_stay_counter[bus] = 0

				# LOCAT-viestit
				elif bus_state[bus] == "LOCAT":

					# Ollaan aluksi paikallaan p��tepys�kill�
					bus_stay_counter[bus] += 1
					if bus_stay_counter[bus] > 3:

						# Lasketaan bussin kulkema matka
						dist,locat_steps,bus_speed_real_mpers = self.calculate_distance(self.bus_speed_mpers,bus_speed_variance_mpers,
																bus_msg_interval,line_locat_reso,area_pixel_size)
					else:
						dist = 0
						locat_steps = 1
						bus_speed_real_mpers = 0
						if self.debug > 0:
							print("Stay: %s, %s" % (bus,bus_stay_counter[bus]))

					change_direction = False
					if bus_direction[bus] == "A":
						bus_line_locat_new = bus_line_locat[bus] + locat_steps
						# Tarkistetaan ollaanko tultu linjan p��h�n
						if bus_line_locat_new > self.line_locat_counter[bus_line[bus]]:
							bus_line_locat_new = self.line_locat_counter[bus_line[bus]]
							change_direction = True
					else:
						bus_line_locat_new = bus_line_locat[bus] - locat_steps
						# Tarkistetaan ollaanko tultu linjan p��h�n
						if bus_line_locat_new < 1:
							bus_line_locat_new = 1
							change_direction = True

					# Tarkistetaan ollaanko tultu linjan p��h�n
					if change_direction == True:
						# Suunnan vaihto
						if bus_direction[bus] == "A":
							bus_direction[bus] = "B"
						else:
							bus_direction[bus] = "A"
						bus_state[bus] = "LOGOUT"
						self.bus_locat_state[bus] = "OUTSIDE"
						self.bus_BS_counter[bus] = 0
						if self.debug > 0:
							print("%s: Bus: %s, Change direction to %s" % (loop_time,bus,bus_direction[bus]))

					else:
						# Tarkistetaan bussin ajo: pys�keilt� l�htemiset ja tulemiset
						self.check_bus_driving(loop_time,loop_counter,bus,bus_line[bus],bus_direction[bus],bus_line_locat_new,f_rtat,f_ad)

					bus_line_locat[bus] = bus_line_locat_new

					# Haetaan ko. paikan koordinaatit linja-tiedoista
					try:
						coords = self.line_locat_data[bus_line[bus],bus_line_locat[bus]]
					except:
						print("Bus: %s, ERR: Not found coords for index: %d and line: %s\n" % (bus,bus_line_locat[bus],bus_line))
						sys.exit()

					if debug > 1:
						print("Bus: %s, %5d: Speed: %3.1f m/s, Dist: %4.1f m, Steps: %d, LOCAT: %s, %s" %
								(bus,loop_counter,bus_speed_real_mpers,dist,locat_steps,bus_line_locat[bus],coords))

					# LOCAT-viestin generointi
					x = coords[0]
					y = coords[1]
					self.generate_locat_message(loop_time,bus,loop_counter,x,y,f[bus])

				# LOGOUT-viestit
				else:

					# LOGOUT-viestin generointi
					self.generate_logout_message(loop_time,bus,loop_counter,bus_line[bus],"-",f_login)

					# Piirretään bussin tapahtumien trace
					if self.gui_enable == 1 and self.source == "Log":
						self.draw_bus_trace(bus)

					# Tarkisteaan ollaanko saavutettu maksimi lukumäärä traceille
					trace_counter += 1
					if trace_counter > self.traces_max:
						print("Max traces: %s, stops" % self.traces_max)
						loop_counter = loop_counter_max
						#break

					#bus_state[bus] = "LOGIN"
					bus_state[bus] = "WAIT_START"
					bus_wait_counter[bus] = 0

					# Bussin haarautuvien tapahtumien laskurien nollaus
					self.trace_pos_rtat_counter[bus] = 0
					self.trace_pos_ad_counter[bus] = 0
					self.trace_pos_locat_bs_counter[bus] = 0

					# Linjakohtainen odotusaika päätepyskillä. Voisi tehdä fiksummin !!?? Jotenkin aikatauluun liittyen ?
					bus_wait_limit[bus] = 2 + random.randrange(4)

		# Suljetaan lokitiedostot
		if single_log == 1:
			f_single_log.close()
		else:
			# Suljetaan bussien lokitiedostot
			for bus in range(1,bus_counter+1):
				f[bus].close()

			# Suljetaan muut lokitiedostot
			f_login.close()
			f_rtat.close()
			f_ad.close()

		print("Stops generate\n")

		print("Generated logs size     = %9d bytes\n" % self.logs_size_counter) 
		print("Generated login events  = %9d" % self.logs_event_login_counter) 
		print("Generated logout events = %9d" % self.logs_event_logout_counter) 
		print("Generated locat events  = %9d" % self.logs_event_locat_counter) 
		for bus in range(1,bus_counter+1):
			print(" Bus: %3d locat events  = %9d" % (bus,self.logs_event_locat_bus_counter[bus]))
		print("Generated rtat_events   = %9d" % self.logs_event_rtat_counter) 
		print("Generated ad_events     = %9d" % self.logs_event_ad_counter) 
		print("Generated events all    = %9d" % self.logs_event_counter) 
		print("Generated traces        = %9d (max %s)" % (trace_counter,self.traces_max)) 

		print("\nExecution time of generating: %.3f seconds" % (time.time() - generate_start_time))

	def calculate_loop_time(self,loop_counter,bus_msg_interval):

		loop_seconds = loop_counter * bus_msg_interval
		loop_time = self.t1 + timedelta(seconds=loop_seconds)
		return loop_time,loop_seconds

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

	def calculate_distance(self,bus_speed_mpers,bus_speed_variance_mpers,
						bus_msg_interval,line_locat_reso,area_pixel_size):

		# Lasketaan bussin kulkema matka
		speed_variance = random.randrange(int(bus_speed_variance_mpers))
		#print("speed_variance = %s" % speed_variance)
		bus_speed_real_mpers = bus_speed_mpers - speed_variance
		dist = bus_msg_interval * bus_speed_real_mpers
		locat_steps	= int(dist / (line_locat_reso * area_pixel_size))
		#print("locat_steps = %s" % locat_steps)

		return dist,locat_steps,bus_speed_real_mpers

	def check_bus_driving(self,loop_time,loop_counter,bus,line_number,bus_direction,bus_locat,f_rtat,f_ad):

		# Haetaan pys�kit ajosuunnan mukaisessa j�rjestyksess�
		if bus_direction == "A":
			busstop_list = self.BS_list[line_number]
		else:
			busstop_list = self.BS_list_reverse[line_number]
		busstop_list_len = len(busstop_list)
		#print("busstop_list_len=%d" % busstop_list_len)

		#line_locats = self.line_locat_counter[line_number]

		# Muutetaan linjan indeksi (x,y) koordinaateiksi
		x_bus,y_bus = self.line_locat_data[line_number,bus_locat]

		# Haetaan pys�kki sen indeksin perusteella, jos l�ytyy
		try:
			next_BS = busstop_list[self.bus_BS_counter[bus]]
		except:
			print("check_bus_driving: ERR: Not found busstop by counter: %s" % self.bus_BS_counter[bus])
			return

		# Tutkitaan ollaanko pys�kkialueen sis�ll�
		ret_inside = self.check_BS_area_coords(next_BS,x_bus,y_bus)

		# Bussin liikkumisen(ali)tilakone

		# Pys�kkialueen ulkopuolella -tila
		if self.bus_locat_state[bus] == "OUTSIDE":

			# Jos bussi pys�kkialueen sis�puolella
			if ret_inside == True:
				if self.debug > 0:
					print("INSIDE : %s: Bus: %s Busstop: %s, count: %d, locat: %s" % (loop_time,bus,next_BS,self.bus_BS_counter[bus],bus_locat))
				self.bus_locat_state[bus] = "INSIDE"

				# Paikkojen n�ytt�minen GUI:ssa
				if self.gui_enable == 1:
					str = "%s, %s, %s, %s\n" % (loop_time,bus,x_bus,y_bus)
					if self.source == "Area":
						if self.gui_info_enable > 0:
							# Huom! T�m� laittaa nurkkapisteen mukaan, ei keskipisteen !!
							self.gui.draw_box(self.qp,"Fill",x_bus,y_bus-20,8,8,Qt.yellow,"I")
						

				# Tarkistetaan miten ennustus on toiminut M-pys�keill�. T�m� vain testi� varten !!
				if next_BS[0] == "M":
					time_diff = loop_time - self.BS_rtat_value[next_BS]
					if self.debug > 0:
						print("ESTIMAT: %s, diff: %s" % (self.BS_rtat_value[next_BS],time_diff))

					if self.gui_enable == 1 and self.source == "Log":
						self.gui.drawLogEvent(self.qp,1,loop_counter,"boxA")

						#self.trace_pos_locat_bs[bus] = loop_counter

						# Monen pysäkilletulon tapahtumat talteen 
						self.trace_pos_locat_bs[bus,self.trace_pos_locat_bs_counter[bus]] = loop_counter

						# Viimeinen bussin AD-viesti myös talteen
						last_ad_ind = self.trace_pos_ad_counter[bus] - 1
						self.trace_pos_locat_bs_last_ad[bus,self.trace_pos_locat_bs_counter[bus]] = last_ad_ind

						self.trace_pos_locat_bs_counter[bus] += 1

			else:
				# Jos kohdepys�kki M-pys�kki
				if next_BS[0] == "M":

					# Lasketaan vain joka 5. kerralla. Voisi olla tehty fiksumminkin ?!
					if loop_counter % 5 == 0:

						# Bussin et�isyys ja ajoaika pys�kille
						locat_diff_m,bus_run_time_sec = self.calculate_time_to_busstop(line_number,next_BS,bus_locat)

						# Lasketaan uusi arvioitu saapumisaika
						rtat_value_new = loop_time + timedelta(seconds=bus_run_time_sec)

						# Alkuper�inen arvioitu saapumisaika
						rtat_value_orig = self.BS_rtat_value[next_BS]

						# Paljon nykyinen saapumisaika eroaa arvioidusta: AD-arvo
						rtat_diff = rtat_value_new - rtat_value_orig
						rtat_diff_sec = rtat_diff.seconds

						# PIT�ISI LASKEA BROADCAST_TYYPPISESTI KAIKILLE TULEVILLE PYS�KEILLE ??!!

						# MILLOIN LASKETAAN JA L�HETET��N ??

						# Generoidaan AD-viesti M-pys�keille
						self.generate_ad_message(loop_time,loop_counter,bus,line_number,
								bus_direction,rtat_diff_sec,bus_locat,f_ad)

						if self.debug > 0:
							print("OUTSIDE: Next M: %s, %s, %s m, %s s, rtat %s, diff %s %s s" % (next_BS,bus_locat,locat_diff_m,bus_run_time_sec,rtat_value_new,rtat_diff,rtat_diff_sec))

		# Pys�kkialueen sis�puolella -tila
		elif self.bus_locat_state[bus] == "INSIDE":

			# Jos bussi pys�kkialueen ulkopuolella
			if ret_inside == False:

				# Seuraava pys�kki
				if self.bus_BS_counter[bus] < busstop_list_len-1:
					self.bus_BS_counter[bus] += 1
					self.bus_locat_state[bus] = "OUTSIDE"
					if self.debug > 0:
						print("OUTSIDE: %s: Bus: %s Busstop: %s, count: %d, locat: %s" % (loop_time,bus,next_BS,self.bus_BS_counter[bus],bus_locat))

					# Paikkojen n�ytt�minen GUI:ssa
					if self.gui_enable == 1:
						if self.source == "Area":
							if self.gui_info_enable > 0:
								str = "%s, %s, %s, %s\n" % (loop_time,bus,x_bus,y_bus)
								# Huom! T�m� laittaa nurkkapisteen mukaan, ei keskipisteen !!
								self.gui.draw_box(self.qp,"Fill",x_bus,y_bus-20,8,8,Qt.yellow,"O")
						#else:
						#	self.gui.drawLogEvent(self.qp,1,loop_counter,"boxA")
							#self.trace_pos_locat_start[bus] = loop_counter

					# Jos l�hdettiin p��tepys�kilt�
					if next_BS[0] != "M":
						#print("  Leaving from TBS")

						# Generoidaan RTAT-viestit kaikille M-pys�keille
						# Laitetaan vähän lisää aikaa "käsin", että viestin aikaleima isompi kuin LOCAT-viestin (pysäkiltä lähtö)
						loop_counter_rtat = loop_counter + 2
						loop_time_rtat,loop_seconds_rtat = self.calculate_loop_time(loop_counter_rtat,self.bus_msg_interval)
						self.generate_rtat_messages(loop_time_rtat,loop_counter_rtat,bus,line_number,
													bus_direction,busstop_list,bus_locat,f_rtat)

						# Paikkojen n�ytt�minen GUI:ssa
						if self.gui_enable == 1:
							if self.source == "Area":
								str = "%s, %s, %s, %s\n" % (loop_time,bus,x_bus,y_bus)
								#self.gui.draw_box(self.qp,"Fill",x_bus,y_bus+10,10,str)
								if self.gui_info_enable > 0:
									# Huom! T�m� laittaa nurkkapisteen mukaan, ei keskipisteen !!
									self.gui.draw_box(self.qp,"Fill",x_bus,y_bus+10,8,8,Qt.yellow,"R")
							else:
								self.gui.drawLogEvent(self.qp,1,loop_counter,"boxB")
								self.trace_pos_locat_start[bus] = loop_counter

		#print("Bus: %s, Locat: %s, Line: %s, Dir: %s, Busstops = %s" % (bus,bus_locat,line_number,bus_direction,busstop_list))

	def draw_bus_trace(self,bus):

		# Värin valinta listalta
		#color = self.color_list[self.color_list_counter]	
		#self.color_list_counter += 1
		#if self.color_list_counter >= len(self.color_list):
		#	self.color_list_counter = 0

		# Käytetään bussikohtaista väriä
		color = self.bus_color[bus]

		rtat_counter = self.trace_pos_rtat_counter[bus] - 1
		ad_counter = self.trace_pos_ad_counter[bus] - 1
		locat_bs_counter = self.trace_pos_locat_bs_counter[bus]

		# Piiretään yhden bussin ajo-trace login:sta logout:iin

		self.gui.drawLogTraceLine(self.qp,0,self.trace_pos_login[bus],1,self.trace_pos_locat_start[bus],color)

		self.gui.drawLogTraceLine(self.qp,1,self.trace_pos_locat_start[bus],2,self.trace_pos_rtat[bus,rtat_counter],color)
		#self.gui.drawLogTraceLine(self.qp,1,self.trace_pos_locat_start[bus],2,self.trace_pos_rtat[bus],color)

		#self.gui.drawLogTraceLine(self.qp,2,self.trace_pos_rtat[bus,rtat_counter],3,self.trace_pos_ad[bus,ad_counter],color)
		#self.gui.drawLogTraceLine(self.qp,2,self.trace_pos_rtat[bus],3,self.trace_pos_ad[bus],color)

		#print("trace_mode: %s" % self.trace_mode)

		if self.trace_mode == "ALL_traces":
			# Piirretään kaikki RTAT:sta lähtevät tracet
			# locat_bs_counter pitäisi olla sama kuin rtat_counter !?
			for i in range(locat_bs_counter):

				last_ad_pos = self.trace_pos_locat_bs_last_ad[bus,i] 
				self.gui.drawLogTraceLine(self.qp,2,self.trace_pos_rtat[bus,rtat_counter],3,self.trace_pos_ad[bus,last_ad_pos],color)
				self.gui.drawLogTraceLine(self.qp,3,self.trace_pos_ad[bus,last_ad_pos],1,self.trace_pos_locat_bs[bus,i],color)
				self.gui.drawLogTraceLine(self.qp,1,self.trace_pos_locat_bs[bus,i],0,self.trace_pos_logout[bus],color)
		else:

			i = 0
			if self.trace_mode == "LAST_trace":
				i = locat_bs_counter - 1

			last_ad_pos = self.trace_pos_locat_bs_last_ad[bus,i] 
			self.gui.drawLogTraceLine(self.qp,2,self.trace_pos_rtat[bus,rtat_counter],3,self.trace_pos_ad[bus,last_ad_pos],color)
			self.gui.drawLogTraceLine(self.qp,3,self.trace_pos_ad[bus,last_ad_pos],1,self.trace_pos_locat_bs[bus,i],color)
			self.gui.drawLogTraceLine(self.qp,1,self.trace_pos_locat_bs[bus,i],0,self.trace_pos_logout[bus],color)

	
	def generate_login_message(self,loop_time,bus,loop_counter,bus_line,bus_direction,f_login):


		self.logs_event_counter += 1
		self.logs_event_login_counter += 1

		# Generoidaan otsikkorivi
		if self.logs_event_login_counter == 1 and self.single_log == 0:
			str_header = ""
			if self.event_versatility > 1:
				str_header = "%s,%s,%s,LOG-TYPE,%s,%s" % ("LOG-TIME","LOG-BUS","LOG-LOOP-CNT","LOG-LINE","LOG-LINE-DIR")
			else:
				str_header = "%s,%s,LOG-TYPE,%s,%s" % ("LOG-BUS","LOG-LOOP-CNT","LOG-LINE","LOG-DIR")	
			f_login.writelines(str_header + "\n")

		# Generoidaan LOGIN-viesti
		str_login = ""
		if self.event_versatility > 1:
			str_login = "%s,%s,%d,LOGIN,%s,%s" % (loop_time,bus,loop_counter,bus_line,bus_direction)
		else:
			str_login = "%s,%d,LOGIN,%s,%s" % (bus,loop_counter,bus_line,bus_direction)			
		
		f_login.writelines(str_login + "\n")
		self.logs_size_counter += len(str_login)
		if self.debug > 0:
			print("%s" % str_login)

		if self.gui_enable == 1 and self.source == "Log":
			self.gui.drawLogEvent(self.qp,0,loop_counter,"boxA")

			self.trace_pos_login[bus] = loop_counter


	def generate_logout_message(self,loop_time,bus,loop_counter,bus_line,bus_direction,f_login):

		self.logs_event_counter += 1
		self.logs_event_logout_counter += 1

		# Generoidaan otsikkorivi
		#if self.logs_event_logout_counter == 1 and self.single_log == 0:
		#	str_header = ""
		#	if self.event_versatility > 1:
		#		str_header = "%s, %s, %s, LOG, %s, %s" % ("loop_time","bus","loop_counter","bus_line","bus_direction")
		#	else:
		#		str_header = "%s, %s, LOG, %s" % ("bus","loop_counter","bus_line")
		#	f_login.writelines(str_header + "\n")

		# Generoidaan LOGOUT-viesti
		str_logout = ""
		if self.event_versatility > 1:
			str_logout = "%s,%s,%d,LOGOUT,%s,%s" % (loop_time,bus,loop_counter,bus_line,bus_direction)
		else:
			str_logout = "%s,%d,LOGOUT,%s,%s" % (bus,loop_counter,bus_line,bus_direction)

		f_login.writelines(str_logout + "\n")
		self.logs_size_counter += len(str_logout)

		if self.debug > 1:
			print("%s" % str_logout)

		if self.gui_enable == 1 and self.source == "Log":
			self.gui.drawLogEvent(self.qp,0,loop_counter,"boxB")

			self.trace_pos_logout[bus] = loop_counter

	def generate_locat_message(self,loop_time,bus,loop_counter,x,y,f_bus):

		# Generoidaan LOCAT-viesti
		if self.event_versatility > 2:

			self.logs_event_counter += 1
			self.logs_event_locat_counter += 1
			self.logs_event_locat_bus_counter[bus] += 1

			# Generoidaan otsikkorivi
			if self.logs_event_locat_bus_counter[bus] == 1 and self.single_log == 0:
				str_header = "%s,%s,%s,LOCAT,%s,%s\n" % ("LOCAT-TIME","LOCAT-BUS","LOCAT-LOOP-CNT","LOCAT-X","LOCAT-Y")
				f_bus.writelines(str_header + "\n")

			str_locat = "%s,%s,%s,LOCAT,%s,%s\n" % (loop_time,bus,loop_counter,x,y)
			f_bus.writelines(str_locat)
			self.logs_size_counter += len(str_locat)


		#if self.gui_enable == 1 and self.source == "Log":
		#	self.gui.drawLogEvent(self.qp,1,loop_counter,"circle")

		#	self.trace_locat_counter += 1
		#	self.trace_pos_locat[self.trace_locat_counter] = loop_counter

		# Paikkojen n�ytt�minen GUI:ssa
		#if self.gui_enable == 1:
		#	str = "%s, %s, %s, %s\n" % (loop_time,bus,x,y)
		#	self.gui.draw_point(self.qp,x,y,str,"yellow")

	def generate_rtat_messages(self,loop_time,loop_counter,bus,line_number,
							bus_direction,busstop_list,bus_locat,f_rtat):

		# Käydään läpi pysäkit
		for busstop in busstop_list:
			if busstop[0] == "M":

				self.logs_event_counter += 1
				self.logs_event_rtat_counter += 1

				# Generoidaan otsikkorivi
				if self.logs_event_rtat_counter == 1 and self.single_log == 0:
					str_header = ""
					if self.event_versatility > 1:
						str_header = "%s,%s,%s,RTAT,%s,%s,%s,%s" % ("RTAT-TIME","RTAT-BUS","RTAT-LOOP-CNT","RTAT-BUSSTOP","RTAT-VALUE","RTAT-LINE","RTAT-LINE-DIR")
					else:
						str_header = "%s,%s,RTAT,%s,%s,%s,%s" % ("RTAT-BUS","RTAT-LOOP-CNT","RTAT-BUSSTOP","RTAT-VALUE","RTAT-LINE","RTAT-LINE-DIR")
					f_rtat.writelines(str_header + "\n")

				# Bussin et�isyys ja (arvioitu) ajoaika pys�kille
				locat_diff_m,bus_run_time_sec = self.calculate_time_to_busstop(line_number,busstop,bus_locat)

				# Lasketaan arvioitu saapumisaika pys�kille
				rtat_value = loop_time + timedelta(seconds=bus_run_time_sec)
				self.BS_rtat_value[busstop] = rtat_value

				# Generoidaan RTAT-viesti
				str_rtat = ""
				if self.event_versatility > 1:
					str_rtat = "%s,%s,%s,RTAT,%s,%s,%s,%s" % (loop_time,bus,loop_counter,busstop,rtat_value,line_number,bus_direction)
				else:
					str_rtat = "%s,%s,RTAT,%s,%s,%s,%s" % (bus,loop_counter,busstop,rtat_value,line_number,bus_direction)

				f_rtat.writelines(str_rtat + "\n")
				self.logs_size_counter += len(str_rtat)

				if self.debug > 0:
					print("%s" % str_rtat)

			if self.gui_enable == 1 and self.source == "Log":
				self.gui.drawLogEvent(self.qp,2,loop_counter,"circle")

				#self.trace_pos_rtat[bus] = loop_counter

				# Monen RTAT-viestin tapahtumat talteen 
				self.trace_pos_rtat[bus,self.trace_pos_rtat_counter[bus]] = loop_counter
				self.trace_pos_rtat_counter[bus] += 1

	def generate_ad_message(self,loop_time,loop_counter,bus,line_number,
							bus_direction,rtat_diff_sec,bus_locat,f_ad):

			self.logs_event_counter += 1
			self.logs_event_ad_counter += 1	

			# Generoidaan otsikkorivi
			if self.logs_event_ad_counter == 1 and self.single_log == 0:
				str_header = ""
				if self.event_versatility > 1:
					str_header = "%s,%s,%s,AD,%s,%s,%s" % ("AD-TIME","AD-BUS","AD-LOOP-CNT","AD-DIFF","AD-LINE","AD-BUS-DIR")
				else:
					str_header = "%s,%s,AD,%s,%s,%s" % ("AD-BUS","AD-CNT","AD-DIFF","AD-LINE","AD-BUS-DIR")
				f_ad.writelines(str_header + "\n")

			# Generoidaan AD-viesti
			str_ad = ""
			if self.event_versatility > 1:
				str_ad = "%s,%s,%s,AD,%s,%s,%s" % (loop_time,bus,loop_counter,rtat_diff_sec,line_number,bus_direction)
			else:
				str_ad = "%s,%s,AD,%s,%s, s" % (bus,loop_counter,rtat_diff_sec,line_number,bus_direction)
			
			f_ad.writelines(str_ad + "\n")
			self.logs_size_counter += len(str_ad)
		
			if self.debug > 0:
				print("%s" % str_ad)

			if self.gui_enable == 1 and self.source == "Log":

				self.gui.drawLogEvent(self.qp,3,loop_counter,"circle")

				#self.trace_pos_ad[bus] = loop_counter

				# Monen AD-viestin tapahtumat talteen 
				self.trace_pos_ad[bus,self.trace_pos_ad_counter[bus]] = loop_counter
				#print("generate_ad_message: bus=%s, ad_counter=%s, loop_counter=%s" % (bus,self.trace_pos_ad_counter[bus],loop_counter))
				self.trace_pos_ad_counter[bus] += 1



	def calculate_time_to_busstop(self,line_number,busstop,bus_locat):

		# Jos pys�kin tiedot l�ytyiv�t, jatketaan
		try:
			busstop_locat = self.line_busstop_locat[line_number,busstop]
		except:
			print("calculate_time_to_busstop: ERR: Not found: Line %s or busstop %s" % (line_number,busstop))
			sys.exit()

		# Bussin et�isyys ja ajoaika pys�kille
		locat_diff = abs(busstop_locat - bus_locat)
		locat_diff_m = locat_diff * self.line_locat_reso * self.area_pixel_size
		bus_run_time_sec = int(locat_diff_m / self.bus_speed_mpers)
		#print("locat_diff=%s, locat_diff_m=%s m, bus_run_time_sec=%s s" % (locat_diff,locat_diff_m,bus_run_time_sec))

		return [locat_diff_m,bus_run_time_sec]




def generate_testarea(args,gui):

	global generate_counter
	global test_area

	generate_counter += 1
	print("\n -- generate_testarea_and_logs: %s -- \n" % generate_counter)

	#if generate_counter > 1:
	#	return

	if args.gui_enable == 1:
		print("generate_testarea_and_logs: GUI in use")
	else:
		print("generate_testarea_and_logs: GUI not in use")

	# Luodaan testialue, -pys�kit ja -linjat sek� piirret��n ne tarvittaessa GUI:hin
	test_area = TestArea(args.area_size,
						args.event_versatility,args.traces_max,
						args.busstops_matrix,args.busstops_area,
						args.busstops_A,args.busstops_B,args.busstop_size,
						args.line_locat_reso,args.line_route,
						args.output_path,args.log_name,args.gui_enable,gui)

	# Gneroidaan linjadatatiedostot
	test_area.generate_test_lines("line_coords")

	# T�m� t�st� viel� muualle ?
	generate_bus_run_logs(args,gui,"Area"," ")

def generate_bus_run_logs(args,gui,source,trace_mode):

	global test_area

	# Sallitaan tai estetään bussitietojen näyttö testialueessa
	gui_info_enable = 0

	# Generoidaan lokit testialueelta
	test_area.generate_bus_runs(args.date,args.start_time,args.stop_time,args.line_locat_reso,args.area_pixel_size,
					   args.bus_msg_interval,args.bus_speed,args.bus_speed_variance,
					   args.bus_amount,args.single_log,args.debug,gui,gui_info_enable,source,trace_mode)

#******************************************************************************
#
#	FUNCTION:	main
#
#******************************************************************************
def main():

	print("version: %s" % g_version)

	print("Python sys: %s\n" % sys.version)
	print("Modules   : %s\n" % sys.modules.keys())

	start_time = time.time()

	parser = argparse.ArgumentParser()
	parser.add_argument('-log_name','--log_name', dest='log_name', help='log_name')
	parser.add_argument('-event_versatility','--event_versatility', dest='event_versatility', type=int, help='event_versatility')
	parser.add_argument('-traces_max','--traces_max', dest='traces_max', type=int, help='traces_max')
	parser.add_argument('-area_size','--area_size', dest='area_size', help='area_size')
	parser.add_argument('-area_pixel_size','--area_pixel_size', dest='area_pixel_size', type=int, help='area_pixel_size')
	parser.add_argument('-date','--date', dest='date', help='date')
	parser.add_argument('-start_time','--start_time', dest='start_time', help='start_time')
	parser.add_argument('-stop_time','--stop_time', dest='stop_time', help='stop_time')
	parser.add_argument('-busstops_matrix','--busstops_matrix', dest='busstops_matrix', help='busstops_matrix')
	parser.add_argument('-busstops_area','--busstops_area', dest='busstops_area', help='busstops_area')
	parser.add_argument('-busstops_A','--busstops_A', dest='busstops_A', type=int, help='busstops_A')
	parser.add_argument('-busstops_B','--busstops_B', dest='busstops_B', type=int, help='busstops_B')
	parser.add_argument('-busstop_size','--busstop_size', dest='busstop_size', help='busstop_size')
	parser.add_argument('-bus_msg_interval','--bus_msg_interval', dest='bus_msg_interval', type=int, help='bus_msg_interval')
	parser.add_argument('-bus_speed','--bus_speed', dest='bus_speed', type=int, help='bus_speed')
	parser.add_argument('-bus_speed_variance','--bus_speed_variance', dest='bus_speed_variance', type=int, help='bus_speed_variance')
	parser.add_argument('-bus_amount','--bus_amount', dest='bus_amount', type=int, help='bus_amount')
	parser.add_argument('-line_route','--line_route', action='append', dest='line_route', default=[], help='line_route')
	parser.add_argument('-line_locat_reso','--line_locat_reso', dest='line_locat_reso', type=int, help='line_locat_reso')
	parser.add_argument('-single_log','--single_log', dest='single_log', type=int, help='single_log')
	parser.add_argument('-debug','--debug', dest='debug', type=int, help='debug')
	parser.add_argument('-output_path','--output_path', dest='output_path', help='output_path')
	parser.add_argument('-gui_enable','--gui_enable', dest='gui_enable', type=int, help='gui_enable')
	parser.add_argument('-gui_zoom','--gui_zoom', dest='gui_zoom', type=float, help='gui_zoom')
	parser.add_argument('-gui_line_zoom','--gui_line_zoom', dest='gui_line_zoom', type=float, help='gui_line_zoom')

	args = parser.parse_args()

	print("log_name           : %s " % args.log_name)
	print("event_versatility  : %s " % args.event_versatility)
	print("traces_max         : %s " % args.traces_max)
	print("area_size          : %s pixels" % args.area_size)
	print("area_pixel_size    : %s m (fixed ?)" % args.area_pixel_size)
	print("date               : %s" % args.date)
	print("start_time         : %s" % args.start_time)
	print("stop_time          : %s" % args.stop_time)
	print("busstops_matrix    : %s" % args.busstops_matrix)
	print("busstops_area      : %s pixels" % args.busstops_area)
	print("busstops_A         : %s" % args.busstops_A)
	print("busstops_B         : %s" % args.busstops_B)
	print("busstop_size       : %s pixels" % args.busstop_size)
	print("bus_msg_interval   : %s s" % args.bus_msg_interval)
	print("bus_speed          : %s km/h" % args.bus_speed)
	print("bus_speed_variance : %s km/h" % args.bus_speed_variance)
	print("bus_amount         : %s" % args.bus_amount)
	print("line_route         : %s" % args.line_route)
	print("line_locat_reso    : %s x %s m (area_pixel_size)" % (args.line_locat_reso,args.area_pixel_size))
	print("single_log         : %s" % args.single_log)
	print("debug              : %s" % args.debug)
	print("output_path        : %s" % args.output_path)
	print("gui_enable         : %s" % args.gui_enable)
	print("gui_zoom           : %s" % args.gui_zoom)
	print("gui_line_zoom      : %s" % args.gui_line_zoom)

	config = configparser.ConfigParser()
	config.read('LogGen.ini')
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

		gui = GUI_TestArea(args,"Testarea",testarea_x,testarea_y,x_width_new,y_height_new,
								x_offset_new,y_offset_new,zoom_factor,generate_testarea)
		gui2 = GUI_LogArea(args,"Logarea",logarea_x,logarea_y,700,1050,0,0,1.0,generate_bus_run_logs)

		#gui.show()
		#gui2.show()

		sys.exit(app.exec_())

	else:
		self_value = ""
		generate_testarea(args,self_value)

	print("\n Total execution time: %.3f seconds" % (time.time() - start_time))

	# Jos GUI k�yt�ss� lopetetaan vasta enterin painamisen j�lkeen
	if args.gui_enable == 1:
		user_input = input("Press enter to stop")

if __name__ == '__main__':
    main()
