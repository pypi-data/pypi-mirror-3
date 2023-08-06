# $Id: __main__.py,v 1.4 2012/02/17 10:06:49 irees Exp $

if __name__ == "__main__":
	import emen2.web.server
	emen2.web.server.start_standalone()

__version__ = "$Revision: 1.4 $".split(":")[1][:-1].strip()
