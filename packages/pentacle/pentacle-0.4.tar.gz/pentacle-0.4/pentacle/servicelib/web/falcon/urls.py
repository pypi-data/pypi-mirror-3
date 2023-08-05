from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(settings.PROJECT_MODULE + '.views',
    # Examples:
    # url(r'^$', 'dj.views.home', name='home'),
    # url(r'^dj/', include('dj.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    # Spline Management.
    url(r'^status$', 'viewStatus'),
    url(r'^$',       'viewStatus'),
)

urlpatterns += patterns('django.views.static',
                        url(r'^(?P<path>(?:images|js|css)/.*)', 'serve',
                            dict(document_root = settings.FALCON_MEDIA_ROOT)))

import re
CLEAN_DOCS_URL = re.compile(r'^/*(.*?)/*$')
cleanDocsUrl = lambda u: CLEAN_DOCS_URL.match(u).group(1)

def ConfigureDocumentation(path, urlbase = None):
    from os.path import abspath
    path = abspath(path)

    urlbase = 'docs' if urlbase is None else cleanDocsUrl(urlbase)

    ##    while urlbase[:1] == '/':
    ##        urlbase = urlbase[1:]
    ##    while urlbase[-1:] == '/':
    ##        urlbase = urlbase[:-1]

    global urlpatterns
    urlpatterns += patterns('django.views.static',
                            url(r'^%s/(?P<path>.*)' % urlbase, 'serve',
                                dict(document_root = path)))

    return dict(link = urlbase)
