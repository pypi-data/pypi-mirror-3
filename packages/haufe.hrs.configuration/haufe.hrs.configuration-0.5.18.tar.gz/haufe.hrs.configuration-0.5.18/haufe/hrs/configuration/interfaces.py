#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################

from zope.interface import Interface


class IConfigurationService(Interface):
    """ A global configuration service for configurations based
        on the cfgparse module.
    """

    def __init__(watch=False, start_notification=False):
        """ Initialize the configuration """

    def registerModel(filename):
        """ Register a configuration model with the service """

    def loadConfiguration(filename):
        """ Load a configuration file matching one of the registered
            models into the service 
        """

    def reload():
        """ Reload all registered models and configuration files """

    def get(name, domain=None):
        """ Return the value of a configuration option for a given key.
            'name' is either a full dotted name or added to a dotted
             domain.
        """

    def getConfiguration():
        """ Return all configuration items as dict """

    def getConfigurationForDomain(domain):
        """ Return all configuration items as dict for a given domain"""

    def start():
        """ Start notification thread """
    def shutdown():
        """ Perform actions upon system shutdown """


class IConfigurationChangedEvent(Interface):
    """ Event send upon configuration changes """
