#-------------------------------------------------------------------------------
# Name:        中国
# Purpose:
#
# Author:      Saint
#
# Created:     17/08/2012
# Copyright:   (c) Saint 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def print_lol(movies):
    for item in movies:
        if isinstance(item,list):
            print_lol(item)
        else:
            print(item)
if __name__ == '__main__':
    print_lol()
