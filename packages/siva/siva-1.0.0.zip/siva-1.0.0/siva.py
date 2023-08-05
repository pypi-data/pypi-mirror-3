"""My first module designed
to print a nested list"""
def print_list(sent_list):
    """This is the actual function doing the work"""
    for i in sent_list:
        if isinstance(i,list):
            print_list(i)
        else:
            print(i)
