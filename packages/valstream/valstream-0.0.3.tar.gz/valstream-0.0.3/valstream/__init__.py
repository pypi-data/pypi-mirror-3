#!/usr/bin/env python
# -*- coding: utf-8 -*-

# all names not starting with under score must be a subcommand module.
import jsonstream as json
import tsv
import io
# import util
import graph
import dbi

import cli as _cli

_modules=dict([ (k,v) for k,v in locals().items() if not k.startswith('_') ])

def _main():
    _cli.main(_modules)

if __name__=='__main__':
    _main()
