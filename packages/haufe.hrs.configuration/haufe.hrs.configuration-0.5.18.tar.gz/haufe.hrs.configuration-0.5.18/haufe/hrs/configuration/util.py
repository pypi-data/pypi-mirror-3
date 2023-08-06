#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################


import os
import cfgparse
import ConfigParser

class OptionNotSetMarker(object):
    pass

DEFAULT_MARKER = OptionNotSetMarker

class MyConfigParser(ConfigParser.RawConfigParser):
    """ A config parser preserving lower-case spelling for keys """

    def optionxform(self, s):
        return s

def generateParser(name, LOG=None, parser=None):
    """ Generate a configuration parser for all modules described.
        'name' is either a directory containing model files (must
        end with .ini) or a single model file (also with .ini sufix).
        A new cfg.ConfigParser instance will be created unless
        specified as 'parser' parameter.
    """

    if os.path.isfile(name):
        filenames = [name]
    elif os.path.isdir(name):
        filenames = list()
        for n in os.listdir(name):
            filenames.append(os.path.join(name, n))
    else:
        raise ValueError('%s is neither a file nor a directory' % name)

    if parser is None:
        parser = cfgparse.ConfigParser()
    for filename in filenames:
        parseModel(filename, parser,  LOG)
    return parser


def parseModel(filename, parser, LOG=None):
    """ Parse a model specified as an ini-style configuration file """

    filename = expand_full(filename)

    if LOG:
        LOG.debug('Processing: %s' % filename)

    if not os.path.exists(filename):
        raise IOError('Model file %s does not exist' % filename)

    CP = MyConfigParser()
    CP.optionxfrom = str
    CP.read([filename])
    for section in CP.sections():
        if LOG:
            LOG.debug('  Section: %s' % section)
        for option in CP.options(section):

            value = CP.get(section, option).strip()
            default = DEFAULT_MARKER
            type = 'string'
            if value:
                if ',' in value:
                    type, other = value.split(',', 1)
                else:
                    type, other = value, ''

                if 'default' in other:
                    default = eval(other.split('=', 1)[1])

            dest = '%s.%s' % (section, option)
            parser.add_option(option, 
                              type=type, 
                              default=default, 
                              dest=dest,
                              keys=section)


class OptionLookup(object):
    """ Lookup values of configurations by a dotted name """

    def __init__(self, opts, domain=None):
        self.opts = opts
        self.domain = domain
        # Optimization: has() should have 0(1) running time
        self.known_opts = dict()
        if opts is not None:
            for k in self.opts.__dict__.keys():
                if '.' in k:
                    self.known_opts[k] = True

    def get(self, name, expand_env=False):

        if self.domain and not name.startswith(self.domain):
            name = '%s.%s' % (self.domain, name)
        try:
            v = getattr(self.opts, name)
        except AttributeError:
            raise KeyError('Unknown key: %s' % name)

        if v is DEFAULT_MARKER:
            raise KeyError('Neither a default nor a configuration ' + 
                           'found for Key: %s' % name)

        if expand_env:
            return os.path.expandvars(v)
        else:
            return v

    def has(self, name):
        if self.domain and not name.startswith(self.domain):
            name = '%s.%s' % (self.domain, name)
        return self.known_opts.has_key(name)

def expand_full(filename):
    """ Expand a file - either to its absolute path
        or expand a leading environment variable.
    """
    if filename.startswith('$'):
        return os.path.expandvars(filename)
    return os.path.abspath(filename)
