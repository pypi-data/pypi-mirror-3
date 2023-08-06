
list_info = [ 'abc', 'def', [ 'hahaha', 1950, 'kkk'] ]


def print_lol ( list_of_list ):

    for each_item in list_of_list:
        if ( isinstance (each_item, list)):
            print_lol (each_item)
        else:
            print (each_item)

