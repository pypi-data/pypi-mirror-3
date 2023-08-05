# Begin
def print_r(the_list, level = 0):
	
	# @arg the_list	The list to iterate over
	# @arg level	Number of levels for iteration
	
	for each_item in the_list:

		if isinstance(each_item, list):
			print_r(each_item, level + 1)

		else:

			for tab_stop in range(level):
				print("\t", end = '')
				
			print(each_item)

# End of file printr.py