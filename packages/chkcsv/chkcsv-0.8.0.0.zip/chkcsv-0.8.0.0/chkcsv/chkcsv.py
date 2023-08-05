#! /usr/bin/python
# chkcsv.py
#
# PURPOSE:
#	Check the contents of a CSV file, specifically that columns match a
#	specified format.
#
# NOTES:
#	1. Column format specifications are stored in a configuration file
#		with an INI-file format, where bracketed sections correspond to
#		columns and each section contains key-value pairs of format specifications.
#	2. Recognized column specifications are:
#		column_required=1|Yes|True|On|0|No|False|Off
#		data_required=1|Yes|True|On|0|No|False|Off
#		minlen=<integer>
#		maxlen=<integer>
#		type=integer|float|string|date|datetime|bool
#		pattern=<regular expression identifying valid values>
#	3. Global options in the format specification file are not yet implemented,
#		though a section name for them is reserved.
#
# COPYRIGHT:
#	Copyright (c) 2011, R.Dreas Nielsen (RDN)
#
# LICENSE:
#	GPL v.3
#	This program is free software: you can redistribute it and/or
#	modify it under the terms of the GNU General Public License as published
#	by the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version. This program is distributed in the
#	hope that it will be useful, but WITHOUT ANY WARRANTY; without even
#	the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#	PURPOSE. See the GNU General Public License for more details. The GNU
#	General Public License is available at http://www.gnu.org/licenses/.
#
# HISTORY:
#	 Date		 Remarks
#	----------	--------------------------------------------------------------
#	2011-09-25	First version.  Version 0.8.0.0.  RDN.
# ============================================================================

_version = "0.8.0.0"
_vdate = "2011-09-24"

import sys
from optparse import OptionParser
import ConfigParser
import codecs
import os.path
import csv
import re
import datetime
import types
import traceback

FORMATSPECS = """Format specification options:
    column_required=1|Yes|True|On|0|No|False|Off
    type=integer|float|string|date|datetime|bool
    data_required=1|Yes|True|On|0|No|False|Off
    minlen=<integer>
    maxlen=<integer>
    pattern=<regular expression identifying valid values>
"""

class ChkCsvError(Exception):
	"""Base class for chkcsv errors."""
	def __init__(self, errmsg, infile=None, line=None, column=None):
		self.errmsg = errmsg
		self.infile = infile
		self.line = line
		self.column = column

class CsvChecker():
	"""Object to check a specific column of a defined type.  After initialization, the 'check()'
	method will return a boolean indicating whether a data value is acceptable."""
	get_fn = {
			'column_required' : ConfigParser.SafeConfigParser.getboolean,
			'data_required' : ConfigParser.SafeConfigParser.getboolean,
			'type' : ConfigParser.SafeConfigParser.get,
			'minlen' : ConfigParser.SafeConfigParser.getint,
			'maxlen' : ConfigParser.SafeConfigParser.getint,
			'pattern' : ConfigParser.SafeConfigParser.get
			}
	datetime_fmts = ("%x",
				"%c",
				"%x %X",
				"%m/%d/%Y",
				"%m/%d/%y",
				"%m/%d/%Y %H%M",
				"%m/%d/%Y %I:%M %p",
				"%m/%d/%y %H%M",
				"%m/%d/%y %I:%M %p",
				"%Y-%m-%d %H%M",
				"%Y-%m-%d %I:%M %p",
				"%Y-%m-%d",
				"%Y/%m/%d %H%M",
				"%Y/%m/%d %I:%M %p",
				"%Y/%m/%d %X",
				"%Y/%m/%d",
				"%b %d, %Y",
				"%b %d, %Y %X",
				"%b %d, %Y %I:%M %p",
				"%b %d %Y",
				"%b %d %Y %X",
				"%b %d %Y %I:%M %p",
				"%d %b, %Y",
				"%d %b, %Y %X",
				"%d %b, %Y %I:%M %p",
				"%d %b %Y",
				"%d %b %Y %X",
				"%d %b %Y %I:%M %p",
				"%b. %d, %Y",
				"%b. %d, %Y %X",
				"%b. %d, %Y %I:%M %p",
				"%b. %d %Y",
				"%b. %d %Y %X",
				"%b. %d %Y %I:%M %p",
				"%d %b., %Y",
				"%d %b., %Y %X",
				"%d %b., %Y %I:%M %p",
				"%d %b. %Y",
				"%d %b. %Y %X",
				"%d %b. %Y %I:%M %p",
				"%Y",
				"%b %Y",
				"%b, %Y",
				"%b. %Y",
				"%b., %Y",
				"%b-%Y",
				"%b.-%Y",
				"%B %d, %Y",
				"%B %d, %Y %X",
				"%B %d, %Y %I:%M %p",
				"%B %d %Y",
				"%B %d %Y %X",
				"%B %d %Y %I:%M %p",
				"%d %B, %Y",
				"%d %B, %Y %X",
				"%d %B, %Y %I:%M %p",
				"%d %B %Y",
				"%d %B %Y %X",
				"%d %B %Y %I:%M %p",
				"%B %Y",
				"%B, %Y",
				"%B-%Y",
				)
	date_fmts = ("%x",
				"%c",
				"%x %X",
				"%m/%d/%Y",
				"%m/%d/%y",
				"%Y-%m-%d",
				"%Y/%m/%d",
				"%b %d, %Y",
				"%b %d %Y",
				"%d %b, %Y",
				"%d %b %Y",
				"%b. %d, %Y",
				"%b. %d %Y",
				"%d %b., %Y",
				"%d %b. %Y",
				"%Y",
				"%b %Y",
				"%b, %Y",
				"%b. %Y",
				"%b., %Y",
				"%b-%Y",
				"%b.-%Y",
				"%B %d, %Y",
				"%B %d %Y",
				"%d %B, %Y",
				"%d %B %Y",
				"%B %Y",
				"%B, %Y",
				"%B-%Y",
				)
	# Basic format checking functions.  These return None if the data are acceptable,
	# a textual description of the problem otherwise.
	def chk_req(self, data):
		return "missing data" if len(data)==0 else None
	def chk_min(self, data):
		return None if (not self.data_required and len(data)==0) or \
			len(data) >= self.minlen else "data too short"
	def chk_max(self, data):
		return None if len(data) <= self.maxlen else "data too long"
	def chk_pat(self, data):
		return None if len(data)==0 or self.rx.match(data) else "pattern mismatch"
	def chk_int(self, data):
		if len(data)==0:
			return None
		try:
			x = int(data)
			return None
		except ValueError:
			return "not an integer"
	def chk_float(self, data):
		if len(data)==0:
			return None
		try:
			x = float(data)
			return None
		except ValueError:
			return "not a floating-point number"
	def chk_bool(self, data):
		if len(data)==0:
			return None
		return None if data in ('True', 'true', 'TRUE', 'T', 't', 'Yes', 'yes', 'YES', 'Y', 'y',
				'False', 'false', 'FALSE', 'F', 'f', 
				'No', 'no', 'NO', 'N', 'n', True, False) else "unrecognized boolean"
	def chk_datetime(self, data):
		if len(data)==0:
			return None
		if type(data) == type(datetime.datetime.now()):
			return None
		if type(data) == type(datetime.date.today()):
			return None
		if type(data) != types.StringType:
			if data==None:
				return "missing date/time"
			try:
				data = str(data)
			except ValueError:
				return "can't convert data to string for date/time test"
		for f in self.datetime_fmts:
			try:
				dt = datetime.datetime.strptime(data, f)
			except:
				continue
			break
		else:
			return "invalid date/time"
		return None
	def chk_date(self, data):
		if len(data)==0:
			return None
		if type(data) == type(datetime.date.today()):
			return None
		if type(data) != types.StringType:
			if data==None:
				return "missing date"
			try:
				data = str(data)
			except ValueError:
				return "can't convert data to string for date test"
		for f in self.date_fmts:
			try:
				dt = datetime.datetime.strptime(data, f)
			except:
				continue
			break
		else:
			return "invalid date"
		return None
	def dispatch(self, check_funcs, data):
		errlist = [ f(data) for f in check_funcs ]
		return [ e for e in errlist if e ]
	def __init__(self, fmt_spec, colname, column_required_default, data_required_default):
		self.name = colname
		self.data_required = data_required_default
		# By default, all columns are required unless there is a specification indicating that it is not.
		self.column_required = column_required_default
		specs = fmt_spec.options(colname)
		# Get the value for each option, using an appropriate function for each expected value type.
		for spec in specs:
			try:
				specval = self.get_fn[spec](fmt_spec, colname, spec)
			except KeyError:
				raise ChkCsvError('Unrecognized format specification (%s)' % spec, column=colname)
			setattr(self, spec,	specval)
		# Convert any pattern attribute to an rx attribute
		if hasattr(self, 'pattern'):
			try:
				self.rx = re.compile(self.pattern)
			except:
				raise ChkCsvError("Invalid regular expression pattern: %s" % self.pattern, column=colname)
		# Create the check method
		errfuncs = []
		if self.data_required:
			errfuncs.append(self.chk_req)
		if hasattr(self, 'type'):
			if self.type == 'string':
				if hasattr(self, 'minlen'):
					errfuncs.append(self.chk_min)
				if hasattr(self, 'maxlen'):
					errfuncs.append(self.chk_max)
				if hasattr(self, 'pattern'):
					errfuncs.append(self.chk_pat)
			elif self.type == 'integer':
				errfuncs.append(self.chk_int)
			elif self.type == 'float':
				errfuncs.append(self.chk_float)
			elif self.type == 'date':
				errfuncs.append(self.chk_date)
				if hasattr(self, 'pattern'):
					errfuncs.append(self.chk_pat)
			elif self.type == 'datetime':
				errfuncs.append(self.chk_datetime)
				if hasattr(self, 'pattern'):
					errfuncs.append(self.chk_pat)
		else:
			if hasattr(self, 'minlen'):
				errfuncs.append(self.chk_min)
			if hasattr(self, 'maxlen'):
				errfuncs.append(self.chk_max)
			if hasattr(self, 'pattern'):
				errfuncs.append(self.chk_pat)
		self.check = lambda data: self.dispatch(errfuncs, data)


def clparser():
	usage_msg = """Usage: %prog [options] <CSV file name>
Arguments:
  CSV file name   The name of a comma-separated-values file to check."""
	vers_msg = "%prog " + "%s %s" % (_version, _vdate)
	desc_msg = "Checks the content and format of a CSV file."
	parser = OptionParser(usage=usage_msg, version=vers_msg, description=desc_msg)
	parser.add_option("-s", "--showspecs", action="store_true", dest="showspecs",
						default=False,
						help="Show the format specifications allowed in the configuration file, and exit.")
	parser.add_option("-f", "--formatspec",
						action="store", dest="formatspec",
						type="string",
						help="Name of the file with the format specification.  The default is the name of the CSV file with an extension of fmt.")
	parser.add_option("-r", "--required", action="store_true", dest="data_required",
						default=False,
						help="A data value is required in data columns for which the format specification does not include an explicit specification of whether data is required for a column.  The default is false (i.e., data are not required).")
	parser.add_option("-q", "--columnsnotrequired", action="store_false", dest="column_required",
						default=True,
						help="Columns listed in the format configuration file are not required to be present unless the column_required specification is explicitly set in the configuration file.  The default is true (i.e., all columns in the configuration file are required in the CSV file).")
	parser.add_option("-c", "--columnexit", action="store_true", dest="columnexit",
						default=False,
						help="Exit immediately if there are more columns in the CSV file header than are specified in the format configuration file.")
	parser.add_option("-l", "--linelength", action="store_false", dest="linelength",
						default=True,
						help="Allow rows of the CSV file to have fewer columns than in the column headers.  The default is to report an error for short data rows.  If short data rows are allowed, any row without enough columns to match the format specification will still be reported as an error.")
	parser.add_option("-i", "--case-insensitive", action="store_true", dest="caseinsensitive",
						default=False,
						help="Case-insensitive matching of column names in the format configuration file and the CSV file.  The default is case-sensitive (i.e., column names must match exactly).")
	parser.add_option("-e", "--encoding", action="store", type="string", dest="encoding",
						default=None,
						help="Character encoding of the CSV file.  It should be one of the strings listed at http://docs.python.org/library/codecs.html#standard-encodings.")
	parser.add_option("-o", "--optsection", action="store", dest="optsection",
						type="string",
						help="An alternate name for the chkcsv options section in the format specification configuration file.")
	parser.add_option("-x", "--exitonerror",
						action="store_true", dest="haltonerror",
						default=False,
						help="Exit when the first error is found.")
	return parser

class UTF8Recoder:
	"""Iterator that reads an encoded stream and reencodes the input to UTF-8."""
	def __init__(self, f, encoding):
		self.reader = codecs.getreader(encoding)(f)
	def __iter__(self):
		return self
	def next(self):
		return self.reader.next().encode('utf-8')

class UnicodeReader:
	"""A CSV reader which will iterate over lines in the CSV file "f",
	which is encoded in the given encoding."""
	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		f = UTF8Recoder(f, encoding)
		self.reader = csv.reader(f, dialect=dialect, **kwds)
	def next(self):
		row = self.reader.next()
		return [unicode(s, "utf-8") for s in row]
	def __iter__(self):
		return self

def show_errors(errlist):
	"""Items in errlist are a tuple of a narrative message, the name of the file
	in which the error occurred, the line number of the file, and the column
	name of the file.  All but the first may be null."""
	for err in errlist:
		sys.stderr.write("%s.\n" % " ".join([ "%s %s" % em for em in [ e for e in 
			zip(("Error:", "in file", "on line", "in column"), err) if e[1]]]))
	

def check_csv_file(csv_fname, cols, halt_on_err, columnexit, \
		linelength, caseinsensitive, encoding=None):
	"""Check that all of the required columns and data are present in the CSV file, and that
	the data conform to the appropriate type and other specification.
	Arguments are: 1. The name of the CSV file to check; 2. A dictionary of
	specifications (ChkCsv objects) indexed by column name; 3. Whether to exit
	on the first error; 4. Whether to exit if the CSV file doesn't have
	exactly the same columns in the format specifications; 5. Whether to
	report an error if any data row has a different number of items than indicated
	by the column headers; 6. Whether column names in the specifications and
	CSV file should be compared case-insensitive; 7. The character encoding of
	the CSV file.
	"""
	dialect = csv.Sniffer().sniff(open(csv_fname, "rt").readline())
	if encoding:
		inf = UnicodeReader(open(csv_fname, "rt"), dialect, encoding)
	else:
		inf = csv.reader(open(csv_fname, "rt"), dialect)
	colnames = inf.next()
	req_cols = [ c for c in cols if cols[c].column_required ]
	# Exit if all required columns are not present
	if caseinsensitive:
		colnames_l = [ c.lower() for c in colnames ]
		req_missing = [ col for col in req_cols if not (col.lower() in colnames_l) ]
	else:
		req_missing = [ col for col in req_cols if not (col in colnames) ]
	if len(req_missing) > 0:
		raise ChkCsvError("The following columns are required, but are not present in the CSV file: %s." % ", ".join(req_missing), csv_fname, 1)
	# Exit if there are extra columns and the option to exit is set.
	if columnexit:
		if caseinsensitive:
			speccols_l = [ c.lower() for c in cols ]
			extra = [ col for col in colnames if not (col.lower() in speccols_l) ]
		else:
			extra = [ col for col in colnames if not (col in cols) ]
		if len(extra) > 0:
			raise ChkCsvError("The following columns have no format specifications but are in the CSV file: %s." % ", ".join(extra), csv_fname, 1)
	# Column names common to specifications and data file.  These will be used
	# to index the cols dictionary to get the appropriate check method
	# and to index the CSV column name list (colnames) to get the column position.
	if caseinsensitive:
		chkcols = {}
		for x in cols:
			for y in colnames:
				if x.lower() == y.lower():
					chkcols[x] = y
	else:
		datacols = [ col for col in cols if col in colnames ]
		chkcols = dict(zip(datacols, datacols))
	# Get maximum required column number (index) to check data rows
	dataindex = [ colnames.index(chkcols[col]) for col in chkcols ]
	maxindex = max(dataindex) if len(dataindex) > 0 else 0		# 0 if format file is empty
	colloc = dict(zip([ chkcols[c] for c in chkcols ], dataindex))
	# Read and check the CSV file until done (or until an error).
	errorlist = []
	row_no = 1	# Header is row 1.
	for datarow in inf:
		row_no += 1
		if (len(datarow) > 0) and (len(datarow) < len(colnames)) and linelength:
			errorlist.append(("fewer data values than column headers", csv_fname, row_no))
		if len(datarow) < maxindex + 1:
			if len(datarow) > 0:
				errorlist.append(("fewer data values than columns in the format specification", csv_fname, row_no))
				if halt_on_err:
					return errorlist
		else:
			for col in chkcols:
				col_errs = cols[col].check(datarow[colloc[chkcols[col]]])
				if len(col_errs) > 0:
					errorlist.extend([ (e, csv_fname, row_no, cols[col].name) for e in col_errs ])
					if halt_on_err:
						return errorlist
	return errorlist


def main():
	parser = clparser()
	(opts, args) = parser.parse_args()
	if opts.showspecs:
		print(FORMATSPECS)
		return 0
	if len(args)==0:
		parser.print_help()
		return 0
	if len(args) <> 1:
		raise ChkCsvError("A single argument, the name of the CSV file to check, must be provided.")
	csv_file = args[0]
	if not os.path.exists(csv_file):
		raise ChkCsvError("The specified CSV file does not exist.", csv_file)
	if opts.formatspec:
		fmt_file = opts.formatspec
	else:
		(fn, ext) = os.path.splitext(csv_file)
		fmt_file = "%s.fmt" % fn
	if not os.path.exists(fmt_file):
		raise ChkCsvError("The format file does not exist.", fmt_file)
	fmtspecs = ConfigParser.SafeConfigParser()
	try:
		files_read = fmtspecs.read([fmt_file])
	except ConfigParser.Error:
		raise ChkCsvError("Error reading format specification file.", fmt_file)
	if len(files_read) == 0:
		raise ChkCsvError("Error reading format specification file.", fmt_file)
	if opts.optsection:
		chkopts = opts.optsection
	else:
		chkopts = "chkcsvoptions"
	# Convert ConfigParser object into a list of CsvChecker objects
	speccols = [ sect for sect in fmtspecs.sections() if sect <> chkopts ]
	cols = {}
	for col in speccols:
		cols[col] = CsvChecker(fmtspecs, col, opts.column_required, opts.data_required)
	# Check the file
	errorlist = check_csv_file(csv_file, cols, opts.haltonerror, 
		opts.columnexit, opts.linelength, opts.caseinsensitive, opts.encoding)
	if len(errorlist) > 0:
		show_errors(errorlist)
		return 1
	else:
		return 0


if __name__=='__main__':
	try:
		status = main()
	except ChkCsvError, msg:
		show_errors( [ (msg.errmsg, msg.infile, msg.line, msg.column) ] )
		exit(1)
	except SystemExit, x:
		sys.exit(x)
	except Exception:
		strace = traceback.extract_tb(sys.exc_info()[2])[-1:]
		lno = strace[0][1]
		src = strace[0][3]
		sys.stderr.write("%s: Uncaught exception %s (%s) on line %s (%s)." % (os.path.basename(sys.argv[0]), str(sys.exc_info()[0]), sys.exc_info()[1], lno, src))
		sys.exit(1)
	sys.exit(status)

