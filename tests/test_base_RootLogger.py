#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import json

# Libs


# Custom
from synlogger.utils import CPU_Filter


##################
# Configurations #
##################


######################
# Tests - RootLogger #
######################

def test_RootLogger_initialise(root_logger):
    """ 
    """
    syn_logging, _ = root_logger.initialise()
    for i in range(10):
        syn_logging.info(f"This is test message {i}")
    


