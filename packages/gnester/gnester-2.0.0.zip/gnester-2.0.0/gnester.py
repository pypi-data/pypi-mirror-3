"""This module provides tools to print lists of elements to the console."""
def print_list(the_list, indent_level=0):
	#print("LIST BEING PRINTED:")
	#print(the_list)
	#print("INDENTATION LEVEL OF:")
	#print(indent_level)
	"""Prints every item in the given list using the given indent level for any nested items.
		If the item is a list, recurse on this method."""
	#print("Cycling through the list")
	for list_item in the_list:
		#print("THE CURRENT LIST ITEM")
		#print(list_item)
		if isinstance(list_item, list):
			#print("THIS IS A LIST")
			#print("RECURSE")
			print_list(list_item, indent_level + 1)
		else:
			#print("THIS IS NOT A LIST")
			for tab in range(indent_level):
				print("\t", end="")
			print(list_item)

