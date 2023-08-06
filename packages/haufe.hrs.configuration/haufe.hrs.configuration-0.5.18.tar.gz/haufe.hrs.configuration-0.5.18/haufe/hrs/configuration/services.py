#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################

# pre-defined services

try:
    import pyinotify
    watch = True
except ImportError:
    watch = False

from service import ConfigurationServiceFactory as factory
CentralConfigurationService = factory(watch=False)
CentralConfigurationServiceSupervised = factory(watch=watch)
