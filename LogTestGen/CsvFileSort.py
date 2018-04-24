# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	CsvFileSort.py

AUTHOR:     Esa Heikkinen
DATE:       24.4.2018
DOCUMENT:   -
VERSION:    "$Id$"
REFERENCES: -
PURPOSE:	Sorts csv-file by timestamp (first) column order
			Need: pip3 install csvsort
CHANGES:    "$Log$"
###############################################################################
"""

import argparse
import sys
import time
from csvsort import csvsort

g_version = "$Id$"

#******************************************************************************
#
#	FUNCTION:	main
#
#******************************************************************************
def main():

	print("version: %s" % g_version)
	print("Python sys: %s\n" % sys.version)

	start_time = time.time()

	parser = argparse.ArgumentParser()
	parser.add_argument('-input_file','--input_file', dest='input_file', help='input_file')
	parser.add_argument('-output_file','--output_file', dest='output_file', help='output_file')
	args = parser.parse_args()

	print("input_file  : %s " % args.input_file)
	print("output_file : %s " % args.output_file)

	# Sorts (by first timestamp column) input csv-file and writes results to output csv-file
	csvsort(args.input_file, [0], args.output_file)

	print("\n Total execution time: %.3f seconds" % (time.time() - start_time))

if __name__ == '__main__':
    main()
