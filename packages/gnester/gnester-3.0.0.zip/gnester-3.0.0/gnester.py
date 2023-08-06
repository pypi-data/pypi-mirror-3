"""This module provides tools to print lists of elements to the console."""
def print_list(the_list, use_indenting=False, indent_level=0):
        """Prints every item in the given list using the given indent level for any nested items.
        If the item is a list, recurse on this method."""
        for list_item in the_list:
                if isinstance(list_item, list):
                        print_list(list_item, use_indenting, indent_level + 1)
                else:
                        if (use_indenting):
                                for tab in range(indent_level):
                                        print("\t", end="")
                        print(list_item)
