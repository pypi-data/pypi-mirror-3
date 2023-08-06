"""This is the standard way to include a multiple-line comment is your code."""
def print_nl (pList):
    """This function requires one parameter"""
    for item in pList:
        if isinstance(item, list):
            print_nl(item)
        else:
            print(item)

