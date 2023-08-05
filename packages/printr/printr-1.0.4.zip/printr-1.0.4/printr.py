#################################################################
#																#
#	PRINTR.PY 													#
#																#
#	Advanced printing for python terminal or file handling		#
#	Homepage: http://pypi.python.org/pypi/printr/1.0.3			#
#																#
#################################################################

import sys

def print_r(the_list, indent = False, level = 0, fh = sys.stdout):
	
	'''

	@param the_list		The list to iterate over
	@param indent		Option to indent output
	@param level		Number of levels to iterate
	@param fh			Output destination, stdout (screen) by default

	'''

	for each_item in the_list:

		if isinstance(each_item, list):
			print_r(each_item, indent, level + 1, fh)

		else:

			if indent:

				for tab_stop in range(level):
					print("\t" * level, end = '', file = fh)

			print(each_item, file = fh)

# End of file printr.py