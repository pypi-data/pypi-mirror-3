"""This is the "nester.py" module, has a "print_lol" function"""
def print_lol(the_list, level):
    """This function has a parameter, is "the_list", it's any list."""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            for num in range(level):
                print("\t", end="")
            print(each_item)
