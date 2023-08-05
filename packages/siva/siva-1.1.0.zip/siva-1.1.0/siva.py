"""My first module designed
to print a nested list"""
def print_list(sent_list,level):
    """This is the actual function doing the work.
        a seaond argument "level" is uses to represent the number of tab stops"""
    for i in sent_list:
        if isinstance(i,list):
            print_list(i,level+1)
        else:
            for tab_stops in range(level):
                print("\t",end='')
            print(i)


            
