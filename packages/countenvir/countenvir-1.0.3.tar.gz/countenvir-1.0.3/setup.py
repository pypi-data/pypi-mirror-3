from distutils.core import setup

setup(
	name		= 'countenvir',
	version		= '1.0.3',
	py_modules	= ['countenvir'],
	author		= 'Jochen Demmer',
	author_email	= 'info@csdemmer.de',
	url		= 'http://www.csdemmer.de',
	license		= 'GPLv3',
	description	= 'A simple environment to count the occurrences of the 26 latin letters',
	description_long= 'The script needs two parameters: The first is the txt file to read from, the second on is the output file which will be csv format.'
)
