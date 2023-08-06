import pkg_resources
try:
    version = pkg_resources.require("pymeigo")[0].version
except:
    version = ""

import logging
logging.basicConfig(level=logging.ERROR)

logging.info("Importing pymeigo %s." % version)
logging.info("==========================")
logging.info("Checking that R packages can be loaded properly.")

from rpy2.robjects import rinterface
from rpy2.robjects import r


from cnolab.wrapper import tools
from cnolab.wrapper.tools import *

# set warning off
Rwarning(False)
try:
    import wrapper_meigo
    from wrapper_meigo import *
    logging.info(" * MEIGOR")
except ImportError,e:
    logging.warning(" * MEIGOR wrapper NOT loaded")
except rinterface.RRuntimeError, e:
    logging.warning(" * MEIGOR wrapper NOT loaded")
Rwarning(True)

import funcs
from funcs import *

import meigo
from meigo import *
