#!python
from . import Client, Authorization, Fault, ClientOptions, Synthetic, User, Endpoint
from . import printFault, pdb, ApplyCompressionChannel, CompressIfWorthIt

# Front End.
def openClient(setup, options, ns):
    if options.support_dir:
        # Run in 'support mode'
        assert options.username

        user = User(options.username, options.secret_key)
        group = user[options.support_dir]

        ns['user'] = user
        ns['group'] = group

        setup.client

    elif options.endpoint:
        # Connect to a specific service using endpoint-url form.
        assert options.username

        user = User(options.username, options.secret_key)
        endpoint = Endpoint.Parse(options.endpoint)
        api = endpoint.open(user)

        ns['user'] = user
        ns['endpoint'] = endpoint
        ns['api'] = api

        setup.client

    elif options.service_partner_name:
        # Use the service-partner-lookup on the service manager.
        from pentacle.bus.partners import OpenPartneredClient
        setup.byline = 'SERVICE-MANAGER FAULT'
        setup.client = OpenPartneredClient(options.service_partner_name,
                                           **optionalArgs(options, 'username', 'port'))

    else:
        # Straight connect:
        print 'Connecting to [%s:%d]...' % (options.address, options.port)
        client = Client.Open(options.address, options.port)

        ApplyCompressionChannel(client.dataChannel,
                                options.compression_level,
                                options.compression_threshold)

        username = options.username
        if username:
            print 'Logging in %s...' % username
            auth = Authorization(username, options.secret_key)
            auth.Authenticate(client)

        setup.client = client

def setupClient(setup, options, ns):
    # Setup interactive namespace.
    import pentacle
    import sys

    client = setup.client
    ns['peer'] = client
    ns['client'] = client
    ns['call'] = client.call if client is not None else None
    ns['options'] = options
    ns['pentacle'] = pentacle
    ns['sys'] = sys
    ns['g'] = Synthetic(**globals())

    # Note: Some of these options are incompatible with --support-dir and --endpoint
    if options.open_system_api:
        system = client.api.open('System::Debugging')
        e = system.invoke.evaluate

        ns['system'] = system
        ns['e'] = e = system.invoke.evaluate
        ns['x'] = x = system.invoke.execute

        if options.enable_timing_tests:
            def testTiming(n = 2017):
                return len(e('"A" * %d' % n))

            def timeIt(n, number, repeat = 1):
                from timeit import repeat as tFunc
                return tFunc(lambda:testTiming(n),
                             number = number,
                             repeat = repeat)

            ns['tt'] = testTiming
            ns['ti'] = timeIt

    elif options.open_spline_api:
        def PrintUptime(svcmgr):
            print 'Uptime: %(running_duration)s' % svcmgr.invoke.GetManagerStats()

        from ..bus import ServiceManagerName
        ns['spline'] = client.api.open(ServiceManagerName)
        ns['PrintUptime'] = PrintUptime

    elif options.open_api:
        (variable, name) = options.open_api.split(':', 1)
        ns[variable] = client.api.open(name)

def optionalArgs(options, *names):
    kwd = {}
    for n in names:
        value = getattr(options, n, None)
        if value is not None:
            kwd[n] = value

    return kwd

def main(argv = None):
    (options, args) = ClientOptions.parseCmdln(argv)
    if options.debug:
        pdb.set_trace()

    ns = dict()
    setup = Synthetic(byline = 'SERVER FAULT',
                      client = None)

    try:
        # Start connection.
        openClient(setup, options, ns)

        # Handle Session.
        ##    if options.api_test:
        ##        testApi(client)

        if options.examine:
            try: import readline
            except ImportError:
                pass

            # Setup interactive namespace.
            setupClient(setup, options, ns)

            from code import InteractiveConsole as IC
            ic = IC(locals = ns)
            ic.interact()

        if options.quit:
            print 'Quitting Application...'
            setup.client.call.stopApplication()

    except Fault, fault:
        printFault(fault, cause = True, byline = setup.byline)
    except KeyboardInterrupt:
        print 'Console Break'

##    def testApi(client):
##        with client.api('API::Management') as api:
##            print 'Loading ClockService...'
##            print api.loadNewServiceApi('pentacle.application.ClockService').NAME
##
##            print 'Loading SystemDebug...'
##            print api.loadNewServiceApi('pentacle.application.SystemDebug').NAME
##
##            print 'Loading ObjectDirectory...'
##            print api.loadNewServiceApi('pentacle.application.ObjectDirectory').NAME
##
##            print 'Loading AuxiliaryApi...'
##            print api.loadNewServiceApi('pentacle.storage.StorageManagement.AuxiliaryApi').NAME
##
##        print 'Start Ticking...'
##        with client.api('ClockService::API') as clock:
##            clock.setClockTicking(10000)
##            print 'Current Clock Time:', clock.getClockTime()
##
##        print 'Testing Debug...'
##        # client.debug = 1
##        with client.api('System::Debugging') as debug:
##            try: debug.fail()
##            except Fault, fault:
##                printFault(fault)
##
##        print 'Testing Object Directory...'
##        with client.api('System::Directory') as directory:
##            N = directory.newObject
##            directory.setObject('Feature', N(Aspect = N(Scope = N(Name = 'A System Feature Aspect Scope'))))
##
##            print directory.getObject('Feature').Aspect.Scope.Name
##
##        print 'Testing Auxiliary Storage'
##        with client.api('Storage::Aux') as aux:
##            db = aux.buildAuxiliaryStore(buildCmdln(db_path = '~/.pentacle/application.db'))
##            user = aux.lookupUnitAccess('UserStorage')
##            fraun = user.Open(db.application, 'fraun')
##
##            # change user-fraun
##            print dict(fraun.unit.unit.items())

if __name__ == '__main__':
    main()
