#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import logging
from datetime import datetime
from attr import dataclass

# Libs
import pytest
import structlog

# Custom
from synlogger.config import CENSOR


##################
# Configurations #
##################

logger = logging.getLogger()
method = logging.getLevelName(logging.INFO) 

##########################
# Tests - StructlogUtils #
##########################

def test_StructlogUtils_default_attibutes(structlog_utils_default_params):
    """ 
    Tests for the correct initialisation defaults for the TTPLogger class

    # C1: censor_keys defaults to an empty list (i.e. no information censored)
    # C2: log_path defaults an empty string
    """
    # C1
    assert len(structlog_utils_default_params.censor_keys) == 0 
    # C2
    assert structlog_utils_default_params.file_path == ""


def test_StructlogUtils_censor_logging(
    structlog_utils_with_censors,
    event_kwargs
):
    """
    Tests if log censoring is functioning correctly

    # C1: Checks if specified censors are applied to their respective keys
    """
    # C1
    censored_keys = structlog_utils_with_censors.censor_keys
    censored_event_dict = structlog_utils_with_censors.censor_logging(
        logger,
        method,
        event_dict=event_kwargs
    )
    assert all(
        censored_event_dict.get(key) == CENSOR
        for key in censored_keys
    )


def test_StructlogUtils_get_file_path(structlog_utils, event_kwargs):
    """
    Tests if file path is logged automatically

    # C1: Checks if file path is added to the event dictionary
    """
    # C1
    augmented_event_dict = structlog_utils.get_file_path(
        logger,
        method,
        event_dict=event_kwargs
    )
    assert augmented_event_dict.get('file_path') == structlog_utils.file_path


def test_StructlogUtils_add_timestamp(structlog_utils, event_kwargs):
    """
    Tests if timestamp is logged automatically

    # C1: Checks if timestamp is added to the event dictionary
    # C2: Checks if timestamp added is of the correct datatype
    """
    augmented_event_dict = structlog_utils.add_timestamp(
        logger,
        method,
        event_dict=event_kwargs
    )
    timestamp = augmented_event_dict.get('timestamp')
    # C1
    assert timestamp
    # C2
    assert isinstance(timestamp, datetime)


def test_StructlogUtils_track_cpu_stats(structlog_utils, event_kwargs):
    """
    Tests if CPU meta-statistics are logged automatically

    # C1: Checks if CPU meta-statistics have been added to the event dictionary
    # C2: Checks if CPU meta-statistics added is of the correct datatype
    """
    augmented_event_dict = structlog_utils.track_cpu_stats(
        logger,
        method,
        event_dict=event_kwargs
    )
    cpu_percent = augmented_event_dict.get('cpu_percent')
    # C1
    assert cpu_percent
    # C2
    assert isinstance(cpu_percent, float)


def test_StructlogUtils_track_memory_stats(structlog_utils, event_kwargs):
    """
    Tests if memory (RAM) meta-statistics are logged automatically 

    # C1: Checks if memory meta-statistics is added to the event dictionary
    # C2: Checks if memory meta-statistics added is of the correct datatype
    """
    augmented_event_dict = structlog_utils.track_memory_stats(
        logger,
        method,
        event_dict=event_kwargs
    )
    memory_total = augmented_event_dict.get('memory_total')
    memory_available = augmented_event_dict.get('memory_available')
    memory_used = augmented_event_dict.get('memory_used')
    memory_free = augmented_event_dict.get('memory_free')

    for ram_stat in (memory_total, memory_available, memory_used, memory_free):
        # C1
        assert ram_stat
        # C2
        assert isinstance(ram_stat, int)


def test_StructlogUtils_track_disk_stats(structlog_utils, event_kwargs):
    """
    Tests if disk meta-statistics are logged automatically 

    # C1: Checks if disk meta-statistics is added to the event dictionary
    # C2: Checks if disk meta-statistics added is of the correct datatype
    """
    augmented_event_dict = structlog_utils.track_disk_stats(
        logger,
        method,
        event_dict=event_kwargs
    )
    disk_read_counter = augmented_event_dict.get('disk_read_counter')
    disk_write_counter = augmented_event_dict.get('disk_write_counter')
    disk_read_bytes = augmented_event_dict.get('disk_read_bytes')
    disk_write_bytes = augmented_event_dict.get('disk_write_bytes')

    for disk_stat in (
        disk_read_counter,
        disk_write_counter, 
        disk_read_bytes,
        disk_write_bytes
    ):
        # C1
        assert disk_stat
        # C2
        assert isinstance(disk_stat, int)


def test_StructlogUtils_track_network_stats(structlog_utils, event_kwargs):
    """
    Tests if network meta-statistics are logged automatically 

    # C1: Checks if network meta-statistics is added to the event dictionary
    # C2: Checks if network meta-statistics added is of the correct datatype
    """
    augmented_event_dict = structlog_utils.track_network_stats(
        logger,
        method,
        event_dict=event_kwargs
    )
    net_bytes_sent = augmented_event_dict.get('net_bytes_sent')
    net_bytes_recv = augmented_event_dict.get('net_bytes_recv')
    net_packets_sent = augmented_event_dict.get('net_packets_sent')
    net_packets_recv = augmented_event_dict.get('net_packets_recv')

    for net_stat in (
        net_bytes_sent,
        net_bytes_recv, 
        net_packets_sent,
        net_packets_recv
    ):
        # C1
        assert net_stat
        # C2
        assert isinstance(net_stat, int)


def test_StructlogUtils_graypy_structlog_processor(
    structlog_utils, 
    event_kwargs
):
    """
    Tests if event dictionary can be converted to a Graylog handler compatible
    format, to be passed as arguments/keyword arguments

    # C1: Check that the position-based arguments are formatted correct
    # c2: Check that keyword-based arguments are formatted correctly
    """
    args, kwargs = structlog_utils.graypy_structlog_processor(
        logger,
        method,
        event_dict=event_kwargs
    )
    # C1
    assert args == (event_kwargs.get('event', ''),)
    # C2
    cached_event_dict = kwargs.get('extra')
    for key, value in cached_event_dict.items():
        assert isinstance(cached_event_dict.get('pid'), str)
        assert isinstance(cached_event_dict.get('process_name'), str)
        assert isinstance(cached_event_dict.get('thread_name'), str)
        assert isinstance(cached_event_dict.get('file'), str)
        assert isinstance(cached_event_dict.get('function'), str)