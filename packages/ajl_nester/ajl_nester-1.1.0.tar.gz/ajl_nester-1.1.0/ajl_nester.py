# Handle nested lists

def print_list( the_list, level):
    # Print nested list
    for i in the_list:
        if isinstance( i, list):
            print_list( i, level + 1)
        else:
            for tab_stop in range( level):
                print("\t", end="")
            print( i)
