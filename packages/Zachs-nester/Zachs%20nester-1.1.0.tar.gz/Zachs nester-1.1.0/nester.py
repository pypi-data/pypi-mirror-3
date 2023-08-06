"""This is a recursive list printer -
it just dumps your list as a series of text files
"""

def print_list(the_list, level):
    for a in the_list:
        if isinstance(a, list):
            print_list(a, level+1)
        else:
            for i in range(level):
                print ("\t", end='')
            print(a)
            


