# Pentacle O-O P2P RPC
#
# Copyright (C) 2011-2012 Clint Banis
# Author: Clint Banis <cbanis@gmail.com>
# URL: <http://www.penobscotrobotics.us>

'''\
Object-Oriented Peer-to-Peer RPC access library and server application framework.

:Author: `%(__author__)s <%(__author_email__)s>`__
:Requires: Python 2.6+
:Version: %(__version__)s

:Group Application: application, config, debugging, security, storage
:Group Core: architecture, encoding, packaging, runtime
:Group Networking: network, client, server
:Group Service Partner Bus: bus, bus.partners, bus.services, bus.spline

:Bug: Some synchronization issues cause intermittant network failures
:Todo: Optimize the package format to eliminate unnecessary marks

:See: `the Pentacle code repository <http://frauncache.googlecode.com>`__
:See: `Penobscot Robotics, Co. <http://www.penobscotrobotics.us>`__

:Copyright: |copyright| %(__copyright__)s
.. |copyright| unicode:: 0xA9 .. copyright sign
'''

__author__ = 'Clint Banis' # __contact__
__author_email__ = 'cbanis@gmail.com'
__copyright__ = '2011-2012 Clint Banis & Penobscot Robotics' # __license__

__version__ = 0.4
__docformat__ = 'restructuredtext en'

__url__ = 'http://www.penobscotrobotics.us/cms/page/pentacle'
__doc__ = __doc__ % vars()

def buildApplicationVersion(appName, busVersion):
    return '%s/%s' % (appName, busVersion)

# Yeah, this is for me:
def DEBUG(*args):
    pass # print '[DEBUG]', ' '.join(map(str, args))

import __builtin__ as builtin
builtin.DEBUG = DEBUG
