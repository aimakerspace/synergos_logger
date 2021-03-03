#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import logging

# Libs


# Custom
from synlogger.config import TTP_PREFIX, TTP_PORT


##################
# Configurations #
##################


#####################
# Tests - TTPLogger #
#####################

def test_TTPLogger_default_attibutes(ttp_logger):
    """ 
    Tests for the correct initialisation defaults for the TTPLogger class

    # C1: logger_name defaults to "TTP_XXX"
    # C2: logging_variant defaults to "basic"
    # C3: server does not need to be specified by default
    # C4: port is assigned TTP_PORT by default
    # C5: logging_level defaults to logging.INFO
    # C6: debugging_fields defaults to False
    # C7: filter_functions defaults to an empty list
    # C8: censor_keys defaults to an empty list (i.e. no information censored)
    """
    # C1
    assert TTP_PREFIX in ttp_logger.logger_name
    # C2       
    assert ttp_logger.logging_variant == "basic"
    # C3        
    assert ttp_logger.server is None
    # C4                    
    assert ttp_logger.port == TTP_PORT
    # C5                      
    assert ttp_logger.logging_level == logging.INFO
    # C6     
    assert ttp_logger.debugging_fields == False
    # C7        
    assert len(ttp_logger.filter_functions) == 0  
    # C8       
    assert len(ttp_logger.censor_keys) == 0 
    


