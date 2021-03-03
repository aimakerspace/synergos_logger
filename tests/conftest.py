#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import contextlib
import logging
import random
from string import Template
from typing import Callable

# Libs
import pytest
import structlog

# Custom
import synlogger

##################
# Configurations #
##################

HOST = "127.0.0.1"
PORT = 12201 # default port for general unittesting

DEFAULT_SUPPORTED_METADATA = [
    'event', 'logger', 'level', 'level_number', 
    'timestamp', 'file_path', 'log_level'
]
SYSMETRIC_SUPPORTED_METADATA = DEFAULT_SUPPORTED_METADATA + [
    'ID_path', 'ID_class', 'ID_function',
    'cpu_percent',
    'memory_total', 'memory_available', 'memory_used', 'memory_free',
    'disk_read_counter', 'disk_write_counter', 'disk_read_bytes', 'disk_write_bytes',
    'net_bytes_sent', 'net_bytes_recv', 'net_packets_sent', 'net_packets_recv'
]

DEFAULT_TRACKERS = [
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_log_level_number,
    structlog.stdlib.filter_by_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.format_exc_info,
    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
    structlog.processors.StackInfoRenderer(), 
    structlog.processors.UnicodeDecoder(),
]
SYSMETRIC_TRACKERS = DEFAULT_TRACKERS + [
    synlogger.utils.StructlogUtils.track_cpu_stats,
    synlogger.utils.StructlogUtils.track_memory_stats,
    synlogger.utils.StructlogUtils.track_disk_stats,
    synlogger.utils.StructlogUtils.track_network_stats
]

TRIALS = 20
EVENT_TEMPLATE = Template("This is Test no. $trial_idx!")
DURATION = 1
POLL_INTERVAL = 0.1

###########
# Helpers #
###########

def extract_name(callable: Callable) -> str:
    """ Given a callable that could be either a class or a function, retrieve
        its name at runtime for subsequent use

    Args:
        callable (Callable): Callable whose name is to be extracted
    Return:
        Name of callable (str)
    """
    try:
        return callable.__name__
    except:
        return type(callable).__class__.__name__


@contextlib.contextmanager
def reconfigure_global_structlog_params(syn_logger):
    """ Takes in a customised Synergos logger and  applies its params to the
        global context. This is required due to how Structlog.wrap_logger()
        works. There currently no way to capture logs from custom wrapped
        logger
    
    Args:
        syn_logger (synlogger.base.RootLogger): 
    """    
    # Save settings for subsequent restoration
    saved_config = structlog.get_config()

    # Extract custom processors in preparation for global override 
    custom_processors = syn_logger.synlog._processors

    try:
        structlog.reset_defaults()
        structlog.configure(
            processors=custom_processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict
        )
        logging.basicConfig(level=syn_logger.logging_level)
        logging_renderer = custom_processors[-1]
        yield logging_renderer.entries

    finally:
        # back to normal behavior
        structlog.configure(**saved_config)


def valid_test_filter(_, __, event_dict):
    """ This is a test filter that is inline with the construction requirements
        of Structlog processors. If processor ingestion is correct, the 
        corresponding log response will have 'is_valid=True' in the returned
        event dictionary.

    Args:
        event_dict (dict): Logging metadata accumulated
    Returns:
        Updated event metadata (dict)
    """
    event_dict['is_valid'] = True
    return event_dict


def invalid_test_filter_wrong_params(event_dict):
    """ This is a test filter that violates the construction requirements
        of Structlog processors, as it accepts the wrong inputs (all filters)
        must take in 3 parameters - logger, method and event_dict, although the
        first 2 is generally left for Structlog to automate). This filter is
        supposed to raise an Exception.

    Args:
        event_dict (dict): Logging metadata accumulated
    Returns:
        Updated event metadata (dict)
    """
    return event_dict
    

def invalid_test_filter_wrong_outputs(_, __, event_dict):
    """ This is a test filter that violates the construction requirements
        of Structlog processors, as it does not return the augmented event_dict.
        This breaks the processors This filter is supposed to raise an Exception.

    Args:
        event_dict (dict): Logging metadata accumulated
    Returns:
        Violating string (str)
    """
    return "some test string that violates the supposed proposed output"

##########################
# Miscellaneous Fixtures #
##########################

@pytest.fixture
def connect_kwargs():
    return {'server': HOST, 'port': PORT}


@pytest.fixture
def test_kwargs():
    random_base = random.randint(0, 10000000)
    return {
        'kwargs_test_str': f"test_string_{random_base}",
        'kwargs_test_int': 42 * random_base,
        'kwargs_test_float': 69.69 * random_base
    }


@pytest.fixture
def event_kwargs(connect_kwargs, test_kwargs):
    return {**connect_kwargs, **test_kwargs}

############################################
# StructlogUtils Helper Component Fixtures #
############################################

@pytest.fixture
def structlog_utils_default_params():
    return synlogger.utils.StructlogUtils()


@pytest.fixture
def structlog_utils():
    return synlogger.utils.StructlogUtils(
        file_path="/path/to/testfile"
    )


@pytest.fixture
def structlog_utils_with_censors(connect_kwargs, test_kwargs):
    all_keys = list(connect_kwargs.keys()) + list(test_kwargs.keys())
    n = 3
    keys_to_censor = random.sample(all_keys, n)
    return synlogger.utils.StructlogUtils(
        censor_keys=keys_to_censor,
        file_path="/path/to/testfile"
    )

#################################
# RootLogger Component Fixtures #
#################################

@pytest.fixture
def root_logger_default_params():
    return synlogger.base.RootLogger(logging_variant="basic")


@pytest.fixture
def root_logger_local():
    return synlogger.base.RootLogger(
        logger_name="test_local_logger",
        logging_variant="test"
    )


@pytest.fixture
def root_logger_remote(connect_kwargs):
    return synlogger.base.RootLogger(
        **connect_kwargs,
        logger_name="test_remote_logger",
        logging_variant="graylog"
    )


@pytest.fixture
def root_logger_custom_filters_valid():
    return synlogger.base.RootLogger(
        logger_name="test_custom_logger_valid_filter",
        logging_variant="test",
        filter_functions=[valid_test_filter]
    )


@pytest.fixture
def root_logger_custom_filters_wrong_params():
    return synlogger.base.RootLogger(
        logger_name="test_custom_logger_wrong_params",
        logging_variant="test",
        filter_functions=[invalid_test_filter_wrong_params]
    )


@pytest.fixture
def root_logger_custom_filters_wrong_outputs():
    return synlogger.base.RootLogger(
        logger_name="test_custom_logger_wrong_outputs",
        logging_variant="test",
        filter_functions=[invalid_test_filter_wrong_outputs]
    )

#####################################
# DirectorLogger Component Fixtures #
#####################################

@pytest.fixture
def director_logger():
    return synlogger.general.DirectorLogger(
        logger_name="Test_director_logger"
    )


@pytest.fixture
def ttp_logger():
    return synlogger.general.TTPLogger(
        logger_name="Test_ttp_logger"
    )


@pytest.fixture
def worker_logger():
    return synlogger.general.WorkerLogger(
        logger_name="Test_worker_logger"
    )

######################################
# SysmetricLogger Component Fixtures #
######################################

@pytest.fixture
def sysmetric_logger_default_params():
    return synlogger.general.SysmetricLogger(
        logger_name="Test_source_logger_default",
        logging_variant="basic"
    )


@pytest.fixture
def sysmetric_logger():
    return synlogger.general.SysmetricLogger(
        server=HOST,
        logger_name="Test_source_logger",
        logging_variant="test"
    )
