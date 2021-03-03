#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import logging
from typing import Callable

# Libs
import pytest
import structlog

# Custom
from conftest import (
    TRIALS, 
    EVENT_TEMPLATE,
    DEFAULT_SUPPORTED_METADATA,
    DEFAULT_TRACKERS,
    extract_name,
    reconfigure_global_structlog_params
)
from synlogger.utils import StructlogUtils

##################
# Configurations #
##################


######################
# Tests - RootLogger #
######################

def test_RootLogger_default_attibutes(root_logger_default_params):
    """ 
    Tests for the correct initialisation defaults for the RootLogger class

    # C1: logger_name defaults to "std_log"
    # C2: logging_variant defaults to "basic"
    # C3: server does not need to be specified by default
    # C4: port does not need to be specified by default
    # C5: logging_level defaults to logging.INFO
    # C6: debugging_fields defaults to False
    # C7: filter_functions defaults to an empty list
    # C8: censor_keys defaults to an empty list (i.e. no information censored)
    """
    # C1
    assert root_logger_default_params.logger_name == "std_log"
    # C2       
    assert root_logger_default_params.logging_variant == "basic"
    # C3        
    assert root_logger_default_params.server is None
    # C4                    
    assert root_logger_default_params.port is None
    # C5                      
    assert root_logger_default_params.logging_level == logging.INFO
    # C6     
    assert root_logger_default_params.debugging_fields == False
    # C7        
    assert len(root_logger_default_params.filter_functions) == 0  
    # C8       
    assert len(root_logger_default_params.censor_keys) == 0       


def test_RootLogger_is_initialised(root_logger_default_params):
    """ 
    Tests for correct initialisation state switching

    # C1: Returns False before .initialise() is ran
    # C2: Returns True after .initialise() is ran
    """
    # C1
    assert root_logger_default_params.is_initialised() == False
    # C2      
    root_logger_default_params.initialise()
    assert root_logger_default_params.is_initialised() == True          


def test_RootLogger_configure_processors(root_logger_default_params):
    """
    Tests if default processors loaded are valid

    # C1: All processors returned are functions
    # C2: logging_renderer must be the last processor of the list
    """
    # C1
    processors = root_logger_default_params._configure_processors()
    assert all(isinstance(_funct, Callable) for _funct in processors)
    # C2   
    last_processor = processors[-1]
    assert any(                                                         
        extract_name(last_processor) == extract_name(_funct)
        for _funct in [
            StructlogUtils.graypy_structlog_processor,
            structlog.processors.JSONRenderer(indent=1)
        ]
    )
    # C3
    processors_names = [extract_name(processor) for processor in processors]
    assert all(
        extract_name(def_tracker) in processors_names
        for def_tracker in DEFAULT_TRACKERS
    )


def test_RootLogger_initialise(root_logger_default_params):
    """ 
    Tests if state transitions during initialisation are valid

    # C1: root_logger.synlog is None before .initialise() is ran
    # C2: root_logger.synlog is not None after .initialise() is ran
    # C3: root_logger.synlog is built upon a global configured logging object
    # C4: root_logger.synlog has processors applied, where processors 
        configured include both default processors and custom processors from 
        self.filter_functions
    """
    # C1
    assert root_logger_default_params.synlog is None 
    # C2                      
    root_logger_default_params.initialise()
    assert root_logger_default_params.synlog is not None
    # C3                 
    core_logger = logging.getLogger(root_logger_default_params.logger_name)
    assert root_logger_default_params.synlog._logger == core_logger    
    # C4    
    configured_processors = [
        extract_name(_funct) 
        for _funct in root_logger_default_params._configure_processors()
    ]
    loaded_processors = [
        extract_name(_funct)
        for _funct in root_logger_default_params.synlog._processors
    ]
    assert all(                                                            
        _functname in loaded_processors
        for _functname in configured_processors
    )    


def test_RootLogger_synlog_local_logging(root_logger_local, test_kwargs):
    """
    Test output formatting when logging locally across X simulated trials

    # C1: X records are detected
    # C2: Each record detected has the appropriate metadata logged
    # C3: Each default metadata logged has valid values
    # C4: Each custom metadata logged corresponds to each statement made
        a. kwargs_test_str
        b. kwargs_test_int
        c. kwargs_test_float
    """
    root_logger_local.initialise()
    with reconfigure_global_structlog_params(root_logger_local) as cap_logs:
        root_logger_local.synlog.setLevel(logging.INFO) # V.IMPT!!!

        # Simulate X logging statements
        for trial_idx in range(TRIALS):
            event_msg = EVENT_TEMPLATE.substitute({'trial_idx': trial_idx})
            root_logger_local.synlog.info(event_msg, **test_kwargs)

        # C1
        assert len(cap_logs) == TRIALS              
        # C2
        assert all(                                                     
            set(DEFAULT_SUPPORTED_METADATA).issubset(list(record.keys()))
            for record in cap_logs
        )

        for r_idx in range(len(cap_logs)):
            record = cap_logs[r_idx]
            # C3
            assert record.get('logger') == root_logger_local.logger_name
            assert record.get('file_path') == root_logger_local.file_path
            level_name = logging.getLevelName(root_logger_local.logging_level)
            assert record.get('level') == level_name.lower()
            assert record.get('log_level') == level_name.lower()
            assert record.get('level_number') == root_logger_local.logging_level
            assert record.get('timestamp') # needs to be recorded
            # C4
            for key, value in test_kwargs.items():
                assert record.get(key) == value
        

def test_RootLogger_synlog_remote_logging(root_logger_remote):
    """
    Tests output formatting when logging remotely

    # C1: Graylog Renderer is located at the end of initialised processors
    """
    root_logger_remote.initialise()
    structlog_utils = StructlogUtils(
        censor_keys=root_logger_remote.censor_keys,
        file_path=root_logger_remote.file_path
    )
    curr_renderer_name = root_logger_remote.synlog._processors[-1].__name__
    correct_renderer_name = structlog_utils.graypy_structlog_processor.__name__
    assert curr_renderer_name == correct_renderer_name


def test_RootLogger_valid_filter(root_logger_custom_filters_valid):
    """
    Tests that filtering functions are applied properly. This test assures that
    a correctly formatted processor will be accepted into the Structlog 
    processors chain

    # C1: Check that valid filter processor was applied
    """
    root_logger_custom_filters_valid.initialise()
    with reconfigure_global_structlog_params(
        root_logger_custom_filters_valid
    ) as cap_logs:
        root_logger_custom_filters_valid.synlog.setLevel(logging.INFO)
        # C1
        root_logger_custom_filters_valid.synlog.info()
        record = cap_logs[0]
        assert record.get('is_valid')


@pytest.mark.xfail(raises=TypeError)
def test_RootLogger_invalid_filter_wrong_params(
    root_logger_custom_filters_wrong_params
):
    """
    Tests output formatting when logging remotely. This test assures that a
    wrongly formatted processor with incorrect input parameters will raise 
    an error

    # C1: Check that "TypeError: invalid_test_filter_wrong_params() takes 1 
        positional argument but 3 were given" is caught due to incompatible
        processor input
    """
    root_logger_custom_filters_wrong_params.initialise()
    with reconfigure_global_structlog_params(
        root_logger_custom_filters_wrong_params
    ) as _:
        root_logger_custom_filters_wrong_params.synlog.setLevel(logging.INFO)
        # C1
        root_logger_custom_filters_wrong_params.synlog.info()


@pytest.mark.xfail(raises=TypeError)
def test_RootLogger_invalid_filter_wrong_outputs(
    root_logger_custom_filters_wrong_outputs
):
    """
    Tests output formatting when logging remotely. This test assures that a
    wrongly formatted processor with incorrect outputs will raise an error

    # C1: Check that "TypeError: XXX missing 1 required positional argument" is
        caught, due to incompatible processor output
    """
    root_logger_custom_filters_wrong_outputs.initialise()
    with reconfigure_global_structlog_params(
        root_logger_custom_filters_wrong_outputs
    ) as _:
        root_logger_custom_filters_wrong_outputs.synlog.setLevel(logging.INFO)
        # C1
        root_logger_custom_filters_wrong_outputs.synlog.info()