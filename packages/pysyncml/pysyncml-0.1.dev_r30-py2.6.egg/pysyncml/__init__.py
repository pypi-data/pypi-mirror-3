# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id: __init__.py 29 2012-06-30 22:52:55Z griff1n $
# lib:  pysyncml
# auth: griffin <griffin@uberdev.org>
# date: 2012/04/20
# copy: (C) CopyLoose 2012 UberDev <hardcore@uberdev.org>, No Rights Reserved.
#------------------------------------------------------------------------------

'''
The ``pysyncml`` package provides a pure-python implementation of the
SyncML adapter framework and protocol. It does not actually provide
any storage or agent implementations - these must be provided by the
calling program.

For more information and links to documentation, please go to::

  http://pypi.python.org/pypi/pysyncml/

'''

from .constants import *
from .common import *
from .agents import *
from .items import *
from .context import *
from .codec import *
from .state import *
from .ctype import *
from .model import enableSqliteCascadingDeletes

#------------------------------------------------------------------------------
# end of $Id: __init__.py 29 2012-06-30 22:52:55Z griff1n $
#------------------------------------------------------------------------------
