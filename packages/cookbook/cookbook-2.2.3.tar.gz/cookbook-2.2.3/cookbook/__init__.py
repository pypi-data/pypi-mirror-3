#
# Copyright John Reid 2006, 2007, 2008, 2012
#


"""
This python package implements some recipes from the python cookbook. Some of the recipes are copied
verbatim from the python cookbook_ and some are modified versions of those at the cookbook. Others 
are written from scratch.

.. _cookbook: http://code.activestate.com/recipes/langs/python/

"""

from bunch import *
from bidirectional_map import *
from const import *
from dicts import *
from enum import *
from equivalence import *
from groupby import *
from lru_cache import *
from named_tuple import *
from pre_post_conditions import *
from process_priority import *
from reverse_dict import *


__major_version__ = 2
__minor_version__ = 2
__release_version__ = 3
__svn_revision__ = '$Revision: 3101 $' # auto-magically updated by subversion using keywords property

__version__ = '%d.%d' % (__major_version__, __minor_version__)
__release__ = '%d.%d.%d' % (__major_version__, __minor_version__, __release_version__)
