#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import logging
import sys
from typing import Callable, List, Tuple

# Lib
import graypy
import structlog

# Custom
from .abstract import AbstractLogger
from .config import LOGGING_FORMAT
from .utils import StructlogUtils

##################
# Configurations #
##################

# Monkey patching structlog to support 'notset' level
structlog.stdlib._LEVEL_TO_NAME[logging.NOTSET] = 'notset'

########################################
# Organisation Base Class - RootLogger #
########################################

class RootLogger(AbstractLogger):
    """
    Initialises configuration for setting up a logging server using Structlog.
    Custom filters can be applied for more meaningfully/context-driven logs.
    However, such filter functions declared MUST take on the following 
    parameter signature, in accordance to Structlog standards:

        def <function_name>(logger, log_method, event_dict):
            ...
            return event_dict
        
    More details on this can be found at:
    https://www.structlog.org/en/stable/processors.html?highlight=filtering#filtering

    Attributes:
        logger_name (str): Logger ID by name e.g. TTP, worker_1, worker_2
        logging_variant: Type of logging to use. There are 2 main options:
            1. "basic" -> basic logging, 
            2. "graylog" -> logging to graylog server
            Default: "basic"
        server (str): Host address of the logging server e.g. 127.0.0.1 
            to be specified if logging_variant != 'basic'. Default: None
        port (int): Port of the logging server e.g. 9000 for graylog 
            to be specified if logging_variant != 'basic'. Default: None
        logging_level (int): logging.DEBUG, logging.INFO, logging.WARNING 
            etc. Default: logging.INFO (i.e. 20)
        debugging_fields (bool): Toggles adding debug fields from the log 
            record into the GELF logs to be sent to Graylog. Default: False
        filter_functions (list(callable)): List of callables to be applied for
            filtering. Default: []
        censor_keys (list(str)): Censor any logs with the specified keys 
            with the value "*CENSORED*". This protects user-specific 
            secrets. Default: []
        file_path (str): File location where logging is called
    """
    def __init__(
        self, 
        logger_name: str = "std_log", 
        logging_variant: str = "basic",
        server: str = None,
        port: int = None, 
        logging_level: int = logging.INFO,
        debugging_fields: bool = False,
        filter_functions: List[str] = [], 
        censor_keys: list = [],
        file_path: str = ""
    ):
        # General attributes
        # e.g. misc attibutes unique to problem
        self.logger_name = logger_name
        self.logging_level = logging_level
        self.logging_variant = logging_variant
        self.debugging_fields = debugging_fields
        self.filter_functions = filter_functions
        
        # Network attributes
        # e.g. server IP and/or port number
        self.server = server
        self.port = port

        # Data attributes
        # e.g participant_id/run_id in specific format
        self.censor_keys = censor_keys
        self.synlog = None

        # Optimisation attributes
        # e.g multiprocess/asyncio if necessary for optimisation


        # Export Attributes 
        # e.g. any artifacts that are going to be exported eg Records
        self.file_path = file_path

    ############
    # Checkers #
    ############

    def is_initialised(self) -> bool:
        """ Checks if logger has already been initialised to enforce 
            idempotence

        Returns:
            State (bool)
        """
        return self.synlog is not None

    ###########
    # Helpers #
    ###########

    def _configure_processors(self):
        """ Assembles a list of processors to be use as filters during logging

        Returns:
            Structlog Processes (list(callable))
        """
        structlog_utils = StructlogUtils(
            censor_keys=self.censor_keys,
            file_path=self.file_path
        )
        RENDER_MAP = {
            'basic': structlog.processors.JSONRenderer(indent=1), # msg as dict
            'graylog': structlog_utils.graypy_structlog_processor,
            'test': structlog.testing.LogCapture()
        }
        censor_logging = structlog_utils.censor_logging
        get_file_path = structlog_utils.get_file_path
        add_timestamp = structlog_utils.add_timestamp
        logging_renderer = RENDER_MAP[self.logging_variant]

        ###########################
        # Implementation Footnote #
        ###########################

        # [Cause]
        # In Structlog, a processor is a callable object that executes a 
        # certain action upon a given event_dict input, and returns an 
        # augmented event_dict as output. As such, a Structlog processor chain
        # is formed and parsed in order and sequentially. 
        #  
        # eg.
        # wrapped_logger.msg(
        #     f4(
        #         wrapped_logger, "msg",
        #         f3(
        #             wrapped_logger, "msg",
        #             f2(
        #                 wrapped_logger, "msg",
        #                 f1(
        #                     wrapped_logger, "msg", 
        #                     {"event": "some_event", "x": 42, "y": 23}
        #                 )
        #             )
        #         )
        #     )
        # )
        #
        # More details on this can be found at:
        # https://www.structlog.org/en/stable/processors.html?highlight=chain

        # [Problems]
        # However, for the event_dict to be usable in PyGelf, it has to be
        # re-casted in a different form, and expressed as args and kwargs. This
        # means that the custom processor handling PyGelf compatibility will
        # have an asymmetric output w.r.t other processors, and thus cannot be
        # used as inputs to a subsequent processor downstream. Doing so results
        # in `TypeError: 'str' object does not support item assignment`.

        # [Solution]
        # Ensure that logging renderer is always the last element of the 
        # processor list (i.e. last unit of the processor chain).

        processors = [
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_log_level_number,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
            structlog.processors.StackInfoRenderer(), 
            structlog.processors.UnicodeDecoder(),
            *self.filter_functions, # apply custom filters
            get_file_path,
            censor_logging,         # censor sensitive log messages - 2nd last!
            logging_renderer        # IMPT - MUST BE LAST!
        ]

        return processors

    ##################
    # Core Functions #
    ##################

    def initialise(self, **kwargs) -> structlog._config.BoundLoggerLazyProxy:
        """ initialise configuration for structlog & pygelf for logging messages
            
            e.g. logging a debug message "hello" to graylog server
            >>> logger.debug("hello")
            {
                "event": "hello",
                "logger": "stdlog",
                "level": "debug",
                "timestamp": "2020-10-21T05:09:10.868747Z"
            }

        Args:
            kwargs: Miscellaneous values for compatibility
        Returns:
            syn_logger: A structlog + Pygelf logger
        """
        core_logger = logging.getLogger(self.logger_name) 
        core_logger.setLevel(level=self.logging_level)

        if not self.is_initialised():

            ###########################
            # Implementation Footnote #
            ###########################

            # [Cause]
            # When adding handlers to logging.Logger, handlers get appended to an
            # existing pool of handlers.

            # [Problems]
            # Blindly appending handlers will result in multiple handlers cached,
            # which results in duplicated logging entries. Calling `.initialise()`
            # thus fails to be idempotent.

            # [Solution]
            # Clear all handlers under logger first before initialisation.

            if core_logger.hasHandlers():
                core_logger.handlers.clear()

            if self.logging_variant == 'graylog':
                
                # `debugging_fields` toggle default debugging fields such as 
                # "function", "pid", "process_name", "thread_name", etc.
                handler = graypy.GELFTCPHandler(
                    host=self.server, 
                    port=self.port,
                    debugging_fields=self.debugging_fields, 
                    facility="", 
                    level_names=True
                )

            else:
                # handler = logging.StreamHandler(stream=sys.stdout)
                handler = logging.NullHandler()

            format = LOGGING_FORMAT.safe_substitute({'name': self.logger_name})
            formatter = logging.Formatter(format)
            handler.setFormatter(formatter)
            core_logger.addHandler(handler) 

        # Allows for dynamic reconfiguration for filtering processors
        processors = self._configure_processors()
        sys_logger = structlog.wrap_logger(
            logger=core_logger,
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            cache_logger_on_first_use=True
        )

        self.synlog = sys_logger

        return self.synlog

