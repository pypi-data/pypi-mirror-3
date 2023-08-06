#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      CSScruggs12
#
# Created:     09/05/2012
# Copyright:   (c) CSScruggs12 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

def main():
    pass

if __name__ == '__main__':
    main()
def print_lol(the_list):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
    else:
        print(each_item)