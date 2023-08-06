#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################


# add 'list' type to cfgparse options

from cfgparse import Option
import cfgparse

def convert_list(self, value):
    try:
        return eval(value), None
    except:
        return None, 'Can not convert %r' % value 
Option.conversions['list'] = convert_list

def convert_bool(self, value):
    try:
        return eval(value), None
    except:
        return None, 'Can not convert %r' % value 
Option.conversions['bool'] = convert_bool


