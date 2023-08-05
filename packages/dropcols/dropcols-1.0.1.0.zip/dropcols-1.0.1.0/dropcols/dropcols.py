#!/usr/bin/python
#
# dropcols.py
#
# Purpose:
#	Filter a CSV file, dropping or keeping specific columns.
#
# Author:
#	Dreas Nielsen (RDN)
#
# Copyright and License:
#	Copyright (c) 2007,2011 R.Dreas Nielsen
#	This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#   The GNU General Public License is available at <http://www.gnu.org/licenses/>
#
# Notes:
#   1. The input file must have a single row of column headers.
#	2. The input file must be some sort of CSV file; the format is diagnosed
#		from the first line (column headers).  The output file is written
#		in the same format, but complete quoting of non-numeric values
#		is forced (instead of the default of minimum quoting).
#
# History:
#	 Date		 Comments
#	----------	----------------------------------
#	12/2/2007	Began.  RDN.
#	12/23/2007	Completed and modified to use functions from the rvect module.  RDN.
#	08/28/2011	Added the list_not, list_or, and list_matches functions to remove
#				the dependency on the rvect module.  RDN.
#	09/01/2011	Modified to write to stdout instead of to a named file.
#				Modified option parsing and error handling.  
#				Added ability to handle numeric ranges and comma-separated lists.
#				Added more complete and consistent error handling.  RDN.
#	09/02/2011	Testing, debugging, and revision of global exception reporting.  RDN.
#	10/05/2011	Removed forced quoting in csv dialect. v. 1.0.1.0.  RDN.
#=================================================================================

_version = "1.0.1.0"
_vdate = "2011-10-05"

# Standard modules
import sys
import os
import os.path
import csv
import re
import traceback

EXIT, NO_EXIT = True, False

class RvectorError(Exception):
	pass


class DropColsError(Exception):
	exc_errlist = []
	def __init__(self, exit, errmsg_list=None):
		if errmsg_list and len(errmsg_list)>0:
			DropColsError.exc_errlist.extend(errmsg_list)
		if exit:
			if len(DropColsError.exc_errlist) > 0:
				sys.stderr.write("Error(s) in %s:\n" % os.path.basename(sys.argv[0]))
				for err in DropColsError.exc_errlist:
					sys.stderr.write("  %s\n" % err)
			sys.exit(1)

def bad_option(errmsg_list, msg, option):
	errmsg_list.append("Bad option. %s (%s)." % (msg, option))


__HELPMSG = """Syntax:
	dropcols [options] <input_file>
Arguments:
   input file
      The name of the input file from which to read data. This must be a
      comma-separated-value (csv) text file.  The first line of the file
      must contain column names.
Options:
   -d <column_name_regex1> [column_name_regex2 [...]]
      Regular expression(s) to match column names to drop.
   -k <column_name1_regex1> [column_name_regex2 [...]]
      Regular expression(s) to match column names to keep.
   -s Show the names of the columns that will be kept.
   -h,--help
      Print this help and exit.
   -v,--version
      Print the version number and exit.
Notes:
   1. Column numbers can be used instead of (or as well as) regular expressions
      on the column names.  Ranges and comma-separated lists of column numbers
      can be used.  The first column is number 1.
   2. If only a 'drop' list is specified, all columns will be kept except those
      on the 'drop' list.  If only a 'keep' list is specified, all columns will
      be dropped except those on the 'keep' list.  If both lists are specified,
      the 'keep' specifications will apply only to (and may thereby undo) the
      columns dropped per the 'drop' list.
   3. Column order in the output file will be the same as in the input
      file, regardless of the order of items in the 'keep' list."""

def __apply(func, index, *lists):
	d = [ l[index] for l in lists ]
	return reduce(func, d)

def all_equal(list1):
	"""Return True if all elements of the list are equal, False otherwise."""
	if list1:
		for i in range(1, len(list1)):
			if list1[i] != list1[0]:
				return False
	return True

def check_minargs(min, *args):
	if len(args) < min:
		raise DropColsError(EXIT, ["Incorrect number of arguments to list function."])

def check_lengths(*lists):
	if lists:
		if not all_equal([len(a) for a in lists]):
			raise DropColsError(EXIT, ["Mismatched lengths in arguments to list function."])

def all_list_len(mincount, *lists):
	"""Return the length of the lists, after a check to ensure that there are at least 'mincount'
	lists provided, and that they are all of the same length."""
	check_minargs(mincount, *lists)
	check_lengths(*lists)
	return len(lists[0])

def list_not(list1):
	return [ not bool(v) for v in list1 ]

def list_or(*lists):
	return [ __apply(lambda a, b: bool(a) or bool(b), i, *lists) for i in range(all_list_len(2, *lists)) ]

def list_matches(regex, list1):
	"""Return a list of booleans indicating whether the regex matches each element 
	of the list.  Note that this uses re.search() rather than re.match(), so the 
	regular expression need not match at the beginning of the list elements."""
	return [ regex.search(elem) != None for elem in list1 ]

def expandrange(range_expr):
	"""Return a list of integers corresponding to the range represented
	by the argument, which should be a string of the form 'nn-mm'."""
	nx = re.compile('\d+')
	lims = re.findall(nx, range_expr)
	rng = [ int(e) for e in lims ]
	rng.sort()
	if rng[0] > 0 and rng[1] > 0:
		return range(rng[0], rng[1]+1)
	else:
		return []

def numlist(numexprs):
	"""Return a list of integers corresponding to a list of strings
	representing either individual integers or integer ranges."""
	rngx = re.compile('^\d+-\d+$')
	nums = []
	for expr in numexprs:
		if rngx.match(expr):
			nums.extend(expandrange(expr))
		else:
			nums.append(int(expr))
	return list(set(nums))

def drop_columns(infilename, drop=None, keep=None, show_hdrs=False):
	"""Filter the input (csv) file to produce the output file, dropping and keeping
	columns as specified.
	Arguments 'drop' and 'keep' are lists of regular expression strings.  The 'drop'
	list is processed first, and can be overridden by the 'keep' list, so if a column
	matches a regular expression in both lists, it will be kept."""
	dialect = csv.Sniffer().sniff(open(infilename, "rt").readline())
	dialect.doublequote = True
	inf = csv.reader(open(infilename, "rt"), dialect)
	colnames = inf.next()
	# regex to match list and range of numeric values
	numxrx = re.compile('^(\d+)((-\d+)|(,\d+)+)*$')
	# regex to match a single numeric value or a range
	rngx = re.compile('\d+(?:-\d+)?')
	keepbools = [ True ] * len(colnames)
	if drop:
		# Create list of numeric expressions, to be converted to a list of column
		# numbers
		nexprs = [ expr for expr in drop if numxrx.match(expr) ]
		# Create list of digit and range expressions
		numstrings = []
		for expr in nexprs:
			numstrings.extend(re.findall(rngx, expr))
		# Convert the list of expressions to a list of integer column numbers
		dint = numlist(numstrings)
		# Create list of non-numeric expressions (to be used as regex patterns)
		dx = [ col for col in drop if not numxrx.match(col) ]
		dropx = [ re.compile(s) for s in dx ]
		dropbools = list_not(keepbools)
		for rx in dropx:
			dropbools = list_or(dropbools, list_matches(rx, colnames) )
		for i in dint:
			if i <= len(colnames):
				dropbools[i-1] = True
		keepbools = list_not(dropbools)
	if keep:
		if not drop:
			keepbools = list_not(keepbools)
		nexprs = [ expr for expr in keep if numxrx.match(expr) ]
		# Create list of digit and range expressions
		numstrings = []
		for expr in nexprs:
			numstrings.extend(re.findall(rngx, expr))
		# Convert the list of expressions to a list of integer column numbers
		kint = numlist(numstrings)
		# Create list of non-numeric expressions (to be used as regex patterns)
		kx = [ col for col in keep if not numxrx.match(col) ]
		keepx = [ re.compile(s) for s in kx ]
		for rx in keepx:
			keepbools = list_or(keepbools, list_matches(rx, colnames) )
		for i in kint:
			if i <= len(colnames):
				keepbools[i-1] = True
	keepindices = [ i for i in range(len(keepbools)) if keepbools[i] ]
	outf = csv.writer(sys.stdout, dialect)
	outf.writerow( [ colnames[x] for x in keepindices ] )
	if not show_hdrs:
		for row in inf:
			outf.writerow( [ row[x] for x in keepindices ] )

def print_help():
	print "%s -- Filter columns." % (os.path.basename(sys.argv[0]))
	print __HELPMSG

def print_version():
	print "%s %s %s" % ((os.path.basename(sys.argv[0])), _version, _vdate) 
	print "Copyright (c) 2011, R.Dreas Nielsen"
	print "License: Gnu General Public License v.3"
	
def get_opts(args):
	"""Return a dictionary of command-line options and a list of
	command-line arguments.  Each entry in the option dictionary
	consists of a list of option items.  Options -k and -d may have
	multiple option items.  The last command-line argument is treated
	as an argument, not an item to any option."""
	# states
	ready, optmult, optmultplus, arg = 1, 2, 3, 4
	validopts = { '-d': optmult, '-k': optmult, '-h': ready, '-s': ready }
	state = ready
	optdict = {}
	arglist = []
	nargs = len(args)
	argno = 0
	curropt = None
	errlist = []
	for arg in args:
		argno += 1
		if len(arg) > 0:
			if arg[0] == '-':			# Option
				if arg in ('-h', '--help', '--hel', '--he', '--h'):
					print_help()
					sys.exit(0)
				if arg in ('-v', '--version', '--versio', '--versi', '--vers', '--ver', '--ve'):
					print_version()
					sys.exit(0)
				if argno == nargs:
					bad_option(errlist, "The last argument should be a filename, not an option", arg)
				if state == optmult:	# expecting an option item
					bad_option(errlist, "Expected an item for option %s" % curropt, arg)
					continue
				if len(arg)==1:
					bad_option(errlist, "Option letter missing", arg)
					continue
				opt = arg[:2]
				if not opt in validopts:
					bad_option(errlist, "Unrecognized", arg)
					continue
				if not opt in optdict:
					optdict[opt] = []
				curropt = opt
				state = validopts[opt]
				if len(arg) > 2:
					if state == optmult:
						optdict[opt].append(arg[2:])
						state = optmultplus
					else:
						bad_option(errlist, "Option item found but not allowed", arg)
						continue
			else:					# Non-option
				if state==ready or (state==optmultplus and argno==nargs):
					arglist.append(arg)
					state = ready
				elif (state==optmult or state==optmultplus) and argno < nargs:
					optdict[curropt].append(arg)
					state = optmultplus
				else:
					bad_option(errlist, "Unexpected argument", arg)
					continue
	if len(errlist) > 0:
		raise DropColsError(NO_EXIT, errlist)
	if len(optdict) == 0 and len(arglist) == 0:
		print_help()
		sys.exit(0)
	if len(arglist) == 0:
		bad_option(errlist, "No input filename specified.", "")
	if len(arglist) > 1:
		bad_option(errlist, "More than one argument provided.", " ".join(arglist))
	infilename = arglist[-1:][0]
	if not os.path.exists(infilename):
		bad_option(errlist, "Input file does not exist.", infilename)
	if len(errlist) > 0:
		raise DropColsError(NO_EXIT, errlist)
	return optdict, arglist


def main():
	try:
		opts, args = get_opts(sys.argv[1:])
	except DropColsError:
		raise DropColsError(EXIT)
	drop_rxs = None
	if opts.has_key('-d'):
		drop_rxs = opts['-d']
	keep_rxs = None
	if opts.has_key('-k'):
		keep_rxs = opts['-k']
	infilename = args[-1:][0]
	drop_columns(infilename, drop_rxs, keep_rxs, opts.has_key('-s'))

if __name__=='__main__':
	try:
		main()
	except DropColsError:
		raise DropColsError(EXIT)
	except SystemExit:
		pass
	except Exception as oops:
		strace = traceback.extract_tb(sys.exc_info()[2])[-1:]
		lno = strace[0][1]
		src = strace[0][3]
		raise DropColsError(EXIT, ["%s: Uncaught exception %s (%s) on line %s (%s)." % (os.path.basename(sys.argv[0]), str(sys.exc_info()[0]), sys.exc_info()[1], lno, src)])

