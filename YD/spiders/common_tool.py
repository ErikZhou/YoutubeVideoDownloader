import fnmatch
import os
import sys
import shutil
from flask import *


def list_files(path):
    list = []
    for file in os.listdir(path):
        fullpath = path + file
        isdir = os.path.isdir(fullpath) 
        #print(isdir)
        list.append([fullpath, isdir])
    return list


'''
Check if a Directory is empty : Method 1
'''
def isEmpty(path): 
    if not os.path.isdir(path):
        return False

    if len(os.listdir(path)) == 0:
        print("Directory is empty")
        return True
    else:    
        print("Directory is not empty")
        return False


def remove(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile(path) or os.path.islink(path):
        print('file was deleted:', path)
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))

path = '../videos/playlist/PL2DywIam67jsFoEhIvVhB0HukSP8IAIt0/'
print(path)
is_empty = isEmpty(path)
print(is_empty)
if is_empty:
    remove(path)
