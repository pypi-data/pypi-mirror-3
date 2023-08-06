''' print nested list module '''

def print_lol(the_list):
    ''' print nested list function '''
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
