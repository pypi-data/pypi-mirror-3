#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################


"""'
ZCML directives for haufe.hrs.configuration
"""

import os

from zope.interface import Interface
from zope.schema import TextLine 
from services import CentralConfigurationService, \
                     CentralConfigurationServiceSupervised

class IModelDefinition(Interface):
    """ Used for defining a model"""

    model = TextLine(
        title=u"Directory name containing model files or a single model file",
        description=u"Directory name containing model files or a single model file",
        default=u"",
        required=True)

class IConfigurationFile(Interface):
    """ Used for defining a configuration file"""

    configuration = TextLine(
        title=u"Directory name containing configuration files or a single configuration filename",
        description=u"Directory name containing configuration files or a single configuration filename",
        default=u"",
        required=True)


def registerModel(_context, model):
    context_dirname = os.path.dirname(_context.info.file)
    model_cfg = os.path.join(context_dirname, model)
    if os.path.exists(model_cfg):
        model = model_cfg
    CentralConfigurationService.registerModel(model)
    CentralConfigurationServiceSupervised.registerModel(model)

def registerConfiguration(_context, configuration):
    # str() because cfgparse.add_file performs an explicit check
    # for <str> type
    context_dirname = os.path.dirname(_context.info.file)
    possible_cfg = os.path.join(context_dirname, configuration)
    if os.path.exists(possible_cfg):
        configuration = possible_cfg

    CentralConfigurationService.loadConfiguration(str(configuration))
    CentralConfigurationServiceSupervised.loadConfiguration(str(configuration))
