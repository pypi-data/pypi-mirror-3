#!/usr/bin/env python
#-*- coding:utf-8 -*-


""" JSON paths manipulation utilities: splitting, etc.
"""


def split(path):
    result = []
    for node in path.split('/')[1:]:
        if '[' in node and ']' in node:
            array, index = node.split('[')
            result.append({'t': 'array', 'name': array})
            result.append({'t': 'index', 'name': int(index[:-1])})
        else:
            result.append({'t': 'object', 'name': node})
    return result

