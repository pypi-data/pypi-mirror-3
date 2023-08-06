"""This is mttm.py test module who provides
    miki's test functions"""

def print_list(the_list, level=0):
    """This function takes parameter the_list,
    and level of nested tabs and displays it"""

    for each_item in the_list:
        if isinstance(each_item, list):
            print_list(each_item, level+1)
        else:
            for each_tab in range(level):
                print('\t', end='')
            print(each_item)
