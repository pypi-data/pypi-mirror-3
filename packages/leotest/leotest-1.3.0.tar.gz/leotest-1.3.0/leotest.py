"""This is the "nester.py" module, has a "print_lol" function"""
def print_lol(the_list, indent=False, level=0):
    """This function has a parameter, is "the_list", it's any list."""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1)
        else:
            if indent:
                for num in range(level):
                    print("\t", end="")
            print(each_item)
