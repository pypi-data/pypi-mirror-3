import os

def read_file(file_str):
	print('code running...')
	get_path=file_str
	try:
		print('looking for the file....')
		data=open(get_path)
		print('file found in...',os.getcwd())
		try:
			file_name=get_path.split('/')
			get_file_name=file_name[len(file_name)-1]
			print('reading data from the file ',end='')
			print(get_file_name)
			for each_line in data:
				return(each_line)
		except:
			print('unable to processs file further')
	except IOError as err_obj:
		print('file error'+str(err_obj))
	finally:
		if 'data' in locals():
			data.close()
def practice_code(file_name):
	try:
		with open(file_name,"w+") as plain_doc:
			print('current file opens in r/w mode')
			write_bool=True
			while write_bool:
				input_data=input('start editing or writing to this file')
				print(input_data,file=plain_doc)
				get_mode_control=input('press y/n to quit editing the document')
				if get_mode_control=='y':
					write_bool=False
			print('save complete....')
	except IOError as eee:
		print(str(eee))
