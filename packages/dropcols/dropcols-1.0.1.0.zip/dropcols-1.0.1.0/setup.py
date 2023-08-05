from distutils.core import setup

setup(name='dropcols',
	version='1.0.1.0',
	description="Filter a CSV file, extracting columns selected by name or position.",
	author='Dreas Nielsen',
	author_email='dreas.nielsen@gmail.com',
    url='none',
	scripts=['dropcols/dropcols.py'],
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Environment :: Console',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Topic :: Text Processing :: General',
		'Topic :: Office/Business'
		],
	long_description="""``dropcols.py`` is a Python module and program 
that removes (or conversely, extracts) 
selected columns from a delimited text file, such as a CSV file. It is analogous 
to the *nix "cut" program, except that it works on CSV files and allows columns 
to be selected by name (regular expressions) in addition to by number. Either the 
columns to keep, or the columns to remove, or both, can be specified.
"""
	)
