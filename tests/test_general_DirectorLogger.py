#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import logging

# Libs


# Custom
from synlogger.config import DIRECTOR_PREFIX, DIRECTOR_PORT

##################
# Configurations #
##################


##########################
# Tests - DirectorLogger #
##########################

def test_DirectorLogger_default_attibutes(director_logger):
    """ 
    Tests for the correct initialisation defaults for the DirectorLogger class

    # C1: logger_name defaults to "DIR_XXX"
    # C2: logging_variant defaults to "basic"
    # C3: server does not need to be specified by default
    # C4: port is assigned DIRECTOR_PORT by default
    # C5: logging_level defaults to logging.INFO
    # C6: debugging_fields defaults to False
    # C7: filter_functions defaults to an empty list
    # C8: censor_keys defaults to an empty list (i.e. no information censored)
    """
    # C1
    assert DIRECTOR_PREFIX in director_logger.logger_name
    # C2       
    assert director_logger.logging_variant == "basic"
    # C3        
    assert director_logger.server is None
    # C4                    
    assert director_logger.port == DIRECTOR_PORT
    # C5                      
    assert director_logger.logging_level == logging.INFO
    # C6     
    assert director_logger.debugging_fields == False
    # C7        
    assert len(director_logger.filter_functions) == 0  
    # C8       
    assert len(director_logger.censor_keys) == 0 
    
