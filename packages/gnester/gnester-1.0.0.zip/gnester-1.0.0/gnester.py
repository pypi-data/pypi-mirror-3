"""This module provides tools to print lists of elements to the console."""
def print_list(the_list):
	"""Prints every item in the given list"""
	for each_item in the_list:
		print_list_item(each_item)

def print_list_item(list_item):
	"""Prints the element if it is not a list.If it is a list, prints the list."""
	if isinstance(list_item, list):
		print_list(list_item)
	else:
		print(list_item)
