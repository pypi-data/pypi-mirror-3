"""nester.py module contains the print_lol() function to print lists and nested lists"""
def print_lol (the_list):
	
	"""print_lol() takes a single argument, "the_list", which can 		contain nested lists, and outputs each listed item on its own 		line using recursion!"""
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol (each_item)
		else:
			print(each_item)
