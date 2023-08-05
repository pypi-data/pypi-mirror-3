from distutils.core import setup

setup(name='chkcsv',
	version='0.8.0.0',
	description="Check the format of a CSV file",
	author='Dreas Nielsen',
	author_email='dreas.nielsen@gmail.com',
    url='none',
	scripts=['chkcsv/chkcsv.py'],
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
	long_description="""``chkcsv.py`` is a Python module and program 
that checks the format of data in a CSV file.  It can check whether required
columns and data are present, and the type of data in each column.  Pattern
matching using regular expressions is supported."""
	)
