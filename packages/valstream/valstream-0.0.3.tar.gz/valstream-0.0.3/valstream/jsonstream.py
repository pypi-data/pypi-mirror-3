#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
import json

def select(fields):
    """select fields from stream"""

    if isinstance(fields, basestring):
        fields=fields.split(',')
    assert isinstance(fields, (list,tuple))

    for line in sys.stdin.readlines():
        data=json.loads(line)
        print json.dumps([data.get(f) for f in fields])

def expand():
    """pretty print singleline jsons"""
    for line in sys.stdin.readlines():
        data=json.loads(line)
        print json.dumps(data, indent=4)

def as_tsv():
    """convert from jsons, which are lists, to tsv."""
    for line in sys.stdin.readlines():
        data=json.loads(line)
        assert isinstance(data, list)
        print "\t".join([ unicode(c).encode('utf8') for c in data ])

def keep(field):
    """grep by attr"""
    for line in sys.stdin.readlines():
        data=json.loads(line)
        if data.get(field):
            print json.dumps(data)
