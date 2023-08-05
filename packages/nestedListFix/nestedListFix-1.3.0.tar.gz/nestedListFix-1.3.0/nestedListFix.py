"""nestedListFix.py module contains the print_lol() function to print lists and nested lists"""
def print_lol (the_list, indent=False, tabs=0):
    """print_lol() takes a first argument, "the_list", which can contain nested lists, and outputs each listed item on its own line using recursion! The second argument, tabs, allows you to set the indentation level of the nested lists"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol (each_item, indent, tabs+1)
        else:
            if indent:
                for tab_count in range(tabs):
                    print('\t', end='')
            print(each_item)
