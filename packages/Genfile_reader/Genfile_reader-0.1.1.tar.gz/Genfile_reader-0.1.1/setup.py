from distutils.core import setup

setup(
	name		='Genfile_reader',
	version		='0.1.1',
	author		='rihen',
	author_email	='rihen234@gmail.com',
	packages		=['simple_file_reader','simple_file_reader.test','input_reader','file_compressor','data_decoder'],
	url		='http://pypi.python.org/pypi/Genfile_reader/',
	license		=open('docs/LICENSE.txt').read(),
	description	='helps to read a file',
	long_description	=open('docs/README.txt').read(),
     )
	
