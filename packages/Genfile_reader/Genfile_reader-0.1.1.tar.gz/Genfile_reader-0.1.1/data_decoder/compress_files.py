def get_custom_data(file_name):
	try:
		with open(file_name) as record:
			temp_hold=record.readline()
			list_gen=temp_hold.strip().split(',')
			return(Athelete_list(list_gen.pop(0),list_gen.pop(0),list_gen))
	except IOError as err:
		print(str(err))

def sanitize(time_format):
	if '-'  in time_format:
		splitter='-'
	elif ':' in time_format:
		splitter=':'
	else:
		return(time_format)
	(minutes,secs)=time_format.split(splitter)
	return(minutes+'.'+secs)

class Athelete_list(list):
	def __init__(self,a_name,a_dob=None,a_lap_time=[]):
		self.name=a_name
		self.dob=a_dob
		self.extend(a_lap_time)
	def top3ranks(self):
		return(sorted(set(sanitize(t) for t in self))[0:3])
