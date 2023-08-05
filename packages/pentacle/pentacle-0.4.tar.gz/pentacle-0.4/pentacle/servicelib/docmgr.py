# Westmetal Document Services
from pentacle.architecture import ServiceBase
from pentacle.runtime import nth, breakOn

class DocumentBrowserManager(ServiceBase):
    NAME = '@westmetal/document/browser'
    def Activate(self, *args, **kwd):
        ServiceBase.Activate(self, *args, **kwd)

        from os import environ
        environ['DISPLAY'] = '1' # Enable X-based browsers

        global webbrowser
        import webbrowser

    WINDOW = dict(normal = 0, new = 1, tab = 2)
    def openUrl(self, url, window = 'normal', autoraise = True, browser = None):
        @nth
        #@breakOn
        def do():
            b = webbrowser.get(browser)
            b.open(url, new = self.WINDOW[window], autoraise = bool(autoraise))

    def knownBrowsers(self):
        return webbrowser._browsers.keys()
