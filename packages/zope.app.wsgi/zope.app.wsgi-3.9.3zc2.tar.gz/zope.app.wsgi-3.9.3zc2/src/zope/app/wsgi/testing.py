##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""zope.app.wsgi common test related classes/functions/objects.

$Id: testing.py 110773 2010-04-13 11:49:56Z thefunny42 $
"""

__docformat__ = "reStructuredText"

import zope.app.wsgi
from zope.app.wsgi.testlayer import BrowserLayer

AppWSGILayer = BrowserLayer(zope.app.wsgi)

