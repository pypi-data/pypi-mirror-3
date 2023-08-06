# $Id: help.py,v 1.3 2011/10/17 02:46:08 irees Exp $
from emen2.web.view import View

@View.register
class Help(View):

	@View.add_matcher(r'^/help/$')
	def main(self, **kwargs):
		self.title = "Help"
		self.template = "/pages/help"
		
		
__version__ = "$Revision: 1.3 $".split(":")[1][:-1].strip()
