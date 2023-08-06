# $Id: __init__.py,v 1.35 2012/06/26 10:00:07 irees Exp $
VERSION = '2.1b8'
__version__ = "$Revision: 1.35 $".split(":")[1][:-1].strip()

# Support Python 2.6
import collections
if not hasattr(collections, 'OrderredDict'):
	from .util import orderreddict
