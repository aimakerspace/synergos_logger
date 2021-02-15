#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import logging
import datetime
from typing import List, Tuple

# Lib
import psutil

# Custom


##################
# Configurations #
##################


################################################
# Organisational Helper Class - StructlogUtils #
################################################

class StructlogUtils:
    """
    Structlog utilities class for enhancing the functionality of the default 
    python logging package

    Attributes:
        censor_keys (list(str)): Censor any logs with the specified keys with 
            the value "*CENSORED*". This is for protecting user-specific secrets.
        file_path (str): File location where logging is called
    """
    def __init__(self, censor_keys: List[str] = [], file_path: str = ""):
        # General attributes
        # e.g. misc attibutes unique to problem
        self.censor_keys = censor_keys
        
        # Network attributes
        # e.g. server IP and/or port number


        # Data attributes
        # e.g participant_id/run_id in specific format
  

        # Optimisation attributes
        # e.g multiprocess/asyncio if necessary for optimisation


        # Export Attributes 
        # e.g. any artifacts that are going to be exported eg Records
        self.file_path = file_path


    ###########
    # Helpers #
    ###########

    def censor_logging(self, _, __, event_dict: dict) -> dict:
        """ Censor log information based on the the keys in the list 
            "censor_keys"

        Args:
            event_dict (dict): Logging metadata accumulated
        Returns:
            Censored event metadata (dict)
        """
        for key in self.censor_keys:
            k = event_dict.get(key)
            if k:
                event_dict[key] = "*CENSORED*"
        return event_dict


    def get_file_path(self, _, __, event_dict: dict) -> dict:
        """ Updates logging metadata with the path to script from which logging
            events were accumulated from

        Args:
            event_dict (dict): Logging metadata accumulated
        Returns:
            Updated event metadata (dict)
        """
        event_dict['file_path'] = self.file_path
        return event_dict


    def add_timestamp(self, _, __, event_dict: dict) -> dict:
        """ Updates logging metadata with the timestamp during which logging
            events were accumulated from

        Args:
            event_dict (dict): Logging metadata accumulated
        Returns:
            Updated event metadata (dict)
        """
        event_dict["timestamp"] = datetime.datetime.utcnow()
        return event_dict


    def graypy_structlog_processor(
        self, _, __,
        event_dict: dict
    ) -> Tuple[Tuple[str], dict]:
        """ Assembles arguments for to pass to Graylog interfacing class PyGelf

        Args:
            event_dict (dict): Logging metadata accumulated
        Returns:
            args (tuple(str))
            kwargs (dict)
        """
        args = (event_dict.get('event', ''),)
        kwargs = {'extra': event_dict}

        # The following are default graypy metrics which is logged to the 
        # graylog server comment these out if the following metrics are 
        # necessary. Alternatively we can set debugging_fields=False in GELF 
        # handler which is similar to the below kwargs setting
        kwargs['extra']['pid'] = ""
        kwargs['extra']['process_name'] = ""
        kwargs['extra']['thread_name'] = ""
        kwargs['extra']['file'] = ""
        # kwargs['extra']['function'] = ""

        return args, kwargs



###############################################################
# Logging Filter Clases for logging dynamic generated inputs  # 
###############################################################

class CPU_Filter(logging.Filter):
    """
    Logging the CPU Usage

    Attributes:
        cpu_percent (float): % of CPU used by system
    """
    def __init__(self):
        # In an actual use case would dynamically get this
        # (e.g. from memcache)
        self.cpu_percent = psutil.cpu_percent(interval=None)


    def filter(self, record: logging.LogRecord) -> bool:
        record.cpu_percent = self.cpu_percent
        return True # required if the record is to be processed



class Memory_Filter(logging.Filter):
    """
    Logging the Memory usage

    Attributes:
        memory_total (int): Total memory of system
        memory_available (int): Available memory for use by system
        memory_used (int): Memory used by system
        memory_free (int): Free memory unused by system
    """
    def __init__(self):
        # In an actual use case would dynamically get this
        # (e.g. from memcache)
        self.memory_total = psutil.virtual_memory().total
        self.memory_available = psutil.virtual_memory().available
        self.memory_used = psutil.virtual_memory().used
        self.memory_free = psutil.virtual_memory().free


    def filter(self, record: logging.LogRecord) -> bool:
        record.memory_total = self.memory_total
        record.memory_available = self.memory_available
        record.memory_used = self.memory_used
        record.memory_free = self.memory_free
        return True # required if the record is to be processed



class DiskIO_Filter(logging.Filter):
    """
    Logging the DiskIO usage

    Attributes:
        disk_read_counter (int): No. of disk reads
        disk_write_counter (int): No. of disk writes
        disk_read_bytes (int): No. of bytes read
        disk_write_bytes (int): No. of bytes wrote
    """
    def __init__(self):
        # In an actual use case would dynamically get this
        # (e.g. from memcache)
        self.disk_read_counter = psutil.disk_io_counters().read_count
        self.disk_write_counter = psutil.disk_io_counters().write_count
        self.disk_read_bytes = psutil.disk_io_counters().read_bytes
        self.disk_write_bytes = psutil.disk_io_counters().write_bytes


    def filter(self, record: logging.LogRecord) -> bool:
        record.disk_read_counter = self.disk_read_counter
        record.disk_write_counter = self.disk_write_counter
        record.disk_read_bytes = self.disk_read_bytes
        record.disk_write_bytes = self.disk_write_bytes
        return True # required if the record is to be processed



class NetIO_Filter(logging.Filter):
    """
    Logging the NetworkIO usage

    Attributes:
        net_bytes_sent (int): No. of bytes sent from the network
        net_bytes_recv (int): No. of bytes sent to the network
        net_packets_sent (int): No. of network packets sent 
        net_packets_recv (int): No. of network packets received
    """
    def __init__(self):
        # In an actual use case would dynamically get this
        # (e.g. from memcache)
        self.net_bytes_sent = psutil.net_io_counters().bytes_sent
        self.net_bytes_recv = psutil.net_io_counters().bytes_recv
        self.net_packets_sent = psutil.net_io_counters().packets_sent
        self.net_packets_recv = psutil.net_io_counters().packets_recv


    def filter(self, record: logging.LogRecord) -> bool:
        record.net_bytes_sent = self.net_bytes_sent
        record.net_bytes_recv = self.net_bytes_recv
        record.net_packets_sent = self.net_packets_sent
        record.net_packets_recv = self.net_packets_recv
        return True # required if the record is to be processed