#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import os
import logging
import time
from typing import Callable

# Libs
import pytest
import structlog

# Custom
from conftest import (
    SYSMETRIC_SUPPORTED_METADATA,
    SYSMETRIC_TRACKERS,
    DURATION,
    POLL_INTERVAL,
    extract_name,
    reconfigure_global_structlog_params
)
from synlogger.config import SYSMETRICS_PREFIX, SYSMETRICS_PORT
from synlogger.utils import StructlogUtils


##################
# Configurations #
##################

file_path = os.path.abspath(__file__)
class_name = "SysmetricLoggerTest"
function_name = "test_SysmetricLogger_initialise"

###########################
# Tests - SysmetricLogger #
###########################

def test_SysmetricLogger_default_attibutes(sysmetric_logger_default_params):
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
    assert SYSMETRICS_PREFIX in sysmetric_logger_default_params.logger_name
    # C2       
    assert sysmetric_logger_default_params.logging_variant == "basic"
    # C3        
    assert sysmetric_logger_default_params.server is None
    # C4                    
    assert sysmetric_logger_default_params.port == SYSMETRICS_PORT
    # C5                      
    assert sysmetric_logger_default_params.logging_level == logging.INFO
    # C6     
    assert sysmetric_logger_default_params.debugging_fields == False
    # C7        
    assert len(sysmetric_logger_default_params.filter_functions) == 0  
    # C8       
    assert len(sysmetric_logger_default_params.censor_keys) == 0 


def test_SysmetricLogger_is_tracking(sysmetric_logger_default_params):
    """
    Tests if tracking state is toggling correctly. Note that while the state
    tested here is dependent on .track() & .terminate(), we are only testing
    for the change of state. The correctness of .track() & .terminate() is not
    enforced and is assumed to work here.

    # C1: is_tracking returns False before tracking is started
    # C2: is_tracking returns True after tracking is started
    # C3: is_tracking returns False after tracking has been terminated
    """
    # C1
    assert sysmetric_logger_default_params.is_tracking() == False
    # C2
    sysmetric_logger_default_params.track(
        file_path=file_path,
        class_name=class_name,
        function_name=function_name,
        resolution=POLL_INTERVAL
    )
    assert sysmetric_logger_default_params.is_tracking() == True
    # C3
    sysmetric_logger_default_params.terminate()
    assert sysmetric_logger_default_params.is_tracking() == False


def test_SysmetricLogger_configure_processors(sysmetric_logger_default_params):
    """
    Tests if sysmetric processors loaded are valid

    # C1: All processors returned are functions
    # C2: logging_renderer must be the last processor of the list
    # C3: Sysmetric processors must be included alongside default processors
    """
    # C1
    processors = sysmetric_logger_default_params._configure_processors()
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
        extract_name(sys_tracker) in processors_names
        for sys_tracker in SYSMETRIC_TRACKERS
    )


def test_SysmetricLogger_track(sysmetric_logger):
    """ 
    Tests if sysmetric process tracking starts & polls correctly

    # C1: Before tracking is initialised, sysmetric_logger.tracker is None
    # C2: After tracking is initialised, sysmetric_logger.tracker is not None
    # C3: After tracking is initialised, tracking process is actively running
    # C4: No. of trials recorded tallies with expected no. of records given
        a predetermined polling interval over a specified duration
    # C5: Each record detected has the appropriate metadata logged
    # C6: Each sysmetric metadata logged has valid values
    """
    # C1
    assert sysmetric_logger.tracker is None

    # Start tracking process to check for state changes
    sysmetric_logger.track(
        file_path=file_path,
        class_name=class_name,
        function_name=function_name,
        resolution=POLL_INTERVAL
    )

    # C2
    assert sysmetric_logger.tracker is not None
    # C3
    assert sysmetric_logger.tracker.is_alive()

    with reconfigure_global_structlog_params(sysmetric_logger) as cap_logs:
        sysmetric_logger.synlog.setLevel(logging.INFO) # V.IMPT!!!

        ###########################
        # Implementation Footnote #
        ###########################

        # [Cause]
        # Structlog's log capture mechanism does not allow for log capturing
        # from multiprocessed loggers with custom processors (i.e. non-global).

        # [Problems]
        # Sysmetric tracking is performed by running a backgrounded process
        # polling for logs once every specified interval. Being a struclog
        # logger, it suffers from the aforementioned limitations DURING TESTING.
        # This results in the failure to capture logs for analysis/testing.

        # [Solution]
        # Manually simulate probing behaviour in the global context, using
        # custom processors that are same as the ones running in the 
        # backgrounded logger.

        trial_count = int(DURATION/POLL_INTERVAL)
        for _ in range(trial_count):
            sysmetric_logger._probe(
                resolution=POLL_INTERVAL,
                descriptors={
                    "ID_path": file_path,
                    "ID_class": class_name,
                    "ID_function": function_name
                }
            )

        # C4
        assert len(cap_logs) == trial_count
        # C5
        assert all(                                                     
            set(SYSMETRIC_SUPPORTED_METADATA).issubset(list(record.keys()))
            for record in cap_logs
        )

        for record in cap_logs:
            # C6
            assert record.get('logger') == sysmetric_logger.logger_name
            assert record.get('file_path') == sysmetric_logger.file_path
            level_name = logging.getLevelName(sysmetric_logger.logging_level)
            assert record.get('level') == level_name.lower()
            assert record.get('log_level') == level_name.lower()
            assert record.get('level_number') == sysmetric_logger.logging_level
            assert isinstance(record.get('timestamp'), str)
            assert isinstance(record.get('ID_path'), str)
            assert isinstance(record.get('ID_class'), str)
            assert isinstance(record.get('ID_function'), str)
            assert isinstance(record.get('cpu_percent'), float)
            assert isinstance(record.get('memory_total'), int)
            assert isinstance(record.get('memory_available'), int)
            assert isinstance(record.get('memory_used'), int)
            assert isinstance(record.get('memory_free'), int)
            assert isinstance(record.get('disk_read_counter'), int)
            assert isinstance(record.get('disk_write_counter'), int)
            assert isinstance(record.get('disk_read_bytes'), int)
            assert isinstance(record.get('disk_write_bytes'), int)
            assert isinstance(record.get('net_bytes_sent'), int)
            assert isinstance(record.get('net_bytes_recv'), int)
            assert isinstance(record.get('net_packets_sent'), int)
            assert isinstance(record.get('net_packets_recv'), int)

        # Manually clean up process (no dependency on .terminate())                    
        sysmetric_logger.tracker.terminate() # send SIGTERM signal to the child
        sysmetric_logger.tracker.join()
        exit_code = sysmetric_logger.tracker.exitcode
        sysmetric_logger.tracker.close()
        sysmetric_logger.tracker = None      # Reset state of tracker
        # assert exit_code == 0                # successful termination    


def test_SysmetricLogger_terminate(sysmetric_logger):
    """ 
    Tests if sysmetric process tracking terminates correctly

    # C1: Before tracking is terminated, sysmetric_logger.tracker is not None
    # C2: Before tracking is terminated, tracking process is actively running
    # C3: After tracking is terminated, sysmetric_logger.tracker is None
    # C4: After tracking is terminated, saved tracker is no longer running
    # C5: Tracking was terminated gracefully
    """
    sysmetric_logger.track(
        file_path=file_path,
        class_name=class_name,
        function_name=function_name,
        resolution=POLL_INTERVAL
    )
    time.sleep(DURATION)

    # C1
    assert sysmetric_logger.tracker is not None
    # C2
    assert sysmetric_logger.tracker.is_alive()
    
    saved_tracker = sysmetric_logger.tracker
    exit_code = sysmetric_logger.terminate()

    # C3
    assert sysmetric_logger.tracker is None
    # C4
    assert saved_tracker._closed
    # C5
    assert exit_code == 0


@pytest.mark.xfail(raises=RuntimeError)
def test_SysmetricLogger_premature_termination(sysmetric_logger):
    """
    Tests if premature termination condition was caught and handled

    # C1: Check that 'RuntimeError(f"Attempted to terminate logger XXX before 
        initialisation!")' is caught, due to Exception being raised when
        checking for initialisation state in sysmetric_logger
    """
    sysmetric_logger.terminate()
