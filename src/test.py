# -*- coding: utf-8 -*-
import re
import sys
import os
import requests
from fake_useragent import UserAgent

def get_brand_list(file_name):
    path = os.path.abspath('..')
    file_path = os.path.join(path, 'infos', file_name)
    with open(file_path, mode='r') as f:
        return f.read()

def generate_new_file(path, pattern_name):
    file_name = "%s.csv" % pattern_name
    file_path = os.path.join(path, file_name)
    if os.path.exists(file_path):
        return file_name


if __name__ == '__main__':
    # list = "[1,2,3,5]"
    # a = list.pop()
    # a_list = "/price/series-412.html#pvareaid=2042205,/price/series-4460.html#pvareaid=2042205"
    # list = a_list.split(",")
    # list.reverse()
    print sys.getdefaultencoding()
