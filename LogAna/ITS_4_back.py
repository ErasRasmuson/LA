from logdig_analyze_template import *
# ----------------------------- DATA-DRIVEN PART -----------------------------
VARIABLES = {
	"STARTTIME-DATE":   "2018-11-26",
	"STARTTIME-TIME": 	"10:00:00",
	"STOPTIME-DATE":	"2018-11-26",
	"STOPTIME-TIME": 	"10:30:00",
	"MAX-LOGIN-TAT": 	"600",
	"MAX-TAT-ARRIVE":	"1200",
	"BUS":				"B1",
	"LINE":				"L1",
	"TBSTOP":			"TBS1"
	}
START = {
	"state":   "TAT",
	"func":   "start"
	}
ESU["TAT"] = {
	"esu_mode":             "SEARCH_EVENT:First:NextRow",
	"log_filename_expr":    "ITS_4_monitors.csv",
	"log_varexprs":         "<LAST-Mon-Msg>==\"TAT\" and <LAST-Mon-Bus-Id>==<BUS> and <LAST-Mon-Line>==<LINE>",
	"log_timecol_name":     "Mon-Time",
	"log_start_time_expr":  "<STARTTIME>,0",
	"log_stop_time_expr":   "<STOPTIME>,0",

	"TF_state":    "LOGIN",
	"TF_func":     "S:<TAT-TIME> = <Mon-Time>;",
	"TN_state":    "STOP",
	"TN_func":     "",
	"TE_state":    "STOP",
	"TE_func":     "exit_error"
}
ESU["LOGIN"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "ITS_4_buses.csv",
	"log_varexprs":         "<LAST-Bus-Msg>==\"LOGIN\" and <LAST-Bus-Id>==<Mon-Bus-Id>",
	"log_timecol_name":     "Bus-Time",
	"log_start_time_expr":  "<TAT-FOUND-TIME>,-<MAX-LOGIN-TAT>",
	"log_stop_time_expr":   "<TAT-FOUND-TIME>,0",

	"TF_state":    "LEAVE",
	"TF_func":     "S:<LEAVE-START-TIME>=<LOGIN-FOUND-TIME>;",
	"TN_state":    "LEAVE",
	"TN_func":     "S:<LEAVE-START-TIME>=<STARTTIME>;"
}
ESU["LEAVE"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "ITS_4_buses.csv",
	"log_varexprs":         "<LAST-Bus-Id>==<LAST-Mon-Bus-Id> and <LAST-Bus-StopOut>==<TBSTOP>",
	"log_timecol_name":     "Bus-Time",
	"log_start_time_expr":  "<LEAVE-START-TIME>,0",
	"log_stop_time_expr":   "<TAT-TIME>,+<MAX-TAT-ARRIVE>",

	"TF_state":    "ARRIVE",
	"TF_func":     "",
	"TN_state":    "STOP",
	"TN_func":     ""
}
ESU["ARRIVE"] = {
	"esu_mode":             "SEARCH_EVENT:First",
	"log_filename_expr":    "ITS_4_buses.csv",
	"log_varexprs":         "<LAST-Bus-Id>==<LAST-Mon-Bus-Id> and <LAST-Bus-StopIn>==<LAST-Mon-BusStop>",
	"log_timecol_name":     "Bus-Time",
	"log_start_time_expr":  "<LEAVE-FOUND-TIME>,0",
	"log_stop_time_expr":   "<TAT-FOUND-TIME>,+<MAX-TAT-ARRIVE>",

	"TF_state":    "AD",
	"TF_func":     "",
	"TN_state":    "STOP",
	"TN_func":     ""
}
ESU["AD"] = {
	"esu_mode":             "SEARCH_EVENT:Last",
	"log_filename_expr":    "ITS_4_monitors.csv",
	"log_varexprs":         "<LAST-Mon-Msg>==\"AD\" and <LAST-Mon-Bus-Id>==<LAST-Bus-Id>",
	"log_timecol_name":     "Mon-Time",
	"log_start_time_expr":  "<TAT-FOUND-TIME>,0",
	"log_stop_time_expr":   "<ARRIVE-FOUND-TIME>,0",

	"TF_state":    "TAT2",
	"TF_func":     "S:<STARTTIME>=<TAT-FOUND-TIME>",
	"TN_state":    "STOP",
	"TN_func":     ""
}
ESU["TAT2"] = {
	"esu_mode":             "SEARCH_EVENT:First:NextRow",
	"log_filename_expr":    "ITS_4_monitors.csv",
	"log_varexprs":         "<LAST-Mon-Msg>==\"TAT\" and <LAST-Mon-Bus-Id>==<BUS> and <LAST-Mon-Line>==<LINE>",
	"log_timecol_name":     "Mon-Time",
	"log_start_time_expr":  "<TAT-FOUND-TIME>,0",
	"log_stop_time_expr":   "<STOPTIME>,0",

	"TF_state":    "LEAVE",
	"TF_func":     "S:<TAT-TIME>=<TAT-FOUND-TIME>",
	"TN_state":    "STOP",
	"TN_func":     ""
}
STOP = {
	"func":     "stop"
}

# ----------------------------- FUNCTION PART -----------------------------
def start():
	set_datetime_variable("STARTTIME","STARTTIME-DATE","STARTTIME-TIME")
	set_datetime_variable("STOPTIME","STOPTIME-DATE","STOPTIME-TIME")
	set_sbk_file("ITS_4","BUS","LINE","LEAVE-START-TIME,LEAVE-FOUND-TIME,TAT-FOUND-TIME,ARRIVE-FOUND-TIME,AD-FOUND-TIME")

def exit_error():
	print("exit_error")
	
def stop():
	print_sbk_file()
	