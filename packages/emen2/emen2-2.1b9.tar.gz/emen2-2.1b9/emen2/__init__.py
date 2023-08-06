# $Id: __init__.py,v 1.37 2012/07/11 11:31:48 irees Exp $
VERSION = '2.1b9'
__version__ = "$Revision: 1.37 $".split(":")[1][:-1].strip()

# Support Python 2.6
import collections
if not hasattr(collections, 'OrderredDict'):
	from .util import orderreddict
