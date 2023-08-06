# $Id: __init__.py,v 1.33 2012/03/12 10:35:52 irees Exp $
VERSION = '2.1b5'
__version__ = "$Revision: 1.33 $".split(":")[1][:-1].strip()

# Support Python 2.6
import collections
if not hasattr(collections, 'OrderredDict'):
	from .util import orderreddict
