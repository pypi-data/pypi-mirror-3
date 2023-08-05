"""
This module consists of the print_list function, which prints a list
"""

# This variable sets the basic indentation level. The default is 4 spaces,
# but feel free to modify it as you like
indent = ' ' * 4

def print_list(the_list, indent_level = 0):
    """
    This function takes a list and an indentation level as arguments, and
    prints each element of the list followed by four spaces multiplied by
    indent_level (second argument). If an element is another list (a list
    within a list), the function is called recursively, increasing the
    indentation by four spaces
    """

    for element in the_list:
        if isinstance(element, list):
            print_list(element, indent_level + 1)
        else:
            print(indent * indent_level + element)

