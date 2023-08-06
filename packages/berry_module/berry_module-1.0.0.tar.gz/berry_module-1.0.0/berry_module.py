"""This is a simple module"""
def print_lol(items):
    for each_item in items:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
            
