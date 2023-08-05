
                          * Pentacle *

                  Object-Oriented, Peer-to-Peer
                  Remote Object Instrumentation


    ~ What is Pentacle?

      Pentacle is an embeddable communication module that enables
      remote access to objects and method calls, with a focus on
      clean framework and aspect design from application code to
      command-line.

      The primary goal is to allow very-high-level access to larger
      systems, to conceptualize complete systems as objects with
      external interfaces that are accessible to even the minute
      aspects of program instruction.  Every aspect is cohesive so
      that it can be lifted out of the main application for custom
      interoperation between peers.

      It's architecture is simple, open and sleak, which differentiates
      it from other remoting libraries while still providing enterprise-
      level, scalable design.  Another goal is to provide full-duplex
      (two-way) remoting between client and server peers based on the
      streamed-socket network.

      Also includes a service manager and system bus for transparent
      coordination of partnered applications (Spline).

    ~ What is its status?

      Alpha stage, because of the rapid development timeframe, still
      containing bugs and requires lots of unit testing.  The API is
      settling in but expect changes.  Encoding format could be more
      condensed.  Still some debugging artifacts and a mess of notes.

      Consider for non-production use and in controlled environments.
      Remote access libraries require lots of security testing.

    ~ What are the requirements?

      Pentacle is developed in python 2.7, but could be ported easily
      to Python 3 and above.  It requires only standard libraries that
      come with every installation, mainly asyncore and the config-parser.

      Requires a POSIX-style networking stack (TCP/IP) and the ability
      to multithread.  The internal database uses the 'shelve' module.
      Some components use 'collections' module, for convenience.

      The Falcon Web Management service (optional Spline partner) is
      built on Django framework (1.x series).

      Documentation requires Sphinx and/or Epydoc.

    ~ How do I install it?

      Use the setuptools setup.py script to plop it in your site-packages
      directory:

      $ python setup.py install

      Place and configure the partner INI files (for example, spline.cfg)
      Place and configure any support directories.

      The Falcon Web Management partner utilizes Django's project settings,
      which has a private key.  It is currently unused, but could be made
      unique.

    ~ How do I start it?

      The architecture supports a service manager for coordinating running
      components on the system.  This could be run by the system cron/initrc,
      Windows Service or scheduled task:

      $ scripts/spline.sh &

      But that's for system administrators.  Developers will want to get into
      the code.

      Pentacle uses a 'named-service partner' directory system that is
      ultimately addressable using a URL-like format (called an endpoint).

      $ python -m pentacle.client.cli --username=Operation --secret-key=... \
                  --endpoint=spline:localhost@westmetal/document/browser \
                  --examine

      $ python -m pentacle.client.cli --support-dir=~/.my-services-configuration \
                                      --username=...
      >>> group.docweb.openUrl('...')
      >>> w = group.database.newWidget(...)

      Clients can store their application configuration sets on the filesystem:
      (can also be configured programmatically: see pentacle.client.support)
      ~/.my-services-configuration/database.cfg:
          [Service]
          partner-name: penobscotrobotics.us/Pentacle/Database
          service-api: PenobscotRobotics[Registry::Active]

      ~/.my-services-configuration/docweb.cfg:
          [Service]
          partner-name: Westmetal Documents
          service-api: @westmetal/document/browser

      Connecting directly:

      $ python -m pentacle --host=penobscotrobotics.us --port=2150 --examine
      >>> print client.call.Identify()
      PentacleApp/0.1

      >>> client = pentacle.Client.Open('localhost', 7050)
      >>> client.call.login('Operator', 'Secret*Password')
      >>> docWeb = client.api.open('@westmetal/document/browser')
      >>> docWeb.invoke.openUrl('http://news.penobscotrobotics.us/today')
      >>> docWeb.close()

      There is also a significant amount of layering of client object interfaces
      to tie it all together:

      >>> with pentacle.User('Operator', 'Secret*Password') as user:
      ...   with user.Grouping('~/.my-services-configuration').database as db:
      ...     db.newWidget(1, 'Field-Value', 0.9, dict(supplement = [complex(5, 1)]))

      The Spline service manager is engineered to keep your application components
      in separate process compartments, but always running according to uptime or
      schedule requirements.

      # org.acme.services.runtime
      class MyServiceAPI(pentacle.architecture.ServiceBase):
          NAME = 'Organization[System::Objects::API]'

          def Activate(self, apiMgr):
              # Configure the service instance.  This method is not remotable
              # (only based on current implementation: this will eventually change
              # requiring explicit exposure of api methods).
              acme = apiMgr.application.config.ConfigSet('AcmeWidgets')
              self.widgets = shelve.open(acme.widget_file_path)

          def getWidget(self, name):
              return self.widgets[name]
          def newWidget(self, name, **values):
              w = self.widgets[name] = Widget(**values)
              w.name = name
              return w

          def decommission(self, widget):
              # Of course this requires a widget object to be passed back using
              # data-space entity proxying.
              del self.widgets[widget.name]

      Now, configure the new API to function as a named-service partner, and use
      the service manager to manage its availability.  Alternatively, embed a service
      application right in your program:

      >>> app = pentacle.Application.Boot(['--config-file', '...']) # Optional
      >>> app.api.loadServiceApiObject(org.acme.services.runtime.MyServiceAPI)
      >>> pentacle.runtime.nth(app.run) # Shorthand for running engine in separate thread.

      Partnered applications automatically register themselves with the Spline service
      manager, including their access information, so that clients utilizing the manager
      as a directory or system bus can lookup partnered applications by name.  Partner
      processes are started and stopped by Spline, so developers can focus on programming
      the APIs directly; sysadmins can worry about security availability.

      The framework also allows for customization of the network connection, or session
      mode, by directly modifying the control scope or 'mode' associated with the peer.
      Service APIs are but a high-level implementation of a mode:

      class MyApplication(pentacle.Application):
          class InitialMode(pentacle.Application.InitialMode):
              # Method names are actually resolved ad mode-level.  The APIMode delegates
              # all object access to the opened API.

              def doSwitchMode(self, engine, peer, nameOfMode):
                  peer.mode = lookupMode(nameOfMode).andBuildIt(peer)
                  return '%s -- good' % nameOfMode

    ~ What IS the security?

      The basic authentication mode uses HMAC-digested password and login pairs, based
      on private (secret) symmetric password keys.  There is an internal rights database
      that handles permissions, which will eventually need some kind of service interface.

      Client socket connections are unencrypted, but encryption requirements are usually
      handled within the organization's application code, or, using transport-level
      encryption (like IPSEC/SSL/VPN).

    ~ Where are the support resources?

      Documentation should be shipped with the package, but must be built
      (with Sphinx and epydoc).  The builtin Falcon Web Management service
      automatically serves these docs.

      I'll host online documentation at:

        http://www.penobscotrobotics.us/docs/pentacle

      There is currently no unit testing.
