# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	logdig_TLG_1.py    

AUTHOR:     Esa Heikkinen
DATE:       26.02.2016
DOCUMENT:   - 
VERSION:    "$Id$"
REFERENCES: -
PURPOSE:    
CHANGES:    "$Log$"
###############################################################################
"""
import datetime

# Tilat
states = ["START","RTAT","LOGIN","BS-START","BS-PASS","AD","LOGOUT","END"]

# Muuttujien taulukko
variables = {}

# Tilan tyypit
state_type = {}
state_type["START"] 	= ":"
state_type["RTAT"] 		= "SEARCH_EVENT:First"
state_type["LOGIN"] 	= "SEARCH_EVENT:First"
state_type["BS-START"] 	= "SEARCH_POSITION:Leaving"
state_type["BS-PASS"] 	= "SEARCH_POSITION:Entering"
state_type["AD"] 		= "SEARCH_EVENT:Last"
state_type["LOGOUT"] 	= "SEARCH_EVENT:First"
state_type["END"] 		= ":"

# Alkutila
start_state_name = "START"

# Syöteaakkosto (tilasiirtymien nimet)
#input_alphabets =
transition_names = ["Found","Not found","Exit"]

# Tilasiirtymät
transition = {}
transition["START"] 	= ["RTAT","RTAT","END"]
transition["RTAT"] 		= ["LOGIN","END","END"]
transition["LOGIN"] 	= ["BS-START","END","END"]
transition["BS-START"] 	= ["BS-PASS","END","END"]
transition["BS-PASS"] 	= ["AD","END","END"]
transition["AD"] 		= ["LOGOUT","END","END"]
transition["LOGOUT"] 	= ["RTAT","END","END"]
transition["END"] 		= ["","",""]

# Tilasiirtymäfunktiot (vastaa tilasiirtymien tietorakennetta)
transition_function = {}
transition_function["START"] 	= ["start_function","",""]
transition_function["RTAT"] 	= ["RTAT_found_function","",""]
transition_function["LOGIN"] 	= ["LOGIN_found_funtion","",""]
transition_function["BS-START"] = ["START_found_function","",""]
transition_function["BS-PASS"] 	= ["PASS_found_function","",""]
transition_function["AD"] 		= ["AD_found_function","",""]
transition_function["LOGOUT"] 	= ["LOGOUT_found_function","",""]

# Funktiot, jotka suoritetaan tilaan mennessä
state_onentry_function = {}
#state_onentry_function["RTAT"] = "RTAT_onentry"

# Funktiot, jotka suoritetaan tilasta poistuttaessa.
state_onexit_function = {}

# Lopputila
end_state_name = "END"

# Tilojen luettavat lokitiedostot
state_logfiles = {}
state_logfiles["RTAT"]		= "ccs_rtat.csv"
state_logfiles["LOGIN"]		= "bus_login.csv"
state_logfiles["BS-START"]	= "bus_coords_<LOCAT-BUS>.csv"
state_logfiles["BS-PASS"]	= "bus_coords_<LOCAT-BUS>.csv"
state_logfiles["AD"]		= "ccs_ad.csv"
state_logfiles["LOGOUT"]	= "bus_login.csv"

# Tilojen data-tiedostot
state_datafiles = {}
state_datafiles["RTAT"]		= ""
state_datafiles["LOGIN"]	= ""
state_datafiles["BS-START"]	= "area_coords_<START-BUSSTOP>.csv"
state_datafiles["BS-PASS"]	= "area_coords_<RTAT-BUSSTOP>.csv"
state_datafiles["AD"]		= ""
state_datafiles["LOGOUT"]	= ""

# Tilojen asetukset. Tarviiko ?
state_settings = {}
state_settings["RTAT"]		= ""
state_settings["LOGIN"]		= ""
state_settings["BS-START"]	= ""
state_settings["BS-PASS"]	= ""
state_settings["AD"]		= ""
state_settings["LOGOUT"]	= ""

# Globaalit asetukset
variables["SET_MAX_LOGIN_RTAT_TIME"] = 1200 
variables["SET_MAX_RTAT_PASS_TIME"] = 1800 

# Tilojen lokitiedoston muuttujat
state_log_variables = {}
state_log_variables["RTAT"]		= "RTAT-LINE"
state_log_variables["LOGIN"]	= "LOG-LINE,LOG-BUS,LOG-LINE-DIR"
state_log_variables["BS-START"]	= "LOCAT-BUS"
state_log_variables["BS-PASS"]	= "LOCAT-BUS"
state_log_variables["AD"]		= "AD-LINE,AD-BUS,AD-BUS-DIR"
state_log_variables["LOGOUT"]	= "LOG-LINE,LOG-BUS,LOG-LINE-DIR"

# Tilojen datatiedoston muuttujat
state_data_variables = {}
state_data_variables["RTAT"]		= ""
state_data_variables["LOGIN"]		= ""
state_data_variables["BS-START"]	= "START-BUSSTOP"
state_data_variables["BS-PASS"]		= "RTAT-BUSSTOP"
state_data_variables["AD"]			= ""
state_data_variables["LOGOUT"]			= ""

# Tilojen lokin paikkatieto muuttujien (lon ja lat) nimet
state_position_variables = {}
state_position_variables["BS-START"] = "LOCAT-X,LOCAT-Y"
state_position_variables["BS-PASS"]  = "LOCAT-X,LOCAT-Y"

# Tilan lokin aika-sarakkeen nimi
state_log_time_column = {}
state_log_time_column["RTAT"] 		= "RTAT-TIME"
state_log_time_column["LOGIN"] 		= "LOG-TIME"
state_log_time_column["BS-START"] 	= "LOCAT-TIME"
state_log_time_column["BS-PASS"] 	= "LOCAT-TIME"
state_log_time_column["AD"] 		= "AD-TIME"
state_log_time_column["LOGOUT"] 	= "LOG-TIME"

# Tilojen tapahtumahaun aikarajat
state_start_time_limit = {}
state_stop_time_limit  = {}
state_start_time_limit["RTAT"] 		= "<INT-START-TIMESTAMP>,+1"
state_stop_time_limit["RTAT"] 		= "<INT-STOP-TIMESTAMP>,0"
state_start_time_limit["LOGIN"] 	= "<RTAT-TIME>,-<SET_MAX_LOGIN_RTAT_TIME>"
state_stop_time_limit["LOGIN"] 		= "<RTAT-TIME>,0"
state_start_time_limit["BS-START"] 	= "<LOG-TIME>,0"
state_stop_time_limit["BS-START"] 	= "<LOG-TIME>,+<SET_MAX_RTAT_PASS_TIME>"
state_start_time_limit["BS-PASS"] 	= "<RES-BUS-START-TIME>,0"
state_stop_time_limit["BS-PASS"] 	= "<RES-BUS-START-TIME>,+<SET_MAX_RTAT_PASS_TIME>"
state_start_time_limit["AD"] 		= "<RTAT-TIME>,0"
state_stop_time_limit["AD"] 		= "<RES-BUSSTOP-PASS-TIME>,0"
state_start_time_limit["LOGOUT"] 	= "<RES-BUSSTOP-PASS-TIME>,0"
state_stop_time_limit["LOGOUT"] 	= "<INT-STOP-TIMESTAMP>,0"

# Varsinaiset tilasiirtymäfunktiot

def start_function():
	print("")
	print("  Transition-function: start_function")
	
	set_variable("INT-LINE-NUMBER","L001")
	
	# Muutetaan aikaleimat pythonin datetime-muotoon
	start_timestamp_str = variables["INT-START-DATE"] + " " + variables["INT-START-TIME"]
	stop_timestamp_str = variables["INT-START-DATE"] + " " + variables["INT-STOP-TIME"]
	start_timestamp = datetime.datetime.strptime(start_timestamp_str,"%Y-%m-%d %H:%M:%S")
	stop_timestamp = datetime.datetime.strptime(stop_timestamp_str,"%Y-%m-%d %H:%M:%S")
	print("  start_timestamp : %s" % start_timestamp)
	print("  stop_timestamp  : %s" % stop_timestamp)
	
	variables["INT-START-TIMESTAMP"] = start_timestamp
	variables["INT-STOP-TIMESTAMP"]  = stop_timestamp
	
	copy_variable("RTAT-LINE","INT-LINE-NUMBER")
	
	print("")

def RTAT_found_function():
	print("")
	print("  Transition-function: RTAT_found_function")
	copy_variable("LOG-LINE","RTAT-LINE")
	copy_variable("LOG-BUS","RTAT-BUS")
	copy_variable("LOG-LINE-DIR","RTAT-LINE-DIR")
	set_variable("START-BUSSTOP","A1")	
	copy_variable("INT-START-TIMESTAMP","RTAT-TIME")

def LOGIN_found_funtion():
	print("")
	print("  Transition-function: LOGIN_found_funtion")
	copy_variable("LOCAT-BUS","RTAT-BUS")

def START_found_function():
	print("")
	print("  Transition-function: START_found_function")
	copy_variable("RES-BUS-START-TIME","INT-LOCAT-TIME-OLD")

def PASS_found_function():
	print("")
	print("  Transition-function: PASS_found_function")
	copy_variable("RES-BUSSTOP-PASS-TIME","INT-LOCAT-TIME-OLD")
	copy_variable("AD-LINE","INT-LINE-NUMBER")
	copy_variable("AD-BUS","RTAT-BUS")
	copy_variable("AD-BUS-DIR","RTAT-LINE-DIR")

def AD_found_function():
	print("")
	print("  Transition-function: AD_found_function")
	#copy_variable("LOG-LINE","RTAT-LINE")
	#copy_variable("LOG-BUS","RTAT-BUS")
	#copy_variable("LOG-LINE-DIR","RTAT-LINE-DIR")

def LOGOUT_found_function():
	print("")
	print("  Transition-function: LOGOUT_found_function")

#------------------------------------------------------------------------------

# Apufunktiot, joita käytetään tilasiirtmäfunktioissa
def copy_variable(target_var,source_var):

	try:
		print("  Copy variables: %s = %s \"%s\"" % (target_var,source_var,variables[source_var]))
		variables[target_var] = variables[source_var]
	except KeyError:
		print("  ERR: Copying variables: %s = %s" % (target_var,source_var))
		
def set_variable(var_name,var_value):

	try:
		print("  Set variable: %s = \"%s\"" % (var_name,var_value))
		variables[var_name] = var_value
	except KeyError:
		print("  ERR: Setting variable: %s = \"%s\"" % (var_name,var_value))
