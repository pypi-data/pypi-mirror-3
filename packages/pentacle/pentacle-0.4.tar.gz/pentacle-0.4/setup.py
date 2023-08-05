#!python
# Pentacle Setup Configuration.
# --
# Copyright 2012 Clint Banis & Penobscot Robotics.  All rights reserved.
#

# Todo: provide some kind of package/distro overview:
'%(main_documentation)s' # (RST-Enabled)

# PyPI Metadata (PEP 301)
SETUP_CONF = \
dict (name = "pentacle",
      description = "An O-O P2P RPC protocol and application framework.",

      download_url = "http://frauncache.googlecode.com/svn/trunk/Pentacle",

      license = "PSF",
      platforms = ['OS-independent', 'Many'],

      include_package_data = True,

      keywords = ['python.objects.remote', 'spline', 'pentacle',
                  'wsgi', 'web', 'rpc', 'p2p', 'remote'],

      classifiers = ['Development Status :: 2 - Pre-Alpha',
                     'License :: OSI Approved :: Python Software Foundation License',
                     'Programming Language :: Python :: 2',
                     'Operating System :: OS Independent',
                     'Environment :: Console',
                     'Environment :: Web Environment',
                     'Environment :: Plugins',
                     'Framework :: Django',
                     'Topic :: Scientific/Engineering',
                     'Topic :: Software Development :: Libraries :: Python Modules',
                     'Topic :: Software Development :: Embedded Systems',
                     'Topic :: Software Development :: Libraries :: Application Frameworks',
                     'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                     'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
                     'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
                     'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
                     'Topic :: Internet :: Proxy Servers',
                     'Topic :: System :: Networking',
                     'Topic :: System :: Clustering',
                     'Topic :: System :: Distributed Computing',
                     'Topic :: System :: Systems Administration',
                     'Topic :: Office/Business :: Groupware',
                     'Topic :: Office/Business :: Scheduling',
                     'Topic :: Utilities',
                     'Intended Audience :: System Administrators',
                     'Intended Audience :: End Users/Desktop',
                     'Intended Audience :: Science/Research',
                     'Intended Audience :: Education'],
    )


# Configure some of this at runtime.
def Summary():
    # Merge code package documentation and setup top-level.
    from pentacle import __doc__ as docMain
    return __doc__ % dict(main_documentation = docMain)

def Configuration(packages):
    from pentacle import __author__, __author_email__, __version__, __url__

    # Overlay configuration:
    SETUP_CONF['version'] = __version__
    SETUP_CONF['url'] = __url__

    SETUP_CONF['author'] = __author__
    SETUP_CONF['author_email'] = __author_email__

    SETUP_CONF['long_description'] = Summary()
    SETUP_CONF['packages'] = packages

    return SETUP_CONF

def Setup():
    try: from setuptools import setup, find_packages
    except ImportError: from distutils.core import setup, find_packages

    # Invoke setup script:
    setup(**Configuration(find_packages()))

if __name__ == '__main__':
    Setup()
