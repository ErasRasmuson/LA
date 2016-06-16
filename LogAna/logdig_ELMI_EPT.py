from logdig_analyze_template import *
# ----------------------------- DATA-DRIVEN PART -----------------------------
VARIABLES = {
	"INT-START-DATE":    		"21.08.06",
	"INT-START-TIME":    		"03:00:00",
	"INT-STOP-TIME":     		"23:00:00",
	"SET-LINE-NUMBER":   		"002150",
	"SET-LINE-DIR":   	 		"2",
	"SET-MAX-LOGIN-RTAT-TIME": 	"1200",
	"SET-MAX-RTAT-PASS-TIME":  	"1200",
	"SET-MAX-PASS-ERR-TIME":   	"120"
	}
START = {
	"state":   				"SEARCH RTAT",
	"func":   				"start"
	}
ESU["SEARCH RTAT"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "FromCCS_RTAT.csv",
	"log_varnames":         "RTAT-LINE-NUMBER",
	"log_timecol_name":     "RTAT-MSG-TIMESTAMP",
	"log_start_time_expr":  "<INT-START-TIMESTAMP>,+1",
	"log_stop_time_expr":   "<INT-STOP-TIMESTAMP>,0",
	
	"TF_state":    			"SEARCH LOGIN",
	"TN_state":    			"STOP",
	"TE_state":    			"STOP",
	"onentry_func": 		"RTAT_onentry",
	"GUI_line_num":			"2"
}
ESU["SEARCH LOGIN"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "Apo_<LOG-BUS-NUMBER>_LOG.csv",
	"log_varnames":         "LOG-MSG-TYPE=LOGIN,LOG-BUS-NUMBER=<RTAT-BUS-NUMBER>,LOG-LINE-NUMBER=<SET-LINE-NUMBER>,LOG-DIRECTION=<RTAT-DIRECTION>",
	"log_timecol_name":     "LOG-MSG-TIMESTAMP",
	"log_start_time_expr":  "<RTAT-MSG-TIMESTAMP>,-<SET-MAX-LOGIN-RTAT-TIME>",
	"log_stop_time_expr":   "<RTAT-MSG-TIMESTAMP>,0",
	
	"TF_state":    			"SEARCH starting",
	"TF_func":     			"LOGIN_found",
	"TN_state":    			"SEARCH starting",
	"TN_func":     			"LOGIN_not_found",
	"TE_state":    			"STOP",
	"GUI_line_num":			"0"
}
ESU["SEARCH starting"] = {
	"esu_mode":            	"SEARCH_POSITION:Leaving",
	"log_filename_expr":   	"Apo_<LOG-BUS-NUMBER>_LOCAT.csv",
	"log_varnames":        	"LOCAT-BUS-NUMBER=<LOG-BUS-NUMBER>",
	"log_timecol_name":    	"LOCAT-MSG-TIMESTAMP",
	"log_start_time_expr": 	"<INT-BUS-START-SEARCH-TIME>,0",
	"log_stop_time_expr":  	"<INT-BUS-START-SEARCH-TIME>,+<SET-MAX-RTAT-PASS-TIME>",

	"ssd_lat_col_name":    	"LOCAT-LATITUDE",
	"ssd_lon_col_name":    	"LOCAT-LONGITUDE",
	"ssd_filename_expr":   	"terminal_busstop_<LOG-LINE-NUMBER>_<LOG-DIRECTION>.csv",
	"ssd_varnames":        	"LOG-LINE-NUMBER,LOG-DIRECTION",

	"TF_state":				"SEARCH arriving",
	"TF_func":     			"starting_found",
	"TN_state":    			"SEARCH RTAT",
	"TN_func":     			"",
	"TE_state":    			"SEARCH RTAT",
	"TE_func":     			"",
	"GUI_line_num":			"1"
}
ESU["SEARCH arriving"] = {
	"esu_mode":             "SEARCH_POSITION:Entering",
	"log_filename_expr":    "Apo_<LOCAT-BUS-NUMBER>_LOCAT.csv",
	"log_varnames":         "LOCAT-BUS-NUMBER",
	"log_timecol_name":     "LOCAT-MSG-TIMESTAMP",
	"log_start_time_expr":  "<INT-BUS-START-SEARCH-TIME>,0",
	"log_stop_time_expr":   "<INT-BUS-START-SEARCH-TIME>,+<SET-MAX-RTAT-PASS-TIME>",
	
	"ssd_lat_col_name":   	"LOCAT-LATITUDE",
	"ssd_lon_col_name":   	"LOCAT-LONGITUDE",
	"ssd_filename_expr":   	"target_busstop_<RTAT-SIGN-NUMBER>.csv",
	"ssd_varnames":   		"RTAT-SIGN-NUMBER",
	
	"TF_state":    			"SEARCH BQD",
	"TF_func":     			"arriving_found",
	"TN_state":    			"SEARCH RTAT",
	"TN_func":     			"",
	"TE_state":    			"STOP",
	"TE_func":     			"",
	"GUI_line_num":			"5"
}
ESU["SEARCH BQD"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "BQD_log_BQD.csv",
	"log_varnames":         "BQD-BUS-NUMBER,BQD-LINE-NUMBER",
	"log_timecol_name":     "BQD-MSG-TIMESTAMP",
	"log_start_time_expr":  "<RTAT-MSG-TIMESTAMP>,+300",
	"log_stop_time_expr":   "<RTAT-MSG-TIMESTAMP>,+<SET-MAX-RTAT-PASS-TIME>",
	
	"TF_state":    			"SEARCH AD",
	"TF_func":     			"BQD_found",
	"TN_state":    			"SEARCH RTAT",
	"TN_func":     			"",
	"TE_state":    			"STOP",
	"TE_func":     			"",
	"GUI_line_num":			"3"
}
ESU["SEARCH AD"] = {
	"esu_mode":             "SEARCH_EVENT:Last",
	"log_filename_expr":    "FromCCS_AD.csv",
	"log_varnames":         "AD-LINE-NUMBER,AD-DIRECTION,AD-BUS-NUMBER",
	"log_timecol_name":     "AD-MSG-TIMESTAMP",
	"log_start_time_expr":  "<RTAT-MSG-TIMESTAMP>,0",
	"log_stop_time_expr":   "<RES-BUSSTOP-PASS-TIME>,0",
	
	"TF_state":    			"SEARCH RTAT",
	"TF_func":    			"AD_found",
	"TN_state":    			"SEARCH RTAT",
	"TN_func":     			"",
	"TE_state":    			"STOP",
	"TE_func":     			"",
	"GUI_line_num":			"4"
}
STOP = {
	"func":    				"stop"
}
# ----------------------------- FUNCTION PART -----------------------------
def start():
	global counter
	counter = 0
	print("  Transition-function: start_function")
	set_sbk_file("EPT","SBK_ID","RTAT-BUS-NUMBER","RTAT-LINE-NUMBER","RTAT-DIRECTION","RTAT-SIGN-NUMBER",
				 "RTAT-MSG-TIMESTAMP","RTAT-TAT-TIME","LOG-MSG-TIMESTAMP","RES-BUS-START-TIME",
				 "RES-BUSSTOP-PASS-TIME","BQD-MSG-TIMESTAMP","AD-MSG-TIMESTAMP",
				 "RES-PASS-TIME-ERROR","RES-BQD-TIME-ERROR")
	set_datetime_variable("SET-START-TIMESTAMP","INT-START-DATE","INT-START-TIME")
	set_datetime_variable("SET-STOP-TIMESTAMP","INT-START-DATE","INT-STOP-TIME")
	copy_variable("RTAT-LINE-NUMBER","SET-LINE-NUMBER")
	copy_variable("RTAT-DIRECTION","SET-LINE-DIR")
	copy_variable("RTAT-MSG-TIMESTAMP","SET-START-TIMESTAMP")
	#copy_variable("INT-STOP-TIMESTAMP","SET-STOP-TIMESTAMP")

def RTAT_onentry():
	global counter
	counter += 1
	print("  Onentry-function: RTAT_onentry")
	copy_variable("INT-START-TIMESTAMP","RTAT-MSG-TIMESTAMP")
	copy_variable("INT-STOP-TIMESTAMP","SET-STOP-TIMESTAMP")
	if counter > 2:
		rtat_timestamp = get_time_variable_value("RTAT-TAT-TIME")
		stop_timestamp =  rtat_timestamp + datetime.timedelta(seconds=1800)
		set_variable("INT-STOP-TIMESTAMP",str(stop_timestamp))

def LOGIN_found():
	print("  Transition-function: Found_LOGIN")
	copy_variable("INT-BUS-START-SEARCH-TIME","LOG-MSG-TIMESTAMP")
	#copy_variable("LOCAT-BUS-NUMBER","LOG-BUS-NUMBER")
	print("")
def LOGIN_not_found():
	print("  Transition-function: Not_found_LOGIN")
	copy_variable("INT-BUS-START-SEARCH-TIME","RTAT-MSG-TIMESTAMP")
def starting_found():
	print("  Transition-function: Found_START")
	copy_variable("RES-BUS-START-TIME","INT-LOCAT-TIME-OLD")
def arriving_found():
	print("  Transition-function: Found_PASS")
	copy_variable("BQD-LINE-NUMBER","LOG-LINE-NUMBER")
	copy_variable("BQD-BUS-NUMBER","LOG-BUS-NUMBER")
		
	locat_old_timestamp = get_time_variable_value("INT-LOCAT-TIME-OLD")
	locat_new_timestamp = get_time_variable_value("INT-LOCAT-TIME-NEW")
	#print("  locat_old_timestamp: %s" % locat_old_timestamp)
	#print("  locat_new_timestamp: %s" % locat_new_timestamp)
	
	time_diff = locat_new_timestamp - locat_old_timestamp
	print("  time_diff: %d" % time_diff.seconds)
	
	passing_time =  locat_old_timestamp + datetime.timedelta(seconds= time_diff.seconds / 2)
	set_variable("RES-BUSSTOP-PASS-TIME",str(passing_time))
def BQD_found():
	print("  Transition-function: Found_BQD")
	copy_variable("AD-LINE-NUMBER","LOG-LINE-NUMBER")
	copy_variable("AD-BUS-NUMBER","LOG-BUS-NUMBER")
	copy_variable("AD-DIRECTION","LOG-DIRECTION")
	copy_variable("RES-BQD-TIME","BQD-MSG-TIMESTAMP")
def AD_found():
	print("  Transition-function: Found_AD")
	rtat_timestamp = get_time_variable_value("RTAT-TAT-TIME")
	
	ad_value_dec = get_variable_int_value("AD-VALUE",16)
	print("  ad_value_dec = %d (hex: %s)" % (ad_value_dec,get_variable_str_value("AD-VALUE")))
	
	if get_variable_str_value("AD-TYPE") == "1":
		ad_value = ad_value_dec
	else:
		ad_value = 0 - ad_value_dec
		
	rtat_ad_timestamp =  rtat_timestamp + datetime.timedelta(seconds=ad_value)
	set_variable("RES-RTAT-AD-VALUE",str(rtat_ad_timestamp))
	
	passing_time = get_time_variable_value("RES-BUSSTOP-PASS-TIME")
	passing_time_error = passing_time - rtat_ad_timestamp
	#print("  passing_time_error: %d" % passing_time_error.seconds)
	
	set_variable("RES-PASS-TIME-ERROR",str(passing_time_error.seconds))
	
	bqd_time = get_time_variable_value("BQD-MSG-TIMESTAMP")
	bqd_time_error = passing_time - bqd_time
	#print("  bqd_time_error: %d" % bqd_time_error.seconds)
	
	set_variable("RES-BQD-TIME-ERROR",str(bqd_time_error.seconds))

	print_sbk_file()
def stop():
	print_sbk_file()

# EPT (Estimated Passing Time) 26.9.2015 EHE
