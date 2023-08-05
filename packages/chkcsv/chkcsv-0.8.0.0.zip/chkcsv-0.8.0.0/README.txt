chkcsv.py.py

chkcsv.py is a Python module and program that checks the format and content 
of a comma-separated-value (CSV) or similar delimited text file. It can check 
whether required columns are present, and the type, length, and pattern of 
each column.


Syntax and Options
===================

	chkcsv.py [options] <CSV file name> 

Arguments
----------
	<CSV file name> The name of the CSV file to check. 

Options
-------
	--version	Show program's version number and exit 
	-h, --help	Show this help message and exit 
	-s, --showspecs 
				Show the format specifications allowed in the 
				configuration file, and exit. 
	-f FORMATSPEC, --formatspec=FORMATSPEC 
				Name of the file with the format specification. The default 
				is the name of the CSV file with an extension of fmt. 
	-r, --required 
				A data value is required in data columns for which the format 
				specification does not include an explicit specification of 
				whether data is required for a column. The default is false 
				(i.e., data are not required). 
	-q, --columnsnotrequired 
				Columns listed in the format configuration file are not 
				required to be present unless the column_required 
				specification is explicitly set in the configuration file. 
				The default is true (i.e., all columns in the configuration 
				file are required in the CSV file). 
	-c, --columnexit 
				Exit immediately if there are more columns in the CSV file 
				header than are specified in the format configuration file. 
	-l, --linelength 
				Allow rows of the CSV file to have fewer columns than in the 
				column headers. The default is to report an error for short 
				data rows. If short data rows are allowed, any row without 
				enough columns to match the format specification will still 
				be reported as an error. 
	-i, --case-insensitive 
				Case-insensitive matching of column names in the format 
				configuration file and the CSV file. The default is 
				case-sensitive (i.e., column names must match exactly). 
	-e ENCODING, --encoding=ENCODING 
				Character encoding of the CSV file. It should be one of the 
				strings listed at 
				http://docs.python.org/library/codecs.html#standard-encodings. 
	-o OPTSECTION, --optsection=OPTSECTION 
				An alternate name for the chkcsv options section in the 
				format specification configuration file. 
	-x, --exitonerror 
				Exit when the first error is found.


Format Specifications
=====================

The format of each of the columns of the CSV file is specified in a separate 
configuration file containing a section for each column. Each section begins 
with the column name in square brackets, followed by key-value pairs 
identifying the specifications for that column. Each key-value pair consists 
of a keyword and an associated value. Keywords and values should be separated 
by either "=" or ":". Each keyword should be at the beginning of a line.

By default, the configuration file has the same name as the CSV file, but 
with an extension of ".fmt". An alternate configuration file can be specified 
with the "-f" command-line option.

The keywords that can be used for column format specifications are listed below. 
A specific type of value should be provided for each keyword. Boolean values 
are indicated by "Yes", "No", "True", "False", "On", "Off", "1", or "0". Format 
specification keywords and values should not be quoted in the configuration 
file. The allowable keywords are:

column_required
    Indicates whether or not the column must be present in the CSV file. 
	This is a Boolean value. The default value is True, and can be changed 
	with the "-q" command-line option. This format option need be included 
	in the format configuration file only when the default is to be overridden.

data_required
    Indicates whether or not a value is required in this column on every row 
	of the CSV file. This is a Boolean value. The default value is False, 
	and can be changed with the "-r" command-line option. This format option 
	need be included in the format configuration file only when the default 
	is to be overridden.

type
    Identifies the type of data in the data column. Valid values are "string", 
	"integer", "float", "bool", "date", and "datetime". Data values in the 
	CSV file will be checked for compatibility with the specified type. If 
	the data type is not specified, data values will be treated as strings—
	that is, minimum and maximum lengths and the pattern will be checked 
	if they have been specified.

minlen
    The required minimum length of data values for this column. This is 
	only checked for string data types and for data with no type specified.

maxlen
    The maximum allowed length of data values for this column. This is only 
	checked for string data types and for data with no type specified.

pattern
    A regular expression specifying the content of the column value. 
	Patterns must match at the beginning of the column value. This is 
	checked for string, date, and datetime data types, and for data with 
	no type specified.


Usage Notes
===========

	*	The first line of the CSV file must contain the names of the columns.

	*	The order of column specifications in the configuration file does not 
		have to match the order of columns in the CSV file.

	*	Format specification keywords for a column may be in any order within 
		the column section in the configuration file

	*	Column names in the CSV file and in the configuration file are 
		case-sensitive, and must match exactly by default. If column names 
		in the configuration file and the CSV file don't match because the 
		case is different, an error will be reported only if the unmatched 
		column is required. The "-i" command-line option can be used to allow 
		case-insensitive matching of column names.

	*	The pattern that a column should match is specified by a regular 
		expression. The regular expression syntax supported by chkcsv.py is 
		as documented at http://docs.python.org/library/re.html.

	*	Patterns (regular expressions) must match at the beginning of the 
		column value. To ensure that the regular expression matches the 
		entire column value, you may need to include "$" at the end of the 
		regular expression.

	*	By default, all columns listed in the configuration file are 
		considered to be required, and if the column name is not present 
		in the CSV file (header row), this will be considered to be an error 
		and chkcsv.py will halt immediately. The default behavior can be 
		changed with the "-q" command-line option. If "-q" is used, or the 
		"column_required" format specification is set to False, and the 
		column is not present, no error will occur. If the column is present, 
		any other format specifications will be applied. That is, even if a 
		column is not required, if it is present and its data fails some other 
		test, an error will be reported.

	*	chkcsv.py recognizes a wide variety of date and datetime formats. 
		It may actually recognize a date or datetime format that the target 
		software (e.g., a DBMS) does not. In this case, specifying a pattern 
		for the date column can usefully restrict the types of date and 
		datetime values that are accepted.

	*	The CSV file is expected to have the same number of data items on 
		each row as there are column names in the first row of the file. 
		If the "-l" command-line option is used, the CSV file may have 
		varying numbers of data values in each row, as long as each row 
		has enough values to correspond to each data column that will be 
		checked. That is, if "-l" is used, and there are columns to the 
		right of all of the required columns, those data items may or may 
		not be present in any row without causing an error. However, if a 
		row is short because a value in a required column is missing, and 
		this omission does not cause any violation of any format 
		specification, this error will not necessarily be recognized.

	*	chkcsv.py does not transform the input file in any way. It does 
		not produce any output file or send any output to stdout except 
		for help and version messages. chkcsv.py only writes error messages, 
		if any, to stderr and sets the exit status value when it terminates.

	*	chkcsv.py is intended to verify that a data file is suitable for 
		import to database, statistical, graphics, modeling, or other 
		software. The checks that it can perform are generally sufficient 
		to determine whether each data column is compatible with typical 
		specifications for a database column. However, chkcsv.py does not 
		do any row-level checks to verify that column values within a row 
		are consistent with each other. Nor does it do any dataset-level 
		checks to ensure, for example, that each row is unique.

	*	chkcsv.py includes a provision to allow additional options to be 
		specified in a special section of the configuration file. By default, 
		the name of this special section is "chkcsvoptions". A different 
		name for this special section can be specified with the "-o" 
		command-line argument. Currently there are no special options 
		supported, and if this special section is present in the 
		configuration file, it will be ignored.

