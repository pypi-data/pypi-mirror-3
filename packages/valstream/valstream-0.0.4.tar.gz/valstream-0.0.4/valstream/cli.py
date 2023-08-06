#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
import jsonstream as json
import tsv
import io
# import util
import graph

def _map_args(argv):
    """placeholder for command-to-function argument mapping"""
    return argv

def _usage(major_cmds):
    print """usage {exe} [{major_cmds}] ... 
""".format(exe=sys.argv[0],
           major_cmds='|'.join(major_cmds))

def main(modules):
    """command entry point"""
    
    try:
        major=sys.argv[1]
    except IndexError:
        _usage(modules)
        sys.exit(1)

    del sys.argv[0]
    modules[major].main()

if __name__=='__main__':
    main()
