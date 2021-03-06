from logdig_analyze_template import *
# ----------------------------- DATA-DRIVEN PART -----------------------------
VARIABLES = {
	"INT-START-DATE":    		"21.08.06",
	"INT-START-TIME":    		"03:00:00",
	"INT-STOP-TIME":     		"23:00:00",
	"SET-LINE-NUMBER":   		"002132",
	"SET-LINE-DIR":   	 		"2",
	"SET-MAX-LOGIN-RTAT-TIME": 	"1200",
	"SET-MAX-RTAT-PASS-TIME":  	"1800",
	"SET-MAX-PASS-ERR-TIME":   	"120"
	}
START = {
	"state":   				"RTAT",
	"func":   				"start"
	}
ESU["RTAT"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "FromCCS_RTAT.csv",
	"log_varnames":         "RTAT-LINE-NUMBER",
	"log_timecol_name":     "RTAT-MSG-TIMESTAMP",
	"log_start_time_expr":  "<INT-START-TIMESTAMP>,+1",
	"log_stop_time_expr":   "<INT-STOP-TIMESTAMP>,0",
	
	"TF_state":    			"LOGIN",
	"TN_state":    			"STOP",
	"TE_state":    			"STOP",
	"onentry_func": 		"RTAT_onentry",
	"GUI_line_num":			"2"
}
ESU["LOGIN"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "Apo_<LOG-BUS-NUMBER>_LOG.csv",
	"log_varnames":         "LOG-MSG-TYPE=LOGIN,LOG-BUS-NUMBER=<RTAT-BUS-NUMBER>,LOG-LINE-NUMBER=<SET-LINE-NUMBER>,LOG-DIRECTION=<RTAT-DIRECTION>",
	"log_timecol_name":     "LOG-MSG-TIMESTAMP",
	"log_start_time_expr":  "<RTAT-MSG-TIMESTAMP>,-<SET-MAX-LOGIN-RTAT-TIME>",
	"log_stop_time_expr":   "<RTAT-MSG-TIMESTAMP>,0",
	
	"TF_state":    			"Starting",
	"TF_func":     			"LOGIN_found",
	"TN_state":    			"Starting",
	"TN_func":     			"LOGIN_not_found",
	"TE_state":    			"STOP",
	"GUI_line_num":			"0"
}
ESU["Starting"] = {
	"esu_mode":            	"SEARCH_POSITION:Leaving",
	"log_filename_expr":   	"Apo_<LOG-BUS-NUMBER>_LOCAT.csv",
	"log_varnames":        	"LOCAT-BUS-NUMBER=<LOG-BUS-NUMBER>",
	"log_timecol_name":    	"LOCAT-MSG-TIMESTAMP",
	"log_start_time_expr": 	"<INT-BUS-START-SEARCH-TIME>,0",
	"log_stop_time_expr":  	"<INT-BUS-START-SEARCH-TIME>,+<SET-MAX-RTAT-PASS-TIME>",

	"ssd_lat_col_name":    	"LOCAT-LATITUDE",
	"ssd_lon_col_name":    	"LOCAT-LONGITUDE",
	"ssd_filename_expr":   	"terminal_busstop_<LOG-LINE-NUMBER><LOG-DIRECTION>.csv",
	"ssd_varnames":        	"LOG-LINE-NUMBER,LOG-DIRECTION",

	"TF_state":				"Arriving",
	"TF_func":     			"starting_found",
	"TN_state":    			"RTAT",
	"TN_func":     			"",
	"TE_state":    			"STOP",
	"TE_func":     			"",
	"GUI_line_num":			"1"
}
ESU["Arriving"] = {
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
	
	"TF_state":    			"RTAT",
	"TF_func":     			"arriving_found",
	"TN_state":    			"RTAT",
	"TN_func":     			"",
	"TE_state":    			"STOP",
	"TE_func":     			"",
	"GUI_line_num":			"3"
}
STOP = {
	"func":    				"stop"
}
# ----------------------------- FUNCTION PART -----------------------------
def start():
	print("  Transition-function: start_function")
	set_sbk_file("EPT","SBK_ID","RTAT-BUS-NUMBER","RTAT-LINE-NUMBER","RTAT-DIRECTION","RTAT-SIGN-NUMBER",
				 "RTAT-MSG-TIMESTAMP","RTAT-TAT-TIME","LOG-MSG-TIMESTAMP","RES-BUS-START-TIME",
				 "RES-BUSSTOP-PASS-TIME")
	set_datetime_variable("SET-START-TIMESTAMP","INT-START-DATE","INT-START-TIME")
	set_datetime_variable("SET-STOP-TIMESTAMP","INT-START-DATE","INT-STOP-TIME")
	copy_variable("RTAT-LINE-NUMBER","SET-LINE-NUMBER")
	copy_variable("RTAT-DIRECTION","SET-LINE-DIR")
	copy_variable("RTAT-MSG-TIMESTAMP","SET-START-TIMESTAMP")
	copy_variable("INT-STOP-TIMESTAMP","SET-STOP-TIMESTAMP")

def RTAT_onentry():
	print("  Onentry-function: RTAT_onentry")
	copy_variable("INT-START-TIMESTAMP","RTAT-MSG-TIMESTAMP")
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
	#copy_variable("BQD-LINE-NUMBER","LOG-LINE-NUMBER")
	#copy_variable("BQD-BUS-NUMBER","LOG-BUS-NUMBER")
		
	locat_old_timestamp = get_time_variable_value("INT-LOCAT-TIME-OLD")
	locat_new_timestamp = get_time_variable_value("INT-LOCAT-TIME-NEW")
	#print("  locat_old_timestamp: %s" % locat_old_timestamp)
	#print("  locat_new_timestamp: %s" % locat_new_timestamp)
	
	time_diff = locat_new_timestamp - locat_old_timestamp
	print("  time_diff: %d" % time_diff.seconds)
	
	passing_time =  locat_old_timestamp + datetime.timedelta(seconds= time_diff.seconds / 2)
	set_variable("RES-BUSSTOP-PASS-TIME",str(passing_time))

	print_sbk_file()
def stop():
	print_sbk_file()

# EPT (Estimated Passing Time) 26.9.2015 EHE
