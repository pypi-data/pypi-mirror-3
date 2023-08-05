# Begin
def print_r(the_list):
	
	# @arg the_list
	
	for each_item in the_list:
		if isinstance(each_item, list):
			print_r(each_item)
		else:
			print(each_item)

# End of file printr.py