# Service Manager Components.
from ..application import Application
from ..security import CalculateDigest, GenerateSecretKey
from ..runtime import Object, LookupObject, getCurrentSystemTime, sendSignal, breakOn, contextmanager
from ..client import Client, Session
from ..network import AsyncoreControl

from . import *

import signal
import socket
import errno
import sys
import os

from os.path import join as joinpath, basename, splitext

DEFAULT_AUTHKEY_SIZE = 32
NOSIG = None

# Utility Routines.
# todo: move into runtime.utility
def DefaultPidFile(name, exepath):
    name = '-'.join(name.split()).lower()
    exepath = splitext(basename(exepath))[0]
    return joinpath('/tmp', 'proc', '%s-%s.pid' % (name, exepath))

def ValidateSignal(name):
    if name == NOSIG:
        return NOSIG

    if isinstance(name, basestring):
        if name.isdigit():
            sigNr = int(name)
        else:
            return getattr(signal, 'SIG%s' % name.upper())
    else:
        assert isinstance(name, int)
        sigNr = name

    for name in dir(signal):
        if len(name) > 3 and name.startswith('SIG') and name[3] != '_':
            if getattr(signal, name) == sigNr:
                return sigNr

    raise UnknownSignalName(name)

@contextmanager
def TemporaryWorkingDir(workingDir):
    if workingDir is None:
        yield
    else:
        thisDir = os.getcwd()
        os.chdir(workingDir)
        try: yield
        finally:
            os.chdir(thisDir)

# Partner Class Implementations
class Partner(Object):
    'Abstract base class'

    @classmethod
    def FromConfig(self, cfg):
        # Load enough options to distinguish partner type.
        main = cfg.getSectionObject('Partner')
        handlerName = main.get('handler')

        if handlerName:
            if handlerName == 'adhoc':
                # Yes, a little workaround, cuz we're not sure how spline is packaged.
                return AdhocPartner.FromConfig(cfg)

            handler = LookupObject(handlerName)
            if handler is None:
                raise NameError(handlerName)

            # Pass it to another object.
            return handler.FromConfig(cfg)

        progr = cfg.getSectionObject('Program')
        builtin = progr.get('builtin')

        # Another special type -- for straight pentacle servers.
        if builtin == 'pentacle-server':
            return PentaclePartner.FromConfig(cfg)

        return ProgramPartner.FromConfig(cfg)

    def __init__(self, cfg, name, auth):
        if auth in ['auto']: # [None]:
            auth = GenerateSecretKey(DEFAULT_AUTHKEY_SIZE)

        # Config
        self.config = cfg
        self.name = name
        self.auth = auth

        self.weblink = cfg.getSectionOption('weblink', 'Application')

        # Stats
        self.bootTime = getCurrentSystemTime()

    def OpenStorage(self, mgr):
        return mgr.OpenStorage(self.name)

    def isAuthorized(self, partner, digest, *payload):
        return CalculateDigest(self.auth, *payload) == digest

    def GetUptime(self):
        return getCurrentSystemTime() - self.bootTime
    def GetInfo(self):
        return dict(name = self.name,
                    boottime = self.bootTime,
                    uptime = self.GetUptime(),
                    weblink = self.weblink)

    def inject(self, injectionMgr, cfg):
        self.bootTime = getCurrentSystemTime()
        self.TrackState(injectionMgr, cfg)
        injectionMgr.partnerInjected(self)

    def updateStatus(self, updateMgr, cfg):
        self.TrackState(updateMgr, cfg)
        updateMgr.partnerUpdated(self)

    def doAutokill(self):
        pass

    def TrackState(self, mgr, cfg):
        # Update state in memory.
        progr = cfg.getSectionObject('Program')
        port = int(progr.get('service-port'))
        self.service_port = int(port) if port else port

        weblink = cfg.getSectionOption('weblink', 'Application')
        if weblink is not None:
            self.weblink = weblink

        bootTime = progr.get('boot-time')
        if bootTime is not None:
            # Todo: time format.
            self.bootTime = int(bootTime)

        self.state = progr.get('state')

        # Update state in records.
        with self.OpenStorage(mgr) as i:
            i.setBootTime(self.bootTime)
            i.setServicePort(self.service_port)

    def RestoreTrackedState(self, mgr):
        # Load current information from records.
        with self.OpenStorage(mgr) as i:
            bootTime = i.getBootTime()
            if bootTime is not None:
                self.bootTime = bootTime

            servicePort = i.getServicePort()
            if servicePort is not None:
                self.service_port = servicePort

class AdhocPartner(Partner):
    'An external previously-unknown process that identifies and registers itself.'

    @classmethod
    def FromConfig(self, cfg):
        # Just load enough to identify and authorize.
        main = cfg.getSectionObject('Partner')
        name = main.get('name')
        auth = main.get('authorization')

        assert name
        return self(cfg, name, auth)

    Meta = Object.Meta('name', 'state')
    def __init__(self, cfg, name, auth):
        Partner.__init__(self, cfg, name, auth)

    def GetInfo(self):
        base = Partner.GetInfo(self)
        base['service_port'] = self.service_port
        return base

class ProgramPartner(Partner):
    'A Spline-managed managed sub-process service.'

    @classmethod
    def FromConfig(self, cfg):
        # A regular program-partner.
        main = cfg.getSectionObject('Partner')
        name = main.get('name')
        auth = main.get('authorization')
        dependencies = main.getOptionMultiple('dependencies')

        progr = cfg.getSectionObject('Program')
        exepath = progr.get('exe-path')
        cmdln_args = [a for a in progr.getOptionMultiple('args') if a is not None]
        pidfile = progr.get('pidfile')
        port = progr.get('service-port')
        working_dir = progr.get('working-dir')
        autokill = progr.get('autokill')

        environ = cfg.getSectionObject('Environ').asDict()

        sigs = cfg.getSectionObject('Signals')
        signals = self.Signals(kill    = sigs.get('kill-signal'),
                               suspend = sigs.get('suspend-signal'),
                               resume  = sigs.get('resume-signal'),
                               reload  = sigs.get('reload-signal'))

        # ... and various runlevel events

        # Validate and construct.
        assert name
        assert exepath

        if pidfile is None:
            pidfile = DefaultPidFile(name, exepath)

        if port:
            if port != 'auto':
                port = int(port)

        return self(cfg, name, auth, exepath, cmdln_args, environ, pidfile,
                    port, working_dir, signals, autokill)

    class Signals(Object):
        if sys.platform == 'cygwin': # or.. linux
            from signal import SIGKILL as DEFAULT_KILL, SIGSTOP as DEFAULT_SUSPEND, \
                               SIGCONT as DEFAULT_RESUME, SIGUSR1 as DEFAULT_RELOAD

        elif sys.platform == 'win32':
            from signal import SIGABRT as DEFAULT_KILL
            DEFAULT_SUSPEND = DEFAULT_RESUME = DEFAULT_RELOAD = -1

        def __init__(self, **kwd):
            self.kill    = ValidateSignal(kwd.pop('kill'   , self.DEFAULT_KILL))
            self.suspend = ValidateSignal(kwd.pop('suspend', self.DEFAULT_SUSPEND))
            self.resume  = ValidateSignal(kwd.pop('resume' , self.DEFAULT_RESUME))
            self.reload  = ValidateSignal(kwd.pop('reload' , self.DEFAULT_RELOAD))

        def copy(self):
            return dict(kill = self.kill, suspend = self.suspend,
                        resume = self.resume, reload = self.reload)

    Meta = Object.Meta('name', 'exepath', 'pidfile', 'service_port')
    def __init__(self, cfg, name, auth, exepath, cmdln_args, environ, pidfile,
                 port, working_dir, signals, autokill):

        Partner.__init__(self, cfg, name, auth)

        self.exepath = exepath
        self.cmdln_args = cmdln_args
        self.environ = environ
        self.pidfile = pidfile
        self.service_port = port
        self.working_dir = working_dir

        self.signals = signals
        self.autokill = autokill

    def GetInfo(self):
        base = Partner.GetInfo(self)
        base.update(dict(exepath = self.exepath,
                         cmdln_args = self.cmdln_args,
                         pidfile = self.pidfile,
                         service_port = self.service_port,
                         signals = self.signals.copy()))
        return base

    def doAutokill(self):
        # todo: override this for PentaclePartner, and have it connect and issue stopApplication.
        if self.autokill and self.signals.kill and isinstance(self.processId, int):
            sendSignal(self.processId, self.signals.kill)

    def ReadPidfile(self):
        if self.pidfile:
            # Strategy: read only enough to identify an integer.
            try:
                contents = open(self.pidfile).read(20)
                if contents.isdigit():
                    return int(contents)

            except IOError, e:
                if e.errno != errno.ENOENT:
                    raise

    def WritePidfile(self, pid):
        if self.pidfile:
            pid = int(pid)
            try:
                fl = open(self.pidfile, 'w')
                print >> fl, pid
                fl.flush()
                fl.close()

            except IOError, e:
                # Usually directory doesn't exist.
                if e.errno != errno.ENOENT:
                    raise

    def ValidateProcess(self):
        # Is the program running with the pid as saved, the same executable?
        # (Recommended for specific executables, not generic instances like python or shell scripts)
        pid = self.ReadPidfile()
        if isinstance(pid, int):
            # Yep, relying on /proc
            try: runningExe = open('/proc/%s/exename' % pid).read()
            except IOError: pass
            else: return runningExe == self.exepath

    def checkRunlevelActively(self):
        # First, check the service-port.
        # todo: catch errors, also skip it if there is no service_port configured.
        # this means merging with isInstanceRunning code (probably put into bus)
        if isinstance(self.service_port, int):
            # Must match this partner name as a feature.  Necessary because service-
            # ports might be reassigned, especially when partner sets are changed.
            partnerName = PartnerNameFeature(self.name)

            try:
                with Session(Client.Open('localhost', self.service_port)) as client:
                    DEBUG('   recognizing:', self.service_port, '(%s)' % self.name)
                    if isRecognizedServer(client.call.Identify(), appFeatures = [partnerName]):
                        # Todo: send updated service manager info (like port),
                        # since obviously it was rebooted out from under partner.
                        return True

            except socket.error, e:
                if e.errno not in [errno.EAGAIN, errno.EBADF, errno.ECONNREFUSED]:
                    raise

            # We'll want to use superior host network.
            #   -- Yeah but host already started, spline-side.
            ##    print 'client-side asyncore wait'
            ##    AsyncoreControl.waitForAsyncoreEnd()
            ##    print '...asyncore done'

        # Then check pidfile and determine its up-time.
        if self.ValidateProcess() is not None:
            return True

    def setupExecutablePath(self, bootMgr):
        return self.exepath
    def setupCommandLineArgs(self, bootMgr):
        return self.cmdln_args
    def setupBootEnvironment(self, bootMgr):
        env = os.environ.copy()
        env['SPLINE_PORT'] = '%s' % (bootMgr.getManagerPort() or '')
        return env

    #@breakOn
    def boot(self, bootMgr):
        if not self.checkRunlevelActively():
            # Otherwise, just boot and build those things
            # todo: allow fork-spawn to cause it to orphan?  We don't want it to get SIGHUP or TERM or whatever
            DEBUG('   booting:', self.name)

            exepath = self.setupExecutablePath(bootMgr)
            args = self.setupCommandLineArgs(bootMgr)
            environ = self.setupBootEnvironment(bootMgr)

            cmdln = [exepath] + list(args)

            with TemporaryWorkingDir(self.working_dir):
                pid = os.spawnve(os.P_NOWAIT, exepath, cmdln, environ)

            # todo: be sensitive to the event that the subprocess didn't successfully boot.
            # (that it somehow crashed).  This isn't necessarily possible if it's orphaned,
            # (or, if we're starting NOWAIT) but I guess we can assume some algorithm that
            # more or less expects a startup answer within an amount of time.
            #
            # Of course, this requires more sophisticated signal/reap-chld handling.

            self.processId = pid
            self.WritePidfile(pid)

            # Push broadcast event to engine
            bootMgr.partnerBooted(self)

class PentaclePartner(ProgramPartner):
    'Specifically a Pentacle sub-server managed by Spline.'

    @classmethod
    def FromConfig(self, cfg):
        # Configure a special program partner that merely invokes another
        # pentacle server instance, passing it another configuration.
        main = cfg.getSectionObject('Partner')
        progr = cfg.getSectionObject('Program')

        name = main.get('name')
        auth = main.get('authorization')

        port = progr.get('service-port')
        autokill = progr.get('autokill')

        # Validate and construct.
        assert name

        if port:
            if port != 'auto':
                port = int(port)

        # Handle inline configuration.
        pentacle_config_file = progr.get('pentacle-config')
        if pentacle_config_file == 'builtin':
            pentacle_config_file = cfg.filename

        return self(cfg, name, auth, port, pentacle_config_file, autokill)

    Meta = Object.Meta('name', 'service_port', 'config_file')
    def __init__(self, cfg, name, auth, port, config_file, autokill):
        ProgramPartner.__init__(self, cfg, name, auth,
                                sys.executable, None, None,
                                None, port, None,
                                self.Signals(), autokill)

        self.config_file = config_file

    def setupCommandLineArgs(self, bootMgr):
        # The partnered application main.
        return ['-m', busPartnerMain()]

    def setupBootEnvironment(self, bootMgr):
        # This would be a good place to paste in the partner authorization code,
        # so it can be used by the bus partner main.
        env = ProgramPartner.setupBootEnvironment(self, bootMgr)
        env[Application.PENTACLE_CONFIG_ENV_VAR] = self.config_file or ''
        env[PENTACLE_PARTNER_NAME_ENV_VAR] = self.name or ''
        env[PENTACLE_PARTNER_AUTH_ENV_VAR] = self.auth or ''
        return env

    def GetInfo(self):
        base = Partner.GetInfo(self) # Skip Program
        base.update(dict(service_port = self.service_port,
                         config_file = self.config_file))
        return base
