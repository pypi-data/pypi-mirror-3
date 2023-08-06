# $Id: __main__.py,v 1.13 2012/02/23 23:26:26 edwlan Exp $

if __name__ == "__main__":
	import emen2.db
	db = emen2.db.opendb(admin=True)

__version__ = "$Revision: 1.13 $".split(":")[1][:-1].strip()
