from distutils.core import setup
    
setup(
    name = "configen",
    # packages = ["configen"],
    py_modules = ["configen"],
    scripts = ["configen.py"],
    version = "0.0.1",
    license = "LGPL",
    platforms = ['POSIX', 'Windows'],
    description = "instantiate a template from various parameter representations.",
    author = "tengu",
    author_email = "karasuyamatengu@gmail.com",
    url = "https://github.com/tengu/configen",
    keywords = [],
    classifiers = [
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Topic :: Software Development",
        ],
    long_description = """
* Synopsis

PROJECT_NAME=yoyodyne
FCGI_PORT=9000
configen.py init.conf.template > yoyodyne.conf

When automating software configuration, one ends up using adhoc templating scheme to 
parametrize config files with sed and awk. configen let's you use python's powerful 
string formatting to generate config files (or any text for that matter) with 
params from various sources.

* Usage
    * environment variables
      set a bunch of env vars in shell script and invoke from it.
      env foo=bar configen template

    * name-values fed to stdin
      echo foo=bar | configen tempalte -s
      env | configen tempalte -s

    * json
      configen template -j params.json

    * yaml
      configen template -y params.yaml

    * dash '-' can be passed for stdin

* Recpie
 
 * generating from a shell script
--------- genconf.sh
PROJECT_NAME=yoyodyne
PYTHON=/usr/bin/python
PROJECT_ROOT=/home/yoyo/dyne
RUNTIME_ROOT=/home/yoyo/dyne
FCGI_PORT=9000
USER=tengu

configen.py init.conf.t
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
	configen.py init.conf.t | tee $@
----------
"""
    )
