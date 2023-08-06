# $Id: __main__.py,v 1.5 2012/07/28 06:31:19 irees Exp $

if __name__ == "__main__":
    import emen2.web.server
    emen2.web.server.start_standalone()

__version__ = "$Revision: 1.5 $".split(":")[1][:-1].strip()
