"""This is a recursive list printer -
it just dumps your list as a series of text files
"""
import sys

tArray = [1,[2,3,['a','b','c']]]

def pd(aList=tArray, indent=False, level=0, fh=sys.stdout):
    for a in aList:
        if isinstance(a, list):
            pd(a,indent,level+1, fh)
        else:
            if indent:
                for t in range(level):
                    print('\t', end='',file=fh)
            print(a,file=fh)
