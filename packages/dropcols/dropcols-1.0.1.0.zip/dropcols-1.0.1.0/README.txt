dropcols.py
Filter columns from a CSV file.

dropcols.py is a Python module and program that removes (or conversely, extracts) 
selected columns from a delimited text file, such as a CSV file. It is analogous 
to the *nix "cut" program, except that it works on CSV files and allows columns 
to be selected by name (regular expressions) in addition to by number. Either the 
columns to keep, or the columns to remove, or both, can be specified.


Syntax and Options
==================

dropcols.py [options] <input_file> 

Arguments
---------

   input file
      The name of the input file from which to read data. This must be a
      comma-separated-value (csv) text file.  The first line of the file
      must contain column names.
	  
Options
-------

   -d <column_name_regex1> [column_name_regex2 [...]]
      Regular expression(s) to match column names to drop.
   -k <column_name1_regex1> [column_name_regex2 [...]]
      Regular expression(s) to match column names to keep.
   -s Show the names of the columns that will be kept.
   -h,--help
      Print this help and exit.
   -v,--version
      Print the version number and exit.


Usage Notes
===========

  *  The first line of the file should contain the names of the columns.

  *  Output is written to stdout.

  *  Column numbers can be used instead of (or as well as) regular expressions on 
     the column names. Ranges and comma-separated lists of column numbers can be used. 
	 The first column is number 1.

  *  If only a 'drop' list is specified, all columns will be kept except those on the 
     'drop' list. If only a 'keep' list is specified, all columns will be dropped except 
	 those on the 'keep' list. If both lists are specified, the 'keep' specifications will 
	 apply only to (and may thereby undo) the columns dropped per the 'drop' list.

  *  Column order in the output file will be the same as in the input file, regardless of 
     the order of items in the 'drop' and 'keep' lists.

  *  The -s option allows verification that the correct columns will be selected without 
     requiring processing of the entire input file.
