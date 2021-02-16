#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import abc

# Libs


# Custom


##################
# Configurations #
##################


###########################################
# Logging Abstract Class - AbstractLogger #
###########################################

class AbstractLogger(abc.ABC):

    @abc.abstractmethod
    def initialise(self):
        """ Creates an operation payload to be sent to a remote queue for 
            linearising jobs for a Synergos cluster
        """
        pass
