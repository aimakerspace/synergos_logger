#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import datetime
import inspect
from typing import List, Tuple

# Lib
import psutil
from structlog._frames import _find_first_app_frame_and_name

# Custom
from synlogger.config import CENSOR

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
                event_dict[key] = CENSOR
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
        event_dict['timestamp'] = datetime.datetime.utcnow()
        return event_dict


    def track_cpu_stats(self, _, __, event_dict: dict) -> dict:
        """ Logs the following CPU statistics of the system:
            1) % of CPU used by system

        Args:
            event_dict (dict): Logging metadata accumulated
        Returns:
            Updated event metadata (dict)
        """
        event_dict['cpu_percent'] = psutil.cpu_percent(interval=None)
        return event_dict


    def track_memory_stats(self, _, __, event_dict: dict) -> dict:
        """ Logs the following memory statistics of the system:
            1) memory_total (int): Total memory of system
            2) memory_available (int): Available memory for use by system
            3) memory_used (int): Memory used by system
            4) memory_free (int): Free memory unused by system


        Args:
            event_dict (dict): Logging metadata accumulated
        Returns:
            Updated event metadata (dict)
        """
        event_dict['memory_total'] = psutil.virtual_memory().total
        event_dict['memory_available'] = psutil.virtual_memory().available
        event_dict['memory_used'] = psutil.virtual_memory().used
        event_dict['memory_free'] = psutil.virtual_memory().free
        return event_dict


    def track_disk_stats(self, _, __, event_dict: dict) -> dict:
        """ Logs the following DiskIO usage statistics of the system:
            1) disk_read_counter (int): No. of disk reads
            2) disk_write_counter (int): No. of disk writes
            3) disk_read_bytes (int): No. of bytes read
            4) disk_write_bytes (int): No. of bytes wrote

        Args:
            event_dict (dict): Logging metadata accumulated
        Returns:
            Updated event metadata (dict)
        """
        event_dict['disk_read_counter'] = psutil.disk_io_counters().read_count
        event_dict['disk_write_counter'] = psutil.disk_io_counters().write_count
        event_dict['disk_read_bytes'] = psutil.disk_io_counters().read_bytes
        event_dict['disk_write_bytes'] = psutil.disk_io_counters().write_bytes
        return event_dict


    def track_network_stats(self, _, __, event_dict: dict) -> dict:
        """ Logs the following NetworkIO usage statistics of the system:
            1) net_bytes_sent (int): No. of bytes sent from the network
            2) net_bytes_recv (int): No. of bytes sent to the network
            3) net_packets_sent (int): No. of network packets sent 
            4) net_packets_recv (int): No. of network packets received

        Args:
            event_dict (dict): Logging metadata accumulated
        Returns:
            Updated event metadata (dict)
        """
        event_dict['net_bytes_sent'] = psutil.net_io_counters().bytes_sent
        event_dict['net_bytes_recv'] = psutil.net_io_counters().bytes_recv
        event_dict['net_packets_sent'] = psutil.net_io_counters().packets_sent
        event_dict['net_packets_recv'] = psutil.net_io_counters().packets_recv
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
        kwargs['extra']['function'] = ""

        return args, kwargs
