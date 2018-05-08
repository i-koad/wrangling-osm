#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
#  

src_path = "C:/Users/pel/Documents/UDAND/Proj 2_Openstreetmap/pyfiles/"
dest_path = "C:/Users/pel/Documents/UDAND/Proj 2_Openstreetmap/"
files = ['nodes.csv','ways.csv', 'ways_tags.csv', 'nodes_tags.csv', 'ways_nodes.csv']

def del_blankrows(src_path, dest_path, files):
    for filename in files:
		src_csv = src_path + filename
		print("\nReading in [{}] from [{}]...").format(filename, src_path)
		
		# Opens a new file with filename prefixed with 'clean_' for writing
		# out CSV non-blank rows. 
		with open('{}{}_{}'.format(dest_path,'clean',filename), 'w') as f_out:
			with open(src_csv) as f_in:
				if skip_header():
					next(f_in)
				for line in f_in:
					line = line.rstrip()
					if line != '':
						line = line + '\n'
						f_out.write(line)
		print("\nProcessed and saved [{}_{}] in [{}]\n").format('clean', filename, dest_path)
    
def skip_header():
	user_response = ""
	
	print("\n  Skip CSV column headers for CSV import to existing SQL table? ")
	while True:
		user_response = raw_input("  ==:> Press 'Y' for Yes, 'N' for No: ")
		print("  You entered: {}").format(user_response)
		
		if user_response == 'y' or user_response == 'yes':
			return True
		elif user_response == 'n' or user_response == 'no':
			return False
		else:
			print("  Please try again with 'Y' or 'N'\n")
	

if __name__ == '__main__':
    del_blankrows(src_path, dest_path, files)
