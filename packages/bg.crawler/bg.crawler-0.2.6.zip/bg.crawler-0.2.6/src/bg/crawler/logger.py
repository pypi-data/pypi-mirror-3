################################################################
# bg.crawler
# (C) 2011, ZOPYX Ltd.  - written for BG Phoenics
################################################################

import os
import sys
import logging
import logging.handlers


def getLogger():
    handler = logging.StreamHandler(sys.stdout) 
    frm = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", 
                                  "%d.%m.%Y %H:%M:%S") 
    handler.setFormatter(frm)

    logger = logging.getLogger() 
    logger.addHandler(handler) 
    logger.setLevel(logging.DEBUG)
    return logger

LOG = getLogger()
