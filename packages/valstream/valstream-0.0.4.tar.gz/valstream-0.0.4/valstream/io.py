#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json

def read_lines(file=sys.stdin):
    """non-buffered, chomped readlines()"""
    
    while True:
        line=file.readline()
        if not line:
            break
        yield line.strip('\n')

def read_jsons(file=sys.stdin):
    """ """
    for line in read_lines(file):
        yield json.loads(line)

def read_tsv(file=sys.stdin):

    for line in read_lines(file):
        yield line.split('\t')
