#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
from string import Template

# Lib


# Custom


##################
# Configurations #
##################

# Default logger prefixes to faciliate role detection
DIRECTOR_NAME_TEMPLATE = Template("DIR_$name")
TTP_NAME_TEMPLATE = Template("TTP_$name")
WORKER_NAME_TEMPLATE = Template("WKR_$name")
SYSMETRICS_NAME_TEMPLATE = Template("SYS_$name")


# Default logging ports to be created in the graylog server. All logs from 
# multiple target types will be matched to a single port i.e. all workers nodes
# will publish to the allocated WORKER_PORT.
SYSMETRICS_PORT = 9100
DIRECTOR_PORT = 9200
TTP_PORT = 9300
WORKER_PORT = 9400
