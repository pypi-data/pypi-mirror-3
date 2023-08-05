# Management Views.
from django.shortcuts import render_to_response
from django.template import Template, Context
from django.http import HttpResponse

from . import getTemplateFile
from ....packaging import Fault

from datetime import datetime

def render_template_response(template_name, **values):
    template_file = getTemplateFile(template_name)
    template_source = open(template_file).read()
    t = Template(template_source)
    content = t.render(Context(values))
    return HttpResponse(content)

render = render_template_response
def viewStatus(request):
    wc = request.META['web.controller']
    messages = []

    # Horrible place for actions (in a status view).
    action = request.GET.get('action')

    try:
        if action == 'reload-views':
            wc.reloadViews()
        elif action == 'shutdown-manager':
            wc.shutdownManager()

    except Fault, f:
        messages.append(f.toString(True))

    # get the remote application.config repr
    mgrConfig = '(not yet available)'

    def partnersInfo():
        nr = 0
        for p in stats['partners']:
            info = spline.GetPartnerInfo(p)

            try: info['configuration'] = open(info['config_file']).read()
            except (IOError, KeyError): pass

            try: boottime = info['boottime']
            except KeyError:
                boottime = '(Unknown)'
            else:
                boottime = datetime.fromtimestamp(boottime)
                info['boottime'] = boottime.ctime()

            info['nr'] = nr
            nr += 1

            yield info

    spline = wc.managerApi

    try:
        stats = spline.GetManagerStats()
        partners = list(partnersInfo())
        version = spline.Identify()
    except Fault, f:
        return HttpResponse(f.toString(True), content_type = 'text/plain')

    return render('status.html',
                  webControl = wc,
                  documentation = request.META['web.documentation'],
                  messages = messages,
                  spline = dict(version = version,
                                partners = partners,
                                mgrConfig = mgrConfig,
                                stats = stats))

# Client-side auth.  (What we want is server auth tho, matched up with user status)
    ##    auth = urllib2.HTTPPasswordMgr()
    ##    auth.add_password(realm, host, username, password)
    ##    opener = urllib2.build_opener(
    ##        urllib2.HTTPBasicAuthHandler(password_mgr = auth)
    ##    )
