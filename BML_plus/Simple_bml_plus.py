
# This python file:                    Simple_bml_plus.py
# is compiled from bml+ language file: Simple_bml_plus.bml
# Time: 2024-08-30 18:24:59

from logdig_analyze_template import *

# ----------------------------- DATA-DRIVEN PART -----------------------------
VARIABLES = {
    "CASENAME" : "CEL",
    "STARTTIME-DATE" : "2016-06-21",
    "STARTTIME-ORIG" : "12:00:00",
    "STOPTIME-ORIG" : "12:20:00",
    "LOGFILENUM" : "1",
    "EVENT-MAX-LEN" : "599",
}

# RESULTS = result_file: BMU_CEL vars: ['EV-ID', 'EV-START', 'EV-STOP', 'EV-LEN', 'EV-STATUS', 'COUNTER-OK', 'COUNTER-ERROR']
START = {
    "state": "BEGIN",
    "func":  "S:ana.set_sbk_file(\"BMU_CEL\",\"EV-ID\",\"EV-START\",\"EV-STOP\",\"EV-LEN\",\"EV-STATUS\",\"COUNTER-OK\",\"COUNTER-ERROR\");ana_new.start()"
}

ESU["BEGIN"] = {
    "esu_mode":             "SEARCH_EVENT:First",
    "log_filename_expr":    "Logfile_<LOGFILENUM>.csv",
    "log_varnames":         "",
    "log_varexprs":         "<LAST-EV-PAR>==\"B\"",
    "log_timecol_name":     "EV-TIME",
    "log_start_time_expr":  "<STARTTIME>,+1",
    "log_stop_time_expr":   "<STOPTIME>,0",
    "log_events_max":       "",
    "ssd_lat_col_name":     "",
    "ssd_lon_col_name":     "",
    "ssd_filename_expr":    "",
    "ssd_varnames":         "",
    "TF_state":    "END",
    "TF_func":     "S:<EV-START> = <EV-TIME>",
    "TN_state":    "STOP",
    "TN_func":     "",
    "TE_state":    "STOP",
    "TE_func":     "",
    "onentry_func": "",
    "onexit_func" : "",
    "GUI_line_num": "0"
}


ESU["END"] = {
    "esu_mode":             "SEARCH_EVENT:First",
    "log_filename_expr":    "Logfile_<LOGFILENUM>.csv",
    "log_varnames":         "",
    "log_varexprs":         "<LAST-EV-PAR>==\"E\",<EV-ID>==<LAST-EV-ID>",
    "log_timecol_name":     "EV-TIME",
    "log_start_time_expr":  "<EV-START>,0",
    "log_stop_time_expr":   "<STOPTIME>,0",
    "log_events_max":       "",
    "ssd_lat_col_name":     "",
    "ssd_lon_col_name":     "",
    "ssd_filename_expr":    "",
    "ssd_varnames":         "",
    "TF_state":    "BEGIN",
    "TF_func":     "S:<EV-STOP> = <EV-TIME>;ana_new.found_end();<STARTTIME> = <EV-START>;ana_new.print_sbk_file()",
    "TN_state":    "STOP",
    "TN_func":     "",
    "TE_state":    "STOP",
    "TE_func":     "",
    "onentry_func": "",
    "onexit_func" : "",
    "GUI_line_num": "1"
}

STOP = {
    "func":  ""
}

# ----------------------------- FUNCTION PART -----------------------------

def start():
    set_datetime_variable("STARTTIME","STARTTIME-DATE","STARTTIME-ORIG")
    set_datetime_variable("STOPTIME","STARTTIME-DATE","STOPTIME-ORIG")

    set_counter("COUNTER-OK",0)
    set_counter("COUNTER-ERROR",0)

def found_end():
    set_variable("EV-STATUS","OK")
    calc_time_diff("TIME-DIFF","EV-LEN","EV-STOP","EV-START")
    if compare_variable("ERR-TIME","EV-LEN",">","EVENT-MAX-LEN") == 1:
        set_variable("EV-STATUS","ERR")
        incr_counter("COUNTER-ERROR")
    else:
        incr_counter("COUNTER-OK")