import pickle
import compress_files
def put_into_store(file_list):
     athelete_globe={}
     for each_file in file_list:
          athelete = compress_files.get_custom_data('each_file')
          athelete_globe[athelete.name]=athelete
     try:
          with open('athelete_base.pickle','wb') as ath:
               pickle.dump(athelete_globe,ath)
     except IOError as err:
          print('file_error(put_into_store)'+"  "+str(err))
     return(athelete_globe)

def get_from_store():
     athelete_globe={}
     try:
          with open('../../athelete_base.pickle','rb') as ath:
               athelete_globe=pickle.load(ath)
     except IOError as err:
          print('file_error(get_from_store)'+"  "+str(err))
     return(athelete_globe)
