#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################


if __name__ == '__main__':
    from haufe.hrs.configuration import ConfigurationService

    service = ConfigurationService(watch=True)
    service.registerModel('example/model')
    service.loadConfiguration('example/sample_config/all-in-one.ini')
    service.start()

    # keep artificially the main thread alive forever
    while True:
        print service.getConfiguration()
        try:
            import time
            time.sleep(5)
        except KeyboardInterrupt:
            # ...until c^c signal
            print 'stop monitoring...'
            # stop monitoring
            if service.notifier:
                service.shutdown()
            print 'done'
            break
        except Exception, err:
            # otherwise keep on looping
            print err
