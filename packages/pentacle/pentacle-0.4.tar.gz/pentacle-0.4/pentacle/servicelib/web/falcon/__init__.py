# Django Web Server Implementation.
import sys, os
from StringIO import StringIO

from django.core.management.validation import get_validation_errors
from django.core.handlers.wsgi import WSGIHandler
from django.conf import settings
from django.utils import translation

from django.core.servers.basehttp import AdminMediaHandler, WSGIServerException, \
                                         WSGIRequestHandler, WSGIServer

class ValidationError(Exception):
    pass

def ValidactivateOnce(app = None):
    if not getattr(sys, '__django_validactivated', False):
        s = StringIO()
        num_errors = get_validation_errors(s, app)
        if num_errors:
            raise ValidationError("One or more models did not validate:\n%s" % s.getvalue())

        translation.activate(settings.LANGUAGE_CODE)
        sys.__django_validactivated = True

def getWSGIServerExceptionMessage(e):
    # Use helpful error messages instead of ugly tracebacks.
    ERRORS = {
        13: "You don't have permission to access that port.",
        98: "That port is already in use.",
        99: "That IP address can't be assigned-to.",
    }
    try: return ERRORS[e.args[0].args[0]]
    except (AttributeError, KeyError):
        return str(e)

class FalconManagementServer(WSGIServer):
    def __init__(self, controller):
        # Setup Django Core Environment.
        os.environ['DJANGO_SETTINGS_MODULE'] = __name__ + '.settings'
        ValidactivateOnce()

        config = controller.application.config
        config = config.ConfigSet(config, section = 'DjangoServer', simplify = True)

        # Manually build WSGI server.
        wsgi_handler = WSGIHandler()

        admin_media_path = config.admin_media_path
        if admin_media_path:
            wsgi_handler = AdminMediaHandler(wsgi_handler, admin_media_path)

        # Fugh: config layer eww.. this will end up defaulting to Manager settings
        # because we're using a ConfigSet -- obviously not what's wanted, so SET THESE!
        hostname = config.hostname or 'localhost'
        port = config.port
        assert port

        from urls import ConfigureDocumentation
        self.documentation = ConfigureDocumentation(config.docs_path, config.docs_url)

        self.controller = controller
        WSGIServer.__init__(self, (hostname, port), WSGIRequestHandler)
        self.set_app(wsgi_handler)

    def setup_environ(self):
        # Called on successful server_bind, and passed down through the application
        # ware to the (WSGI) request class and is stored in the META attribute.
        WSGIServer.setup_environ(self)
        self.base_environ['web.controller'] = self.controller
        self.base_environ['web.documentation'] = self.documentation

    def server_handle_request(self):
        try: return self.baseControlClass.server_handle_request(self)
        except WSGIServerException, e:
            self.log(getWSGIServerExceptionMessage(e))

# Project and Views Support.
from os.path import join as joinpath, dirname
TEMPLATES_DIR = joinpath(dirname(__file__), 'templates')

def getTemplateFile(name):
    return joinpath(TEMPLATES_DIR, name)
