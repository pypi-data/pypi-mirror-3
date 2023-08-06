import pkg_resources
try:
    version = pkg_resources.require("pymeigo")[0].version
except:
    version = "unknown"

import logging
logging.basicConfig(level=logging.ERROR)

logging.info("Importing pymeigo %s." % version)
logging.info("==========================")
logging.info("Checking that R packages can be loaded properly.")

import wrapper_meigo
from wrapper_meigo import *

import funcs
from funcs import *

import meigo
from meigo import *
