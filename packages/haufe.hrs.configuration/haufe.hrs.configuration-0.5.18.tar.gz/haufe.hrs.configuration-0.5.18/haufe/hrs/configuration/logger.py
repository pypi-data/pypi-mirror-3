#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################

"""
A simple logger for haufe.hrs.configuration
"""

import os
import logging
import logging.handlers

def getLogger():

    if os.environ.has_key('INSTANCE_HOME'): 
        # ZOPE
        return logging.getLogger('haufe.hrs.configuration')
    else:
        LOG = logging.getLogger()
        LOG.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)-6s %(message)s')
        streamhandler = logging.StreamHandler()
        streamhandler.setFormatter(formatter)
        LOG.addHandler(streamhandler)
        return LOG

