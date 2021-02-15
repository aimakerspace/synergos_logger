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
from .utils import StructlogUtils

##################
# Configurations #
##################


########################################
# Organisation Base Class - RootLogger #
########################################

class RootLogger(AbstractLogger):
    """
    initialise configuration for setting up a logging server using structlog

    Attributes:
        server (str): Host address of the logging server e.g. 127.0.0.1
        port (int): Port of the logging server e.g. 9000 for graylog
        logger_name (str): Logger ID by name e.g. TTP, worker_1, worker_2
        logging_level (int): logging.DEBUG, logging.INFO, logging.WARNING etc.
        logging_variant: Type of logging to use. There are 2 main options:
            1. "basic" -> basic logging, 
            2. "graylog" -> logging to graylog server
            Default: "basic"
        debugging_fields (bool): Toggles adding debug fields from the log
            record into the GELF logs to be sent to Graylog
        filter_functions (list(callable)): List of Filter modules to apply on
            logging records
        file_path (str): File location where logging is called
    """
    def __init__(
        self, 
        server: str,
        port: int, 
        logger_name: str = "std_log", 
        logging_level: int = logging.INFO, 
        logging_variant: str = "graylog",
        debugging_fields: bool = False,
        filter_functions: List[str] = [], 
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
        self.synlog = None
        self.templog = None

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
        return self.synlog and self.templog

    ###########
    # Helpers #
    ###########
    
    def apply_filters(
        self, 
        logger: structlog.BoundLogger,
        filter_functions: List[Callable]
    ) -> None:
        """ Apply filters on a specified logger

        Args:
            logger (logging.RootLogger): A logger object
            filter_functions (list(Callable)): List of custom filter classes
        """
        for filter in filter_functions:
            logger.addFilter(filter())

    ##################
    # Core Functions #
    ##################

    def initialise(
        self,
        censor_keys: list = [],
        **kwargs
    ) -> Tuple[structlog._config.BoundLoggerLazyProxy, structlog.BoundLogger]:
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
            censor_keys (list(str)): Censor any logs with the specified keys with 
                the value "*CENSORED*". This protects user-specific secrets.
            kwargs: 
        Returns:
            syn_logger: A structlog + Pygelf logger
            logger: base logger class
        """
        if not self.is_initialised():
            structlogUtils = StructlogUtils(
                censor_keys=censor_keys, 
                file_path=self.file_path
            )
            censor_logging = structlogUtils.censor_logging
            get_file_path = structlogUtils.get_file_path
            graypy_structlog_processor = structlogUtils.graypy_structlog_processor
            logging_variant = (
                graypy_structlog_processor
                if self.logging_variant == "graylog"
                else structlog.processors.JSONRenderer(indent=1) # msg as dict
            )

            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    # structlog.stdlib.add_log_level_number,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
                    structlog.processors.StackInfoRenderer(), 
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    # structlog.stdlib.render_to_log_kwargs,
                    censor_logging, # censoring sensitive log messages
                    get_file_path,
                    logging_variant
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )

            logging.basicConfig(
                format="%(message)s",
                stream=sys.stdout,
                level=self.logging_level # default
            )

            # Logger templates for basic logging and structlog MUST tally
            logger = logging.getLogger(self.logger_name) 

            if self.logging_variant == 'graylog':
                
                # Disable default debugging fields such as "function", "pid", 
                # "process_name", "thread_name"
                handler = graypy.GELFTCPHandler(
                    host=self.server, 
                    port=self.port,
                    debugging_fields=self.debugging_fields, 
                    facility="", 
                    level_names=True
                )
                logger.addHandler(handler)

            self.apply_filters(logger, self.filter_functions)

            self.synlog = structlog.get_logger(self.logger_name)
            self.templog = logger

        return self.synlog, self.templog

