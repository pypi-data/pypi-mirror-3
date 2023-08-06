#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################


if __name__ == '__main__':
    from haufe.hrs.configuration import generateParser, OptionLookup

    import logging
    LOG = logging.getLogger()
    parser = generateParser('example/model', LOG)
    parser.add_file('example/sample_config/all-in-one.ini')

    opts = parser.parse()
    from pprint import pprint
    pprint(opts.__dict__)

    OL = OptionLookup(opts, 'cms')
    print OL.get('adb2version')
    print OL.has('foobar')

    OL = OptionLookup(opts)
    print OL.get('cms.adb2version')
    print OL.has('cms.adb2version')
   
