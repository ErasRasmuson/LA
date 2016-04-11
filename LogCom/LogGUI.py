# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	LogGUI.py

AUTHOR:     Esa Heikkinen
DATE:       5.3.2016
DOCUMENT:   -
VERSION:    "$Id$"
REFERENCES: -
PURPOSE:
CHANGES:    "$Log$"
###############################################################################
"""

import os.path
import sys
import time
from datetime import datetime, timedelta
import glob
import math

#from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *

g_version = "$Id$"

#******************************************************************************
#
#	CLASS:	GUI
#
#******************************************************************************
class GUI(QWidget):

	generate_counter = 0

	def __init__(self):
			print("GUI init")
			#generate_counter = 0

	def draw_line(self,qp,x1,y1,x2,y2,text,color):

		x1_new = int(x1 * self.zoom_factor) + self.x_offset
		y1_new = int(y1 * self.zoom_factor) + self.y_offset
		x2_new = int(x2 * self.zoom_factor) + self.x_offset
		y2_new = int(y2 * self.zoom_factor) + self.y_offset

		pen = QPen(color, 2, Qt.SolidLine)

		qp.setPen(pen)
		qp.drawLine(x1_new,y1_new,x2_new,y2_new)
		#qp.drawStaticText(x1_new,y1_new,QStaticText(text))

	def draw_point(self,qp,x,y,text,color):

		x_new = int(x * self.zoom_factor) + self.x_offset
		y_new = int(y * self.zoom_factor) + self.y_offset

		pen = QPen(color, 2, Qt.SolidLine)

		qp.setPen(pen)
		#qp.setPen(Qt.red)
		qp.drawPoint(x_new, y_new)
		#qp.drawStaticText(x_new,y_new,QStaticText(text))

	def draw_circle(self,qp,x,y,w,text,color):

		w_new = w * self.zoom_factor
		x_new = int(x * self.zoom_factor) + self.x_offset - int(w_new / 2.0)
		y_new = int(y * self.zoom_factor) + self.y_offset - int(w_new / 2.0)


		#pen = QPen(Qt.black, 1, Qt.SolidLine)
		pen = QPen(color, 1, Qt.SolidLine)
		qp.setPen(pen)
		qp.drawEllipse(x_new,y_new,w_new,w_new)
		#qp.drawStaticText(x_new,y_new,QStaticText(text))

	def draw_box(self,qp,mode,x,y,w,h,text):

		x_new = int(x * self.zoom_factor) + self.x_offset
		y_new = int(y * self.zoom_factor) + self.y_offset

		w_new = int(w * self.zoom_factor)
		h_new = int(h * self.zoom_factor)

		#print("draw_box: %s,%s,%s,%s : %s,%s,%s,%s : %s" % (x,y,w,h,x_new,y_new,w_new,h_new,text))

		pen = QPen(Qt.black, 1, Qt.SolidLine)
		qp.setPen(pen)
		if mode == "Fill":
			qp.fillRect(x_new,y_new,w_new,h_new,Qt.yellow)
		else:
			qp.drawRect(x_new,y_new,w_new,h_new)
		qp.drawStaticText(x_new,y_new,QStaticText(text))

#******************************************************************************
#
#	CLASS:	GUI_TestArea
#
#******************************************************************************
class GUI_TestArea(GUI,QWidget):
#class GUI(QWidget):

	global generate_testarea

	def __init__(self,args,name,x,y,width,height,x_offset,y_offset,zoom_factor,callback_function):
		print("GUI TestArea INIT for: %s" % name)
		super(GUI, self).__init__()
		self.initUI(name,x,y,width,height)

		self.args = args
		self.x_offset    = x_offset
		self.y_offset    = y_offset
		self.zoom_factor = zoom_factor
		self.area_width = width
		self.area_height = height
		self.area_pixel_size = args.area_pixel_size
		self.area_size = args.area_size
		self.line_route = args.line_route
		self.start_time = args.start_time
		self.stop_time = args.stop_time
		self.bus_amount = args.bus_amount
		self.bus_speed = args.bus_speed
		self.bus_speed_variance = args.bus_speed_variance
		self.log_name    = args.log_name

		# S�iett� ei tarvita ?
		#self.thread = Worker()

		self.generate_callback_function=callback_function

	def initUI(self,name,x,y,width,height):


		#self.button = QPushButton('Set geometry', self)
		#self.button.clicked.connect(self.handleButton)
		#layout = QVBoxLayout(self)
		#layout.addWidget(self.button)

		self.setGeometry(x,y,width,height)
		self.setWindowTitle(name)
		self.show()

		self.generate_counter = 0

	def handleButton(self):
		print("handleButton")

	def paintEvent(self, e):

		# Tätä kutsutaan turhan usein !? Aina kun focus muuttuu ikkunassa tai koko tms. ?
		self.generate_counter += 1
		#if self.generate_counter > 1:
		#	return

		qp = QPainter()
		qp.begin(self)
		self.qp = qp

		# Tyhjennett�� piirtoalue (jos piirret��n uudestaan)
		qp.eraseRect(0,0,self.area_width,self.area_height)

		window_width  = self.width()
		window_height = self.height()
		x_central_pos = int(self.area_width / 2.0) - 100
		qp.drawText( x_central_pos, 30, "Name: %s"  %  (self.log_name) )

		width,height=self.area_size.split("x")
		width_m = int(width) * self.area_pixel_size
		height_m = int(height) * self.area_pixel_size

		qp.drawText( x_central_pos, 50, "Window size is %dx%d, Test area size is %s, %sx%s m, zoom %s "  %  \
						( window_width, window_height, self.area_size, width_m, height_m, self.zoom_factor) )

		qp.drawText( x_central_pos, 70, "Time: %s - %s"  % (self.start_time,self.stop_time) )
		qp.drawText( x_central_pos, 90, "Bus: amount/line: %s, speed: %s km/h, s.variance: %s km/h"  % (self.bus_amount,self.bus_speed,self.bus_speed_variance) )

		pos_y = 90
		for line_route in self.line_route:
			pos_y += 20
			line_number, line_color, line_start, line_busstops = line_route.split(":")
			qp.drawText( x_central_pos, pos_y, "%s"  % (line_route) )

		# Generoidaan testialue, -pys�kit ja -linjat
		#generate_testarea(self.args,self)

		self.generate_callback_function(self.args,self)

		qp.end()

		print("TestArea: width: %s, height: %s, x: %s, y: %s" % (self.width(),self.height(),self.x(),self.y()))

#******************************************************************************
#
#	CLASS:	GUI_LogArea
#
#******************************************************************************
class GUI_LogArea(GUI,QWidget):

	event_line_x1 = {}

	def __init__(self,args,name,x,y,width,height,x_offset,y_offset,zoom_factor,callback_function):

		print("GUI LogArea INIT for: %s" % name)
		super(GUI, self).__init__()
		self.initUI(name,x,y,width,height)

		self.args = args
		self.x_offset    = x_offset		
		self.y_offset    = y_offset
		self.zoom_factor = zoom_factor
		self.area_width = width
		self.area_height = height
		self.start_time = args.start_time
		self.stop_time = args.stop_time
		#self.bus_amount = args.bus_amount
		self.bus_amount = args.bus_amount
		self.bus_speed = args.bus_speed
		self.bus_speed_variance = args.bus_speed_variance
		self.date = args.date
		#self.start_time = args.start_time
		#self.stop_time = args.stop_time
		self.bus_msg_interval = args.bus_msg_interval
		self.line_route = args.line_route
		self.log_name    = args.log_name
		self.line_zoom = args.gui_line_zoom
		self.traces_max = args.traces_max

		t1,t2,loop_counter_max = convert_datetime(self.date,self.start_time,self.stop_time,self.bus_msg_interval)
		self.loop_counter_max = loop_counter_max
		self.t1 = t1		

		self.trace_mode = "ALL_traces"

		self.generate_callback_function=callback_function

	def initUI(self,name,x,y,width,height):

		combo = QComboBox(self)
		combo.addItem("ALL_traces")
		combo.addItem("FIRST_trace")
		combo.addItem("LAST_trace")
		combo.activated[str].connect(self.onComboActivated) 
		combo.move(10,5)
		self.setGeometry(x,y,width,height)
		self.setWindowTitle(name)
		self.show()

		self.generate_counter = 0

	def onComboActivated(self, text):
		#print(" ---- onComboActivated: %s ---- " % text)
		self.trace_mode = text
		#self.paintEvent()

	def paintEvent(self, e):

		# Tätä kutsutaan turhan usein !? Aina kun focus muuttuu ikkunassa tai koko tms. ?
		self.generate_counter += 1
		#if self.generate_counter > 1:
		#	return

		qp = QPainter()
		qp.begin(self)
		self.qp = qp

		# Tyhjennett�� piirtoalue (jos piirret��n uudestaan)
		qp.eraseRect(0,0,self.area_width,self.area_height)

		window_width  = self.width()
		window_height = self.height()
		x_central_pos = int(self.area_width / 2.0) - 100
		#qp.drawText( 0, 20, "Window size is %dx%d "  %  ( window_width, window_height ) )
		line_count = len(self.line_route)
		qp.drawText( 60, 40, "Name: %s, Lines: %s, Bus: amount/line: %s, speed: %s km/h, s.variance: %s km/h, traces max: %s, line_zoom: %s"  % 
			(self.log_name ,line_count,self.bus_amount,self.bus_speed,self.bus_speed_variance,self.traces_max,self.line_zoom) )

		# Muodostetaan aika-asteikko
		timestamp_interval_sec = 600
		timetamp_counter = self.loop_counter_max * self.bus_msg_interval / timestamp_interval_sec
		print("timetamp_counter = %s" % timetamp_counter)

		self.line_y1 = 80
		x_pos = 10
		x_pos2 = window_width - 50
		for i in range(int(timetamp_counter)+1):
			sec = i * timestamp_interval_sec
			t = self.t1 + timedelta(seconds=sec)
			y_pos = self.line_y1 + i * timestamp_interval_sec / self.bus_msg_interval * self.line_zoom
			pen = QPen(QColor(127,127,127,127), 1, Qt.DashLine)
			qp.setPen(pen)
			qp.drawLine(x_pos,y_pos,x_pos2,y_pos)
			text = "%s, %s" % (t,i)
			qp.drawStaticText(x_pos,y_pos,QStaticText(text))

		# Muodostetaan tapahtumakohtaiset aikajanat
		event_topics = {}
		event_topics[0] = "LOGIN/LOGOUT"
		event_topics[1] = "LOCAT" 
		event_topics[2] = "RTAT" 
		event_topics[3] = "AD" 

		line_y2 = y_pos
		start_x = 150
		for i in range(4):
			self.event_line_x1[i] =  start_x + 150 * i
			line_x2 = self.event_line_x1[i]
			self.draw_line(self.qp,self.event_line_x1[i],self.line_y1,line_x2,line_y2,"",Qt.black)
			qp.drawText( self.event_line_x1[i], self.line_y1 - 10 , event_topics[i])


		# Generoidaan lokidata ja sen kautta päivitetään GUI
		#generate_bus_run_logs(self.args,self,"Log",self.trace_mode)
		self.generate_callback_function(self.args,self,"Log",self.trace_mode)
		qp.end()

		screen = QDesktopWidget().screenGeometry()
		print("width: %s, height: %s" % (screen.width(),screen.height()))
		print("LogArea: width: %s, height: %s, x: %s, y: %s" % (self.width(),self.height(),self.x(),self.y()))


	def drawLogEvent(self,qp,event_pos,time_pos,symbol):

		width = 6
		width_half = int(width / 2.0)
		x_pos = self.event_line_x1[event_pos] - width_half
		y_pos = self.line_y1 - width_half + time_pos * self.line_zoom

		if symbol == "circle":
			pen = QPen(Qt.black, 1, Qt.SolidLine)
			qp.setPen(pen)
			qp.drawEllipse(x_pos,y_pos,width,width)
		elif symbol == "boxA":
			qp.fillRect(x_pos,y_pos,width,width,Qt.green)
		elif symbol == "boxB":
			qp.fillRect(x_pos,y_pos,width,width,Qt.blue)
		else:
			qp.fillRect(x_pos,y_pos,width,width,Qt.red)

	def drawLogTraceLine(self,qp,event_pos1,time_pos1,event_pos2,time_pos2,color):

		y_pos = self.line_y1 + time_pos1 * self.line_zoom
		y_pos2 = self.line_y1 + time_pos2 * self.line_zoom
		self.draw_line(qp,self.event_line_x1[event_pos1],y_pos,self.event_line_x1[event_pos2],y_pos2,"",color)

#******************************************************************************
#
#	CLASS:	GUI_AnalyzeArea
#
#******************************************************************************
class GUI_AnalyzeArea(GUI,QWidget):

	event_line_x1 = {}

	def __init__(self,args,name,x,y,width,height,x_offset,y_offset,zoom_factor,callback_function,state_GUI_line_num):

		print("GUI AnalyzeArea INIT for: %s" % name)
		super(GUI, self).__init__()
		self.initUI(name,x,y,width,height)

		self.args = args
		self.x_offset    = x_offset		
		self.y_offset    = y_offset
		self.zoom_factor = zoom_factor
		self.area_width = width
		self.area_height = height
		self.start_time = args.start_time
		self.stop_time = args.stop_time
		self.date = args.date
		self.state_GUI_line_num = state_GUI_line_num
		self.state_order = args.state_order
		self.analyze_file = args.analyze_file

		self.analyzing_mode,self.analyzing_col_num = args.analyzing_mode.split(":")
		#self.analyzing_mode = args.analyzing_mode

		# Muutetaan ajat oikeaan muotoon
		days,months,years=self.date.split(".")
		print("date = %s %s %s" % (days,months,years))
		hours,minutes,seconds=self.start_time.split(":")
		print("start_time = %s %s %s" % (hours,minutes,seconds))
		stop_hours,stop_minutes,stop_seconds=self.stop_time.split(":")
		print("stop_time  = %s %s %s" % (stop_hours,stop_minutes,stop_seconds))

		# Lasketaan aikaerot yms.
		t1 = datetime(int(years),int(months),int(days),int(hours),int(minutes),int(seconds))
		t2 = datetime(int(years),int(months),int(days),int(stop_hours),int(stop_minutes),int(stop_seconds))
		delta = t2 - t1
		#print("delta=%s" % delta)
		self.delta_secs = delta.seconds
		if self.analyzing_mode == "COMPARE":
			self.delta_secs = 1200

		self.t1 = t1
		self.line_y1 = 80
		self.line_y2 = 40

		#self.line_auto_zoom = (height - self.line_y1 - self.line_y2) / self.delta_secs
		#print("line_auto_zoom  = %s" % (self.line_auto_zoom))

		self.line_auto_zoom = self.calc_auto_zoom(self.delta_secs)

		self.win_width = 200
		self.first_start = True

		self.trace_mode = "ALL_traces"

		self.reference_pos = 0
		self.reference_time = 0
		self.reference_diff_time = 0

		self.generate_callback_function=callback_function

	def calc_auto_zoom(self,seconds):
		line_auto_zoom = (self.area_height - self.line_y1 - self.line_y2) / seconds
		print("calc_auto_zoom: line_auto_zoom  = %s" % (line_auto_zoom))
		return line_auto_zoom

	def initUI(self,name,x,y,width,height):

		#combo = QComboBox(self)
		#combo.addItem("ALL_traces")
		#combo.addItem("FIRST_trace")
		#combo.addItem("LAST_trace")
		#combo.activated[str].connect(self.onComboActivated) 
		#combo.move(10,5)
		self.setGeometry(x,y,width,height)
		self.setWindowTitle(name)
		self.show()

		self.generate_counter = 0

	def onComboActivated(self, text):
		#print(" ---- onComboActivated: %s ---- " % text)
		self.trace_mode = text
		#self.paintEvent()

	def paintEvent(self, e):

		# Tätä kutsutaan turhan usein !? Aina kun focus muuttuu ikkunassa tai koko tms. ?
		self.generate_counter += 1
		#if self.generate_counter > 1:
		#	return

		qp = QPainter()
		qp.begin(self)
		self.qp = qp

		# Tyhjennett�� piirtoalue (jos piirret��n uudestaan)
		qp.eraseRect(0,0,self.area_width,self.area_height)

		window_width  = self.width()
		window_height = self.height()
		x_central_pos = int(self.area_width / 2.0) - 100
		#qp.drawText( 0, 20, "Window size is %dx%d "  %  ( window_width, window_height ) )
		#line_count = len(self.line_route)
		#qp.drawText( 60, 40, "Analyze name: %s,  \t  mode: %s, \t  zoom: %.2f" % (self.analyze_file,self.analyzing_mode,self.line_zoom) )

		if self.analyzing_mode == "COMPARE":
			#self.delta_secs = 3600
			self.line_auto_zoom = self.calc_auto_zoom(self.delta_secs)

		# Muodostetaan aika-asteikko
		timestamp_interval_sec = 1200
		timetamp_counter = self.delta_secs / timestamp_interval_sec
		print("timetamp_counter = %s" % timetamp_counter)

		#line_zoom = self.zoom_factor
		self.line_zoom = self.line_auto_zoom

		qp.drawText( 60, 25, "Analyze name: %s,  \t  mode: %s : col: %s, \t  zoom: %.2f" % 
				(self.analyze_file,self.analyzing_mode,self.analyzing_col_num,self.line_zoom) )

		x_pos = 10
		x_pos2 = window_width - 50
		for i in range(int(timetamp_counter)+1):
			sec = i * timestamp_interval_sec
			t = self.t1 + timedelta(seconds=sec)
			#print("t=%s, sec=%s" % (t,sec))
			y_pos = self.line_y1 + i * timestamp_interval_sec * self.line_zoom
			pen = QPen(QColor(127,127,127,127), 1, Qt.DashLine)
			qp.setPen(pen)
			qp.drawLine(x_pos,y_pos,x_pos2,y_pos)
			text = "%s, %s" % (t,i)

			if self.analyzing_mode == "COMPARE":
				text = "%s, %s" % (sec,i)

			qp.drawStaticText(x_pos,y_pos,QStaticText(text))

		# Muodostetaan tapahtumakohtaiset aikajanat ym. tiedot
		self.line_y3 = y_pos
		self.start_x = 150
		event_topics = {}
		self.line_gap = 150
		for state_name in self.state_GUI_line_num.keys():
			GUI_line_num = self.state_GUI_line_num[state_name]

			state_order = self.state_order[state_name]

			i = int(GUI_line_num)
			if i in event_topics:
				event_topics[i] += ", " + state_name + " (" + str(state_order) + ".)"
			else:
				event_topics[i] = state_name + " (" + str(state_order) + ".)"

			self.event_line_x1[i] =  self.start_x + self.line_gap * i

			print(" %3d, %s, %s" % (i,self.event_line_x1[i],event_topics[i]))

			#line_x2 = self.event_line_x1[i]
			self.drawVerticalLine(qp,i,0,2)
			self.drawVerticalText(qp,i,0,event_topics[i],35)

		# Sovitetaan ikkunan leveys sopivaksi, vain kerran alussa
		if self.first_start == True:
			#win_width = len(self.state_GUI_line_num.keys()) * line_gap + self.start_x
			self.win_width = len(event_topics.keys()) * self.line_gap + self.start_x + 100
			self.resize(self.win_width,self.height())
			self.first_start = False

		#print(" x=%s, y=%s, w=%s, h=%s, win_width=%s" % (self.x(),self.y(),self.width(),self.height(),self.win_width))

		# Analysoidaan lokidata ja sen kautta päivitetään GUI
		self.generate_callback_function(self.args,self,"Ana",self.trace_mode)
		qp.end()

		screen = QDesktopWidget().screenGeometry()
		print("width: %s, height: %s" % (screen.width(),screen.height()))
		print("Analyze area: width: %s, height: %s, x: %s, y: %s" % (self.width(),self.height(),self.x(),self.y()))

	def drawVerticalLine(self,qp,event_pos,event_offset,line_width):

		line_x2 =  event_offset + self.start_x + self.line_gap * event_pos

		# Levennetään ikkunaa tarvittaessa
		if line_x2 > self.win_width:
			self.win_width = line_x2 + 100
			self.resize(self.win_width ,self.height())

		pen = QPen(QColor(127,127,127,127), line_width, Qt.DashLine)
		qp.setPen(pen)
		qp.drawLine(line_x2,self.line_y1,line_x2,self.line_y3)


	def drawVerticalText(self,qp,event_pos,event_offset,text_str,text_offset):

		line_x2 =  event_offset + self.start_x + self.line_gap * event_pos

		# Levennetään ikkunaa tarvittaessa
		if line_x2 > self.win_width:
			self.win_width = line_x2 + 100
			self.resize(self.win_width ,self.height())

		pen = QPen(Qt.black, 2, Qt.SolidLine)
		qp.setPen(pen)
		qp.drawText(line_x2, self.line_y1 - text_offset , text_str)

	def drawEvent(self,qp,event_pos,event_offset,timestamp,text,symbol,override_mode):

		if self.analyzing_mode == "COMPARE" and override_mode == 0:
			return

		width = 6
		width_half = int(width / 2.0)
		x_pos = self.event_line_x1[int(event_pos)] - width_half + event_offset 
		y_pos = self.line_y1 - width_half + self.calcEventPos(timestamp) * self.line_zoom

		# Levennetään ikkunaa tarvittaessa
		if x_pos > self.win_width:
			self.win_width = x_pos + 100
			self.resize(self.win_width ,self.height())

		if symbol == "circle":
			pen = QPen(Qt.black, 1, Qt.SolidLine)
			qp.setPen(pen)
			qp.drawEllipse(x_pos,y_pos,width,width)
		elif symbol == "boxA":
			qp.fillRect(x_pos,y_pos,width,width,Qt.green)
		elif symbol == "boxB":
			qp.fillRect(x_pos,y_pos,width,width,Qt.blue)
		else:
			qp.fillRect(x_pos,y_pos,width,width,Qt.red)

		#qp.drawText(x_pos + 10,y_pos + 10 , str(timestamp))
		qp.drawText(x_pos + 10, y_pos + 10, text)

	def setReferenceTime(self,ref_time,event_line_ind):

		if self.analyzing_mode == "COMPARE" and event_line_ind == 0:
			self.reference_time = self.t1
		else:
			self.reference_time = ref_time
		
		print("  setReferenceTime: ref_time: %s \n" % (ref_time))

	def setTraceReferenceTime(self,ref_time):
		self.reference_diff_time = ref_time - self.reference_time
		print("  setTraceReferenceTime: ref_time: %s, ref_diff_time: %s \n" % (ref_time,self.reference_diff_time))

	def drawTimeLine(self,qp,event_pos,event_offset,timestamp1,timestamp2,color):

		if self.analyzing_mode == "COMPARE":
			return

		#print("drawTimeLine: analyzing_mode: %s" % self.analyzing_mode)

		y_pos = int(self.line_y1 + self.calcEventPos(timestamp1) * self.line_zoom)
		y_pos2 = int(self.line_y1 + self.calcEventPos(timestamp2) * self.line_zoom)
		#y_pos = int(self.line_y1 + tp1 * self.line_zoom)
		#y_pos2 = int(self.line_y1 + tp2 * self.line_zoom)

		line_width = 5
		x_pos = self.event_line_x1[int(event_pos)] + event_offset * line_width

		#pen = QPen(QColor(127,0,127,63), line_width, Qt.SolidLine)
		pen = QPen(color, line_width, Qt.SolidLine)
		qp.setPen(pen)
		qp.drawLine(x_pos,y_pos,x_pos,y_pos2)

		#pen = QPen(Qt.black, 1, Qt.SolidLine)
		#qp.setPen(pen)
		#qp.drawText( x_pos,y_pos - 10,str(timestamp1))
		#qp.drawText( x_pos,y_pos2 - 10,str(timestamp2))

	def drawTraceLine(self,qp,event_pos1,event_offset_1,timestamp1,event_pos2,event_offset_2,timestamp2,color):

		if self.analyzing_mode == "COMPARE":
			ts1 = timestamp1 - self.reference_diff_time
			ts2 = timestamp2 - self.reference_diff_time

			if ts2 >= self.t1:
				delta = ts2 - self.t1
			else:
				delta = self.t1 - self.t1

			t2_delta_secs = delta.seconds

			#print(" .... drawTraceLine: ts2: %s, t1: %s, delta: new: %s, old: %s" % (ts2,self.t1,t2_delta_secs,self.delta_secs))

			# Kasvatetaan aikaskaalaa, jos aika isompi kuin suurin nykyinen
			if t2_delta_secs > self.delta_secs:
				self.delta_secs = t2_delta_secs + 100

			#print(" drawTraceLine: ts1: %s, ts2: %s, ref_diff_time: %s" % (ts1,ts2,self.reference_diff_time))
		else:
			ts1 = timestamp1
			ts2 = timestamp2

		y_pos = int(self.line_y1 + self.calcEventPos(ts1) * self.line_zoom)
		y_pos2 = int(self.line_y1 + self.calcEventPos(ts2) * self.line_zoom)
		#y_pos = int(self.line_y1 + tp1 * self.line_zoom)
		#y_pos2 = int(self.line_y1 + tp2 * self.line_zoom)

		#print("y_pos=%s, y_pos2=%s" % (y_pos,y_pos2))
		#print("event_pos1=%s, event_pos2=%s" % (event_pos1,event_pos2))

		x_pos = self.event_line_x1[int(event_pos1)] + event_offset_1
		#print("x_pos=%s" % (x_pos))

		x_pos2 = self.event_line_x1[int(event_pos2)] + event_offset_2
		#print("x_pos2=%s" % (x_pos2))

		# Levennetään ikkunaa tarvittaessa
		if x_pos > self.win_width:
			self.win_width = x_pos + 100
			self.resize(self.win_width ,self.height())

		self.draw_line(qp,x_pos,y_pos,x_pos2,y_pos2,"",color)

	def calcEventPos(self,event_time):
		
		if event_time >= self.t1:
			delta = event_time - self.t1
		else:
			delta = self.t1 - self.t1
		return delta.seconds

# Tämä ei oikeastaan kuulu tänne, mutta toimii näinkin ?!!
def convert_datetime(date,start_time,stop_time,bus_msg_interval):

	#print("date=%s" % date)

	# Muutetaan ajat oikeaan muotoon
	days,months,years=date.split(".")
	print("date = %s %s %s" % (days,months,years))
	hours,minutes,seconds=start_time.split(":")
	print("start_time = %s %s %s" % (hours,minutes,seconds))
	stop_hours,stop_minutes,stop_seconds=stop_time.split(":")
	print("stop_time  = %s %s %s" % (stop_hours,stop_minutes,stop_seconds))

	# Lasketaan aikaerot yms.
	t1 = datetime(int(years),int(months),int(days),int(hours),int(minutes),int(seconds))
	t2 = datetime(int(years),int(months),int(days),int(stop_hours),int(stop_minutes),int(stop_seconds))
	delta = t2 - t1
	delta_secs = delta.seconds
	loop_counter_max = int(delta_secs / bus_msg_interval)
	print("Time delta: %s sec, loop_counter_max: %s" % (delta_secs,loop_counter_max))
	print("")

	return t1,t2,loop_counter_max
