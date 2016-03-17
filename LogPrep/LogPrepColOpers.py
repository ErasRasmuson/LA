# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	LogPrepColOpers.py    

AUTHOR:     Esa Heikkinen
DATE:       27.10.2014
DOCUMENT:   - 
VERSION:    "$Id$"
REFERENCES: -
PURPOSE:    
CHANGES:    "$Log$"
###############################################################################
"""

from datetime import datetime

def ccs_time(ccs_day,ccs_time,date):
	
	#print("ccs_time: %s %s %s" % (ccs_day,ccs_time,date))
	
	timestamp_new_str = ccs_time
	timestamp_str = str(date) + " " + ccs_time
	try:
		timestamp = datetime.strptime(timestamp_str,"%d%m%y %H:%M:%S")
		timestamp_new_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
	except ValueError:
		print("ERR: ccs_time: Can not convert time: %s" % timestamp_str)
	
	return timestamp_new_str
	
def bus_time(bus_day,bus_month,bus_time,date):
	
	#print("bus_time: %s %s %s %s" % (bus_day,bus_month,bus_time,date))
	
	timestamp_new_str = bus_time
	timestamp_str = str(date) + " " + bus_time
	try:
		timestamp = datetime.strptime(timestamp_str,"%d%m%y %H:%M:%S")
		timestamp_new_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
	except ValueError:
		print("ERR: bus_time: Can not convert time: %s" % timestamp_str)
	
	return timestamp_new_str
	
def coord_ms2aadd(coord_ms):
	#print("coord_ms2aadd: coord_ms: %s" % (coord_ms))
	
	coord_aadddd = int(coord_ms) / 3600000.0
	#print("coord_ms2aadd: coord_aadddd: %s" % (coord_aadddd))
	
	return str(coord_aadddd)
	
def bqd_bus_time(bqd_year,bqd_month,bqd_day,bqd_time):
	
	#print("bqd_bus_time: %s %s %s %s" % (bqd_year,bqd_month,bqd_day,bqd_time))
	
	timestamp_new_str = bqd_time
	timestamp_str = str(bqd_year) + str(bqd_month) + str(bqd_day) + " " + bqd_time
	try:
		timestamp = datetime.strptime(timestamp_str,"%Y%m%d %H:%M:%S")
		timestamp_new_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
	except ValueError:
		print("ERR: bqd_bus_time: Can not convert time: %s" % timestamp_str)
	
	return timestamp_new_str
	
def ccs_rtattime(ccs_rtat_time,date):

	#print("ccs_rtattime: %s %s %s" % (ccs_rtat_time,date))
	
	timestamp_new_str = ccs_rtat_time
	timestamp_str = str(date) + " " + ccs_rtat_time
	try:
		timestamp = datetime.strptime(timestamp_str,"%d%m%y %H%M%S")
		timestamp_new_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
	except ValueError:
		print("ERR: ccs_rtattime: Can not convert time: %s" % timestamp_str)
	
	return timestamp_new_str
	
def ccs_busnum(busnum):
	#print("ccs_busnum")
	busnum_dec = str(int(busnum,16))
	return busnum_dec

def bus_busnum(busnum):
	#print("bus_busnum")
	return busnum
	
def bqd_busnum(busnum):
	#print("bqd_busnum")
	return busnum
	
	