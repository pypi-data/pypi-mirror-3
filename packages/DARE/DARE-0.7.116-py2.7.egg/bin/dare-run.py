#!/usr/bin/env python

__author__    = "Sharath Maddineni"
__email__     = "smaddineni@cct.lsu.edu"
__copyright__ = "Copyright 2011, Sharath Maddineni"
__license__   = "MIT"

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "..")

import optparse
parser = optparse.OptionParser()

from daresrc.runtime import DareManager

from daresrc import logging

def main(conffile):
    
    # parse conf files
    #parser = optparse.OptionParser()
    #parser.add_option("-c", "--conf_job", dest="conf_job", help="job configuration file")
    #(options, args) = parser.parse_args()

    #confjob = options.conf_job

    logging.debug("starting DARE")
    try:
       dare = DareManager(conffile)
       #dare.start()
    except KeyboardInterrupt:
       dare.cancel()

    logging.debug("DARE Exec Done")
     
if __name__ == "__main__":
    if (len(sys.argv)> 1): 
       conffile = sys.argv[1] 
    else:
       raise Exception, "missing dare configurtion file" 
    main(conffile)