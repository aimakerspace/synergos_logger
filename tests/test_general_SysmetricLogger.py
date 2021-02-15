#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import json
import os

# Libs


# Custom


##################
# Configurations #
##################

file_path = os.path.abspath(__file__)
class_name = "SysmetricLoggerTest"
function_name = "test_SysmetricLogger_initialise"

###########################
# Tests - SysmetricLogger #
###########################

def test_SysmetricLogger_initialise(sysnetric_logger):
    """ 
    """
    sysnetric_logger.track(
        file_path=file_path,
        class_name=class_name,
        function_name=function_name
    )
    


