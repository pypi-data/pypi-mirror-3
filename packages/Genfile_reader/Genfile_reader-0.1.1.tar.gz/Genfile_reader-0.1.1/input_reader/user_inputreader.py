def input_reader(io_num,input_msg):
	input_data_list=[]
	try:
		for each_num in range(io_num):
			input_data_list.append(input(input_msg))
		return input_data_list
	except IOError as err:
		print(str(err))	
