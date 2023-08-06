# $Id: __init__.py,v 1.31 2012/02/01 11:13:25 irees Exp $
"""EMEN2: An object-oriented scientific database."""

def opendb(config=None, **kwargs):
	"""Open a database."""
	# Import the config first and parse
	import emen2.db.config
	cmd = emen2.db.config.UsageParser()
	import emen2.db.database
	return emen2.db.database.DB.opendb(**kwargs)
	

__version__ = "$Revision: 1.31 $".split(":")[1][:-1].strip()