"""
This module consists of the print_list function, which prints a list
"""

# This variable sets the basic indentation level. The default is 4 spaces,
# but feel free to modify it as you like
indent = ' ' * 4

def print_list(the_list, indent_bool = False, indent_level = 0):
    """
    This function takes three arguments. The first one is the list to be
    printed. The second argument turns the indentation on/off when printing
    lists within lists. The third argument specifies the indent level.
    """

    for element in the_list:
        if isinstance(element, list):
            print_list(element, indent_bool, indent_level + 1)
        else:
            if indent_bool:
                print(indent * indent_level + element)
            else:
                print(element)

