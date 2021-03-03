#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import logging

# Libs


# Custom
from synlogger.config import WORKER_PREFIX, WORKER_PORT


##################
# Configurations #
##################


########################
# Tests - WorkerLogger #
########################

def test_WorkerLogger_default_attibutes(worker_logger):
    """ 
    Tests for the correct initialisation defaults for the RootLogger class

    # C1: logger_name defaults to "WORKER_XXX"
    # C2: logging_variant defaults to "basic"
    # C3: server does not need to be specified by default
    # C4: port is assigned WORKER_PORT by default
    # C5: logging_level defaults to logging.INFO
    # C6: debugging_fields defaults to False
    # C7: filter_functions defaults to an empty list
    # C8: censor_keys defaults to an empty list (i.e. no information censored)
    """
    # C1
    assert WORKER_PREFIX in worker_logger.logger_name
    # C2       
    assert worker_logger.logging_variant == "basic"
    # C3        
    assert worker_logger.server is None
    # C4                    
    assert worker_logger.port == WORKER_PORT
    # C5                      
    assert worker_logger.logging_level == logging.INFO
    # C6     
    assert worker_logger.debugging_fields == False
    # C7        
    assert len(worker_logger.filter_functions) == 0  
    # C8       
    assert len(worker_logger.censor_keys) == 0 
    


