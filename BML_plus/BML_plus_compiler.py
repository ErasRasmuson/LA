# -*- coding: cp1252 -*-
#******************************************************************************
#
#   This script reads and parses a log data query in novel BML+ language and 
#   compiles (or converts) it to BML language that is pure Python.
#   LOGDIG tool understands Python based BML language.
#
#   HEADER:     BML_plus_compiler.py 
#   AUTHOR:     Esa Heikkinen
#   DATE:       26.08.2024
#
#******************************************************************************

from lark import Lark, Transformer, v_args, Tree, Token
import time
from datetime import datetime
import csv
import logging
import pprint
import argparse
import os
import re

# Setup logging
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.CRITICAL)

pp = pprint.PrettyPrinter(width=2)

#******************************************************************************
#
#   GRAMMAR for BML+
#
#******************************************************************************

# Define the grammar for a BML+
bml_plus_grammar = """
bml_plus: data_driven_part function_part?

data_driven_part: "VARIABLES" "{" variables_clause "}" pattern_clause 
variables_clause: variable value ("," variable value)*

function_part: "FUNCTIONS" "{" functions_clause "}"
functions_clause: function (function)*
function: function_call "{{" python_code "}}"
python_code: /(.|\\n)+?(?=\\}\\})/s

pattern_clause: "PATTERN" "{" from_clause? select_clause? \
        start_state state_clauses common_stop_state_clause? \
        result_clause? "}"
state_clauses: state_clause (state_clause)*
start_state: "START[" state_entry_clause? "]"
state_clause: "=>" state "[" state_entry_clause? "]" "{" state_data_clause "}" 
state_data_clause: from_clause? select_clause? \
        where_clause within_clause next_clause?

from_clause: "FROM" logfile "TIMECOL" timecol
select_clause: "SELECT" select_policy
where_clause: "WHERE" compare_expr ("AND" compare_expr)*
within_clause: "WITHIN" time_expr "TO" time_expr
next_clause: "NEXT" "[" state_onexit_clause? "]" "{" found_state_clause? not_found_state_clause? \
        exit_state_clause? "}"

state_onexit_clause: state_exit_clause
found_state_clause: "+>" state "[" state_exit_clause? "]"
not_found_state_clause: "->" state "[" state_exit_clause? "]"
exit_state_clause: "~>" state "[" state_exit_clause? "]"

common_stop_state_clause: "STOP" "[" state_entry_clause? "]"


result_clause: "RESULT" "{" "FILE" result_file "," \
        result_variables_clause "}"
result_variables_clause: "VARIABLES" "{" variable ("," variable)* "}"
result_file: NAME

logfile: logfile_beginning ("<" logfile_variable ">")? "." logfile_end
logfile_beginning: NAME
logfile_end: NAME
logfile_variable: NAME

timecol: NAME
!select_policy: "SEARCH_EVENT:First" | "SEARCH_EVENT:Last" | "First:NextRow"
compare_expr: comparison_item comparison_op comparison_item

!comparison_op: ">" | "<" | "==" | "!="
comparison_item: variable | value

expression: NAME "=" term
term: variable | value
value: NUMBER | QUOTED_STRING

time_expr: variable offset?
state: NAME
offset: NUMBER
variable: NAME

state_entry_clause: state_entry_expr (";" state_entry_expr)*
state_exit_clause: state_exit_expr (";" state_exit_expr)*

state_entry_expr: function_call | expression
state_exit_expr: function_call | expression

function_call: function_name "(" parameters ")"
function_name: NAME
parameters: parameter? ("," parameter)*
parameter: term

QUOTED_STRING: /"[^"]*"/ | /'[^']*'/

// Custom rule for variable names with minus signs
NAME: /[a-zA-Z_][a-zA-Z0-9_-]*/

%import common.ESCAPED_STRING
%import common.SIGNED_NUMBER -> NUMBER
%import common.WS
%ignore WS
"""

#******************************************************************************
#
#   FUNCTIONS for transformer
#
#******************************************************************************
def extract_value(item):
    if isinstance(item, Tree):
        return [extract_value(child) for child in item.children]
    elif isinstance(item, Token):
        return item.value
    else:
        return item

class BMLPlusTransformer(Transformer):
    def bml_plus(self, items):
        logging.debug(f'bml_plus: {items}')
        return {
            "data_driven_part": items[0],
            "function_part": items[1] if len(items) > 1 else None
        }
    
    def data_driven_part(self, items):
        logging.debug(f'data_driven_part: {items}')
        return {
            "variables_clause": items[0],
            "pattern_clause": items[1]
        }
    
    def function_part(self, items):
        logging.debug(f'function_part: {items}')
        return {
            #functions_clause": extract_value(items[0])
            "functions_clause": items[0]
        }
    
    def functions_clause(self, items):
        logging.debug(f'functions_clause: {items}')
        # items is a list of dictionaries, each representing a function
        return items  # Return the list as is

    def function(self, items):
        logging.debug(f'function: {items}')
        # Assuming items[0] is the function name, items[1:-1] are parameters, and items[-1] is the Python code
        return {
            #"function_name": items[0],
            #"parameters": items[1:-1],  # all except the last one which is the Python code
            "function_call": items[0],
            "python_code": items[1]  # the last item in the list is the Python code
        }

    def variables_clause(self, items):
        logging.debug(f'variables_clause: {items}')
        variables = {items[i]: items[i + 1] for i in range(0, len(items), 2)}
        return variables

    def pattern_clause(self, items):
        logging.debug(f'pattern_clause: {items}')
        pattern = {}
        for item in items:
            #print(f"item: {item}")
            #pp.pprint(item)
            pattern.update(item)
        return pattern

    def state_clauses(self, items):
        logging.debug(f'state_clauses: {items}')
        #pp.pprint(items)
        return {"state_clauses" : items}

    def start_state(self, items):
        logging.debug(f'start_state: {items}')
        return {"start_state": extract_value(items[0]) if items else None}

    def state_clause(self, items):
        logging.debug(f'state_clause: {items}')
        #pp.pprint(items)

        if len(items) == 2:
            return {
                "state": extract_value(items[0]),
                "state_data_clause": extract_value(items[1])
            }
        elif len(items) == 3:
            return {
                "state": extract_value(items[0]),
                "state_entry_clause": extract_value(items[1]),
                "state_data_clause": extract_value(items[2])
            }
        else:
            return {None}          

    def state_data_clause(self, items):
        logging.debug(f'state_data_clause: {items}')
        state_data = {}
        for item in items:
            state_data.update(item)
        return state_data
    
    def from_clause(self, items):
        logging.debug(f'from_clause: {items}')
        return {"from_clause": {"logfile": extract_value(items[0]), "timecol": extract_value(items[1])}}
    
    def select_clause(self, items):
        logging.debug(f'select_clause: {items}')
        return {"select_clause": {"select_policy": extract_value(items[0])}}
    
    def where_clause(self, items):
        logging.debug(f'where_clause: {items}')
        # Ensure items is a list of dicts and merge them
        conditions = []
        for item in items:
            if isinstance(item, dict):
                conditions.append(item)
            else:
                conditions.append({"condition": item})
        return {"where_clause": {"conditions": conditions}}
    
    def within_clause(self, items):
        logging.debug(f'within_clause: {items}')
        return {"within_clause": {"time_expr_start": items[0], "time_expr_end": items[1]}}
    
    def next_clause(self, items):
        logging.debug(f'next_clause: {items}')
        next_clauses = {}
        for item in items:
            next_clauses.update(item)
        return {"next_clause": next_clauses}
    
    def found_state_clause(self, items):
        logging.debug(f'found_state_clause: {items}')
        return {"found_state_clause": {"state": items[0], "state_exit_clause": items[1] if len(items) > 1 else None}}
    
    def not_found_state_clause(self, items):
        logging.debug(f'not_found_state_clause: {items}')
        return {"not_found_state_clause": {"state": items[0], "state_exit_clause": items[1] if len(items) > 1 else None}}
    
    def exit_state_clause(self, items):
        logging.debug(f'exit_state_clause: {items}')
        return {"exit_state_clause": {"state": items[0], "state_exit_clause": items[1] if len(items) > 1 else None}}
    
    def common_stop_state_clause(self, items):
        logging.debug(f'common_stop_state_clause: {items}')
        return {"common_stop_state_clause": items[0] if items else None}
    '''
    def common_exit_state_clause(self, items):
        logging.debug(f'common_exit_state_clause: {items}')
        return {"common_exit_state_clause": items[0] if items else None}
    '''
    def state_onexit_clause(self, items):
        logging.debug(f'state_onexit_clause: {items}')
        return {"state_onexit_clause": items[0] if items else None}

    def result_clause(self, items):
        logging.debug(f'result_clause: {items}')
        return {"result_clause": {"result_file": extract_value(items[0]), 
                                  "result_variables_clause": extract_value(items[1])}}
    def result_variables_clause(self, items):
        logging.debug(f'result_variables_clause: {items}')
        variables = []
        for item in items:
            #print(f"item {item}")
            variables.append(item)
        return variables

    def function_call(self, items):
        logging.debug(f'function_call: {items}')
        return {"function_name": extract_value(items[0]), "parameters": extract_value(items[1:])}
    
    def parameters(self, items):
        logging.debug(f'parameters: {items}')
        return items
    
    def parameter(self, items):
        logging.debug(f'parameter: {items}')
        return items[0]
    
    def python_code(self, items):
        logging.debug(f'python_code: {items}')
        return extract_value(items[0]).strip()  # items[0] is a string, not a token
    
    def state(self, items):
        logging.debug(f'state: {items}')
        return items[0]
    
    def variable(self, items):
        logging.debug(f'variable: {items}')
        return items[0]
    
    # Process value, which can be either a number or a quoted string
    def value(self, items):
        item = items[0]
        if item.type == "NUMBER":
            # Convert the number to an integer or float
            try:
                return int(item)  # If it's an integer
            except ValueError:
                return float(item)  # If it's a float
        elif item.type == "QUOTED_STRING":
            # Strip the quotes and return the string
            return item[1:-1]  # Remove the surrounding quotes

    def time_expr(self, items):
        logging.debug(f'time_expr: {items}')
        #return extract_value(items[0])
        return {"variable": items[0], "offset": extract_value(items[1])[0] if len(items) > 1 else 0}

    def comparison_item(self, items):
        logging.debug(f'comparison_item: {items}')
        return items[0]
    
    def comparison_op(self, items):
        logging.debug(f'comparison_op: {items}')
        return items[0]
    
    def compare_expr(self, items):
        logging.debug(f'compare_expr: {items}')
        return {"left": items[0], "op": items[1], "right": items[2]}
    
    def expression(self, items):
        logging.debug(f'expression: {items}')
        return {"variable": items[0], "value": items[1]}
    
    def term(self, items):
        logging.debug(f'term: {items}')
        return items[0]

    def state_entry_expr(self, items):
        logging.debug(f'state_entry_expr: {items}')
        if isinstance(items[0], dict) and 'function_name' in items[0]:
            return {"type": "function_call", "value": items[0]}
        else:
            return {"type": "expression", "value": items[0]}
    
    def state_exit_expr(self, items):
        logging.debug(f'state_exit_expr: {items}')
        if isinstance(items[0], dict) and 'function_name' in items[0]:
            return {"type": "function_call", "value": items[0]}
        else:
            return {"type": "expression", "value": items[0]}

    def state_entry_clause(self, items):
        logging.debug(f'state_entry_clause: {items}')
        return [extract_value(item) for item in items]
    
    def state_exit_clause(self, items):
        logging.debug(f'state_exit_clause: {items}')
        return [extract_value(item) for item in items]


#******************************************************************************
#
#   FUNCTIONS and TEMPLATES for generating python (BML) code
#
#******************************************************************************

template_state_dict = """
ESU["{esu_state}"] = {{
    "esu_mode":             "{esu_mode}",
    "log_filename_expr":    "{log_filename_expr}",
    "log_varnames":         "{log_varnames}",
    "log_varexprs":         "{log_varexprs}",
    "log_timecol_name":     "{log_timecol_name}",
    "log_start_time_expr":  "{log_start_time_expr}",
    "log_stop_time_expr":   "{log_stop_time_expr}",
    "log_events_max":       "{log_events_max}",
    "ssd_lat_col_name":     "{ssd_lat_col_name}",
    "ssd_lon_col_name":     "{ssd_lon_col_name}",
    "ssd_filename_expr":    "{ssd_filename_expr}",
    "ssd_varnames":         "{ssd_varnames}",
    "TF_state":    "{TF_state}",
    "TF_func":     "{TF_func}",
    "TN_state":    "{TN_state}",
    "TN_func":     "{TN_func}",
    "TE_state":    "{TE_state}",
    "TE_func":     "{TE_func}",
    "onentry_func": "{onentry_func}",
    "onexit_func" : "{onexit_func}",
    "GUI_line_num": "{GUI_line_num}"
}}
"""
# "log_varnames":         "{log_varnames}", -> log_varexprs korvaa tämän!?

def get_nested_value(data, keys):
    """
    Recursively retrieve a value from a nested dictionary using a list of keys.
    Args:
        data (dict): The dictionary to search.
        keys (list): A list of keys representing the path to the value.
    Returns:
        The value if found, otherwise None.
    """
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return None
    return data


def convert_value_type(value):

    if isinstance(value, (int, float)):
        #print(f"value {value} is number")
        # It's a number, so generate the appropriate code for a numeric value
        value = str(value)  # Convert to string for code generation
    elif isinstance(value, Token):
        #print(f"value {value} is Token variable")
        # It's a variable
        value = f"<{value.value}>"
    elif isinstance(value, str):
        #print(f"value {value} is string")
        # It's a string, so generate the appropriate code for a string value
        value = f'\\"{value}\\"'  # Surround the string with quotes in the generated code
    else:
        raise ValueError(f"Unexpected value type: {type(value)}")

    return value

# Function to parse the dictionary into the desired string
def parse_functions_and_expressions(clause):
    result = []
    for item in clause:

        item_type = item['type']
        if item_type == 'function_call':
            function_name = item['value']['function_name'][0]  # Assuming only one function name

            # This is special function related to printing SBK results
            if function_name == "PRINT_RESULT":
                function_name = "print_sbk_file"

            #parameters = ', '.join([token.value for param in item['value']['parameters'] for token in param])
            parameters = ','.join([convert_value_type(token) for param in item['value']['parameters'] for token in param])
            result.append(f"ana_new.{function_name}({parameters})")
        
        elif item_type == 'expression':
            #variable = item['value']['variable'].value
            variable = item['value']['variable']
            #value = item['value']['value'].value
            value = item['value']['value']

            print(f"variable {variable} value {value}")

            try:
                value = convert_value_type(value)
            except:
                break

            result.append(f"<{variable}> = {value}")
    
    return ';'.join(result)

def parse_logfile_expr(log_filename_expr):

    log_filename_str = f"{log_filename_expr[0][0]}"
    if len(log_filename_expr) > 2:
        log_filename_str += f"<{log_filename_expr[1][0]}>"
    log_filename_str += f".{log_filename_expr[-1][0]}"

    print(f"log_filename_str {log_filename_str}")
    return log_filename_str

def generate_condition(condition):
    # Extract left, op, and right values, handling both Tokens and raw values
    #left = condition['left'].value if isinstance(condition['left'], Token) else condition['left']
    op = condition['op'].value if isinstance(condition['op'], Token) else condition['op']
    #right = condition['right'].value if isinstance(condition['right'], Token) else condition['right']

    try:
        left = convert_value_type(condition['left'])
        right = convert_value_type(condition['right'])
    except:
        return f""

    # Return the generated condition as a string
    return f"{left}{op}{right}"

def generate_code_from_conditions(conditions_dict):
    # Extract the list of conditions
    conditions = conditions_dict['conditions']

    # Generate code for each condition
    condition_strings = [generate_condition(cond) for cond in conditions]

    # Combine all conditions with 'AND' (you could use 'OR' or other operators if needed)
    #return " AND ".join(condition_strings)
    return ",".join(condition_strings)

def adjust_indentation(code_string):
    # Split the string into individual lines
    lines = code_string.split('\n')
    
    # List to hold the adjusted lines
    adjusted_lines = []
    
    for line in lines:
        # Count the number of leading spaces
        leading_spaces = len(line) - len(line.lstrip(' '))
        
        # If indentation is more than 4 spaces, reduce it by 4
        if leading_spaces > 4:
            adjusted_line = line[4:]  # Remove 4 leading spaces
        else:
            adjusted_line = line  # Leave the line as is
        
        # Check if the line contains a word surrounded by "<" and ">"
        if re.search(r'<[^<>]+>', adjusted_line):
            # If found, wrap the line inside statem()
            adjusted_line = f'statem({adjusted_line.strip()})'
        
        # Append the adjusted line to the list
        adjusted_lines.append(adjusted_line)
    
    # Join the adjusted lines back into a single string with \n
    adjusted_code_string = '\n'.join(adjusted_lines)
    
    return adjusted_code_string

def generate_python_code(transformed_data):
    # Initialize code parts
    header = [f"\n# This python file:                    {python_file}"]
    header.append(f"# is compiled from bml+ language file: {bml_plus_file}")
    header.append(f"# Time: {timestamp}\n")

    imports = ["from logdig_analyze_template import *"]
    variables_code = []
    functions_code = []
    pattern_code = []

    # Process variables
    variables_code.append(f"\n# ----------------------------- DATA-DRIVEN PART -----------------------------")
    variables = transformed_data["data_driven_part"]["variables_clause"]
    #print(f"variables: {variables}")
    variables_code.append(f"VARIABLES = {{")
    for var, value in variables.items():
        variables_code.append(f"    \"{var}\" : \"{value}\",")
    variables_code.append(f"}}")

    # Process pattern (state machine logic)
    pattern = transformed_data["data_driven_part"]["pattern_clause"]
    #print(f"pattern: {pattern}\n")
    #pp.pprint(pattern)

    state_clauses = pattern.get("state_clauses", [])
    #print(f"state_clauses: {state_clauses}\n")

    # Gets only state names
    state_list = []
    for clause in state_clauses:
        state = clause["state"]
        state_list.append(state)

    print(f"state_list {state_list}")

    state_num = len(state_clauses)
    print(f"state_num {state_num}")

    # RESULTS
    result_clause = get_nested_value(pattern,["result_clause"])
    #print(f"result_clause {result_clause}")
    sbk_str = ""
    result_file = ""
    if result_clause != None:
        result_file = get_nested_value(result_clause,["result_file"])[0]
        print(f"result_file {result_file}")

        result_variables_clause = get_nested_value(result_clause,["result_variables_clause"])
        #print(f"result_variables_clause {result_variables_clause}")
        variable_list = [token.value for token in result_variables_clause]

        #pattern_code.append(f"\n# RESULTS = start: {result_start_state} set: {result_set_state} end: {result_end_state} vars: {variable_list}")
        pattern_code.append(f"\n# RESULTS = result_file: {result_file} vars: {variable_list}")

        sbk_str = f'\\"{result_file}\\",'
        sbk_str += ','.join([f'\\"{var}\\"' for var in variable_list])

    #start_state = pattern["start_state"]
    start_state = pattern.get("start_state", [])

    start_func_list = []
    start_func = ""

    if sbk_str != "":
        start_func_list.append(f"ana.set_sbk_file({sbk_str})")

    if start_state != None:
        start_func = parse_functions_and_expressions(start_state)
        start_func_list.append(start_func)

    start_func_str = ';'.join([f"{start_func}" for start_func in start_func_list])
    if start_func_str != "":
        start_func_str = f"S:{start_func_str}"

    pattern_code.append(f"START = {{")
    pattern_code.append(f"    \"state\": \"{state_list[0]}\",")   
    pattern_code.append(f'    \"func\":  \"{start_func_str}"')
    pattern_code.append(f"}}")  

    log_filename_expr_common = get_nested_value(pattern,["from_clause","logfile"])
    log_timecol_name_common = get_nested_value(pattern,["from_clause","timecol"])
    select_policy_common = get_nested_value(pattern,["select_clause","select_policy"])

    state_counter = 0
    for clause in state_clauses:
        #print(f"clause: {clause}\n")
        #pp.pprint(clause)
        state = clause["state"]

        sbk_result_set_command = ""
        #if result_set_state == state:
        #    sbk_result_set_command = "ana.print_sbk_file()"

        select_policy =  get_nested_value(clause,["state_data_clause","select_clause","select_policy"])
        if select_policy == None:
            select_policy = select_policy_common

        # If list type, takes first item
        if select_policy != None:
            select_policy = select_policy[0]

        log_filename_expr = get_nested_value(clause,["state_data_clause","from_clause","logfile"])
        if log_filename_expr == None:
            log_filename_expr = log_filename_expr_common
    
        # If list type, takes first item
        if log_filename_expr != None:
            #log_filename_expr = log_filename_expr[0]
            log_filename_expr = parse_logfile_expr(log_filename_expr)

        log_timecol_name = get_nested_value(clause,["state_data_clause","from_clause","timecol"])
        if log_timecol_name == None:
            log_timecol_name = log_timecol_name_common

        # If list type, takes first item
        if log_timecol_name != None:
            log_timecol_name = log_timecol_name[0]

        log_where_conditions = generate_code_from_conditions(get_nested_value(clause,["state_data_clause","where_clause"]))
        print(f"log_where_conditions {log_where_conditions}")

        start_time_expr = get_nested_value(clause,["state_data_clause","within_clause","time_expr_start"])
        start_time_var = start_time_expr["variable"]
        start_time_offset = start_time_expr["offset"]
        print(f"start_time_var {start_time_var} start_time_offset {start_time_offset}")
        log_start_time_expr = f"<{start_time_var}>,{start_time_offset}"

        stop_time_expr = get_nested_value(clause,["state_data_clause","within_clause","time_expr_end"])
        stop_time_var = stop_time_expr["variable"]
        stop_time_offset = stop_time_expr["offset"]
        print(f"stop_time_var {stop_time_var} stop_time_offset {stop_time_offset}")
        log_stop_time_expr = f"<{stop_time_var}>,{stop_time_offset}"

        TF_state = get_nested_value(clause,["state_data_clause","next_clause","found_state_clause","state"])
        TN_state = get_nested_value(clause,["state_data_clause","next_clause","not_found_state_clause","state"])
        TE_state = get_nested_value(clause,["state_data_clause","next_clause","exit_state_clause","state"])

        if TF_state == None:
            # Gets next state. If last one, takes first.
            TF_state = state_list[(state_counter + 1 ) % state_num]

        if TN_state == None:
            TN_state = "STOP"

        if TE_state == None:
            TE_state = "STOP"

        # STATE TRANSITIONS FUNCTIONS AND EXPRESSIONS
        TF_func = ""
        TF_func_tree = get_nested_value(clause,["state_data_clause","next_clause","found_state_clause","state_exit_clause"])
        if TF_func_tree != None:
            TF_func = "S:" + parse_functions_and_expressions(TF_func_tree)

        TN_func = ""
        TN_func_tree = get_nested_value(clause,["state_data_clause","next_clause","not_found_state_clause","state_exit_clause"])
        if TN_func_tree != None:
            TN_func = "S:" + parse_functions_and_expressions(TN_func_tree)

        TE_func = ""
        TE_func_tree = get_nested_value(clause,["state_data_clause","next_clause","exit_state_clause","state_exit_clause"])
        if TE_func_tree != None:
            TE_func = "S:" + parse_functions_and_expressions(TE_func_tree)

        # STATE ONENTRY FUNCTIONS AND EXPRESSIONS
        state_entry = ""
        state_entry_tree = get_nested_value(clause,["state_entry_clause"])
        if state_entry_tree != None:
            state_entry = parse_functions_and_expressions(state_entry_tree)

        print(f"state_entry {state_entry}")

        if state_entry != "":
            state_entry = f"S:{state_entry}"

        # STATE ONEXIT FUNCTIONS AND EXPRESSIONS
        onexit_func_list = []
        state_exit = ""
        state_exit_tree = get_nested_value(clause,["state_data_clause","next_clause","state_onexit_clause"])
        if state_exit_tree != None:
            state_exit = parse_functions_and_expressions(state_exit_tree)
            onexit_func_list.append(state_exit)

        print(f"state_exit {state_exit}")

        onexit_func_str = ';'.join([f"{func}" for func in onexit_func_list])

        if onexit_func_str != "":
            onexit_func_str = f"S:{onexit_func_str}"

        filled_state_dict = template_state_dict.format(
            esu_state = state,
            esu_mode = select_policy,
            log_filename_expr = log_filename_expr,
            log_varnames = "",
            log_varexprs = log_where_conditions,
            log_timecol_name = log_timecol_name,
            log_start_time_expr = log_start_time_expr,
            log_stop_time_expr = log_stop_time_expr,
            log_events_max = "",
            ssd_lat_col_name = "",
            ssd_lon_col_name = "",
            ssd_filename_expr = "",
            ssd_varnames = "",
            TF_state = TF_state,
            TF_func = TF_func,
            TN_state = TN_state,
            TN_func = TN_func,
            TE_state = TE_state,
            TE_func = TE_func,
            onentry_func = state_entry,
            onexit_func = onexit_func_str,
            GUI_line_num = state_counter
            )

        pattern_code.append(filled_state_dict)

        state_counter += 1

    # STOP state
    stop_state_clause = pattern.get("common_stop_state_clause", [])
    stop_func = ""
    if stop_state_clause != None:
        stop_func = parse_functions_and_expressions(stop_state_clause)

    if stop_func != "":
        stop_func = f"S:{stop_func}"

    pattern_code.append(f"STOP = {{")  
    pattern_code.append(f"    \"func\":  \"{stop_func}\"")  
    pattern_code.append(f"}}") 

    # Process functions (if any)
    if transformed_data["function_part"]:
        functions_code.append(f"\n# ----------------------------- FUNCTION PART -----------------------------")
        functions = transformed_data["function_part"]["functions_clause"]

        #print(f"functions: {functions}")

        for func in functions:

            #print(f"func: {func}")
            #pp.pprint(func)
            func_name = func["function_call"]["function_name"][0]
            #print(f"func_name: {func_name}")
            parameters = ""
            for param in func["function_call"]["parameters"]:
                parameters = ", ".join(param)
            #print(f"parameters: {parameters}")
            code = adjust_indentation(func["python_code"])
            functions_code.append(f"\ndef {func_name}({parameters}):\n    {code}")

    # Adds internal functions
    #functions_code.append(f"\ndef start():")
    #functions_code.append(f"    a = 1")
    # Combine all parts
    code = "\n".join(header + imports + variables_code + pattern_code + functions_code)
    return code

#******************************************************************************
#
#   FUNCTIONS for utilities
#
#******************************************************************************

# Custom pretty-print function
def custom_pretty_print(data, indent=0):
    if isinstance(data, dict):
        for key, value in data.items():
            print(' ' * indent + str(key) + ':')
            custom_pretty_print(value, indent + 4)
    elif isinstance(data, list):
        for item in data:
            custom_pretty_print(item, indent + 4)
    else:
        print(' ' * indent + str(data))

def write_python_file(filename, code):
    with open(filename, 'w') as file:
        file.write(code)


#******************************************************************************
#
#   FUNCTION:   main
#
#******************************************************************************
def main():

    global python_file
    global bml_plus_file
    global timestamp

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    parser = argparse.ArgumentParser()
    parser.add_argument('-bml_plus_path','--bml_plus_path', dest='bml_plus_path', help='bml_plus_path')
    parser.add_argument('-bml_plus_file','--bml_plus_file', dest='bml_plus_file', help='bml_plus_file')
    args = parser.parse_args()

    print("bml_plus_path              : %s" % args.bml_plus_path)
    print("bml_plus_file              : %s" % args.bml_plus_file)

    bml_plus_file = args.bml_plus_file
    name, extension = os.path.splitext(bml_plus_file)

    bml_plus_file_path = args.bml_plus_path + bml_plus_file

    python_file = name + ".py"
    
    python_file_path = args.bml_plus_path + python_file

    print("python_file_path              : %s" % python_file_path)

    # Reading the query from the file
    with open(bml_plus_file_path, 'r') as file:
        query = file.read().strip()
    #print(query)

    parser = Lark(bml_plus_grammar, start='bml_plus', parser='lalr')
    parsed_query = parser.parse(query)
    #print(parsed_query.pretty())

    transformer = BMLPlusTransformer()
    result = transformer.transform(parsed_query)

    print("Transformed result:")
    #pp.pprint(result)
    #custom_pretty_print(result)

    print("Started to generate Python code ...")
    # Generate the Python code based on the transformed data
    python_code = generate_python_code(result)

    # Write the Python code to a file
    write_python_file(python_file_path, python_code)

    print(f"Timestamp: {timestamp}")
    print(f"BML+ code from file: {bml_plus_file_path} has been commpiled to python file: {python_file_path}")

if __name__ == '__main__':
    main()
