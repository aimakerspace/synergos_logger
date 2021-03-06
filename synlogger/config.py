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

LOGGING_FORMAT = Template("[$name] %(message)s")

# Default string used to censor sensitive values
CENSOR = "*CENSORED*"

# Default logger prefixes to faciliate role detection
DIRECTOR_PREFIX = "DIR"
TTP_PREFIX = "TTP"
WORKER_PREFIX = "WKR"
SYSMETRICS_PREFIX = "SYS"

# Default logger templates to faciliate role detection
DIRECTOR_NAME_TEMPLATE = Template(f"{DIRECTOR_PREFIX}_$name")
TTP_NAME_TEMPLATE = Template(f"{TTP_PREFIX}_$name")
WORKER_NAME_TEMPLATE = Template(f"{WORKER_PREFIX}_$name")
SYSMETRICS_NAME_TEMPLATE = Template(f"{SYSMETRICS_PREFIX}_$name")

# Default logging ports to be created in the graylog server. All logs from 
# multiple target types will be matched to a single port i.e. all workers nodes
# will publish to the allocated WORKER_PORT.
SYSMETRICS_PORT = 9100
DIRECTOR_PORT = 9200
TTP_PORT = 9300
WORKER_PORT = 9400
