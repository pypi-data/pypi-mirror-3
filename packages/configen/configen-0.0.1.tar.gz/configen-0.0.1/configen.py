#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" configen: Instantiate a template with params from various sources.

    * from environment variables
      set a bunch of env vars in shell script and invoke from it.
      env foo=bar configen template
      Just set variables and invoke from a shell script.

    * from name-values fed to stdin
      echo foo=bar | configen tempalte -t -
      env | configen tempalte -t -

    * from json
      configen template -j params.json

    * from yaml
      configen template -y params.yaml

    dash '-' can be passed for stdin.
    see also: configen -h

* recpie
 
 * generating from a shell script
--------- genconf.sh
PROJECT_NAME=yoyodyne
PYTHON=/usr/bin/python
PROJECT_ROOT=/home/yoyo/dyne
RUNTIME_ROOT=/home/yoyo/dyne
FCGI_PORT=9000
USER=tengu

./configen.py init.conf.t > yoyodyne.init
---------

 * generating a config file from makefile
   export the variables and run configen as follows:

---------- Makefile
export PROJECT_NAME=yoyodyne
export PYTHON=/usr/bin/python
export PROJECT_ROOT=/home/yoyo/dyne
export RUNTIME_ROOT=/home/yoyo/dyne
export FCGI_PORT=9000
USER=tengu

yoyodyne.conf:
	./configen.py init.conf.t | tee $@
----------

"""
import sys,os
from optparse import OptionParser

def parse_opt():

    parser = OptionParser()

    parser.add_option("-d", 
                      "--doc",
                      dest="doc", 
                      action="store_true",
                      default=False,
                      help="print detailed usage.")

    parser.add_option("-t", 
                      "--text",
                      dest="text", 
                      help="read name/value pairs of form foo=bar")

    parser.add_option("-j", 
                      "--json", 
                      dest="json",
                      help="load params from a json file")

    parser.add_option("-y", 
                      "--yaml", 
                      dest="yaml",
                      help="load params from a yaml file")

    return parser.parse_args()

def inputstream(filename):
    if filename=='-':
        return sys.stdin
    return file(filename)

def main():

    opt, args=parse_opt()

    if opt.doc:
        print __doc__
        sys.exit(0)

    if not args:
        print >>sys.stderr, "see %s -h" % (sys.argv[0], )
        sys.exit(1)

    # select params. defaults to environment variables. xx use callback
    params=os.environ
    if opt.text:
        params=dict([ l.strip().split('=') for l in inputstream(opt.text).readlines() ])
    elif opt.json:
        import json
        params=json.load(inputstream(opt.json))
    elif opt.yaml:
        import yaml
        params=yaml.load(inputstream(opt.yaml))

    template_file,=args
    template=file(template_file).read()
    try:
        interpolated=template.format(**params)
    except KeyError,e:
        name,=e.args
        print >>sys.stderr, 'missing param "%s"' % name
        sys.exit(1)
    print interpolated

if __name__=='__main__':

    main()
