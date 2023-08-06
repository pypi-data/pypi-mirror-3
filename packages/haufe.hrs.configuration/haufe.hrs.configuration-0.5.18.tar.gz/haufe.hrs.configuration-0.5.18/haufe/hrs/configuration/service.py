#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################


"""
The central configuration service
"""

import os
import time
import cfgparse
import zope.event
import threading
from sets import Set
from decorator import synchronized
from zope.component.interfaces import IFactory
from zope.interface import implements, implementedBy

import util
from logger import getLogger
from interfaces import IConfigurationService, IConfigurationChangedEvent

try:
    from pyinotify import  ThreadedNotifier, WatchManager, EventsCodes
    from pyinotify import ProcessEvent
    have_pyinotify = True
except ImportError:
    have_pyinotify = False


LOG = getLogger()

class ConfigurationService(object):

    implements(IConfigurationService)

    lock = threading.Lock()

    def __init__(self, watch=False, start_notification=False):
        self._clear()
        self.watch = watch # Watch configuration file changes
        self.parser = None
        self.opts = None

        # start notification service
        self.notify_wm = None
        self.notifier = None
        self.notifier_started = False
        if watch and not have_pyinotify:
            raise RuntimeError('The "pyinotify" module must be installed '
                               'for using watch=True')
        if self.watch and have_pyinotify:
            self.notify_mask = ( EventsCodes.IN_MODIFY 
                               | EventsCodes.IN_DELETE 
                               | EventsCodes.IN_ATTRIB 
                               | EventsCodes.IN_CREATE 
                               | EventsCodes.IN_MOVE_SELF)
            self.notify_wm = WatchManager()
            event_handler = NotificationEvent()
            event_handler.setService(self) # needed for callback
            self.notifier = ThreadedNotifier(self.notify_wm, event_handler)
            if start_notification:
                self.start()

    @synchronized(lock)
    def _clear(self):
        self.parser = cfgparse.ConfigParser()
        self.model_files = list()
        self.configuration_files = list()

    def registerModel(self, filename):
        """ Register a configuration model with the service """
        filename = util.expand_full(filename)
        if not os.path.exists(filename):
            raise IOError('Model file %s does not exist' % filename)
        if not filename in self.model_files:
            LOG.debug('register model: %s' % filename)
            self.model_files.append(filename)
        self.reload()

    def loadConfiguration(self, filename):
        """ Load a configuration file matching one of the registered
            models into the service 
        """
        filename = util.expand_full(filename)
        if not os.path.exists(filename):
            raise IOError('Configuration file %s does not exist' % filename)
        if not filename in self.configuration_files:
            LOG.debug('loading configuration: %s' % filename)
            self.configuration_files.append(filename)
        self.reload()

        if self.watch and have_pyinotify:
            # watch path for events handled by notification mask.
            LOG.debug('watching %s' % filename)
            self.notify_wm.add_watch(filename, self.notify_mask)

    @synchronized(lock)
    def reload(self):
        try:
            self._reload()
        except Exception, e:
            LOG.error('Reloading the configuration failed', exc_info=True)
            return

        if self.watch and have_pyinotify:
            # re-add watches
            for filename in self.configuration_files:
                self.notify_wm.add_watch(filename, self.notify_mask)

        zope.event.notify(ConfigurationChangedEvent(self.getConfiguration()))

    def _reload(self):
        """ Reload models and configuration """

        LOG.debug('Reloading configuration')
        # create a new parser first (w/o overriding the original one)
        parser = cfgparse.ConfigParser()

        # re-add model files
        for filename in self.model_files:
            util.generateParser(filename, parser=parser)

        # add configuration files
        for filename in self.configuration_files:
            parser.add_file(cfgfile=filename, content=None)

        opts = parser.parse()
        self.opts = opts
        self.parser = parser

    ############################################################
    # Notifier thread handling
    ############################################################

    def start(self):
        """ Start notification thread """

        if self.notifier is not None:
            self.notifier.start()
            self.notifier_started = True
        else:
            raise RuntimeError('Notification thread can not be started')

    def shutdown(self):
        """ Explict shutdown of the notifier thread (basically required for
            Zope integration).
        """

        if self.notifier is not None:
            if not self.notifier_started:
                raise RuntimeError('Notifier thread is not started')
            self.notifier.stop()
            self.notifier_started = False

    ############################################################
    # Option/configuration lookup
    ############################################################

    def get(self, name, domain=None):
        """ Return the value of a configuration option for a given key.
            'name' is either a full dotted name or added to a dotted
             domain.
        """
        OL = util.OptionLookup(self.opts, domain=domain)
        return OL.get(name)

    def getConfiguration(self):
        """ Return all configuration entries as dict """
        return self.opts.__dict__.copy() 

    def getConfigurationForDomain(self, domain):
        """ Return all configuration entries as dict for a given domain"""
        opts = self.getConfiguration().copy()
        for opt in opts.keys():
            opt_domain, opt_key = opt.rsplit('.' , 1)
            if opt_domain != domain:
                del opts[opt]
        return opts


class ConfigurationServiceFactory(object):
    """ Factory for the configuration service """
    implements(IFactory)

    def __call__(self, watch=False):
        return ConfigurationService(watch=watch)

    def getInterfaces(self):
        return implementedBy(ConfigurationService)

ConfigurationServiceFactory = ConfigurationServiceFactory()

#######################################
# pyinotify handler for events
#######################################

if have_pyinotify:
    class NotificationEvent(ProcessEvent):

        service = None

        def setService(self, service):
            self.service = service

        def process_default(self, event):
            LOG.info('Configuration file changed: %s' % event.path)
            time.sleep(5)
            self.service.reload()


class ConfigurationChangedEvent(object):
    """ Event indicating that the main configuration has been reloaded """

    implements(IConfigurationChangedEvent)

    def __init__(self, configuration):
        self.configuration = configuration
