# $Id: error.py,v 1.5 2011/10/17 02:46:08 irees Exp $
from emen2.web.view import View

@View.register
class Error(View):

	@View.add_matcher('/error/')
	@View.provides('error_handler')
	def main(self, error='', location='/', **kwargs):
		self.template = '/errors/error'
		self.title = 'Error'
		self.set_context_item("error", error)
		self.set_context_item('location', location)

	@View.add_matcher('/error/auth')
	def auth(self, error='', location='/', **kwargs):
		self.template = '/errors/auth'
		self.title = 'Error'
		self.set_context_item("error", error)
		self.set_context_item('location', location)

	@View.add_matcher('/error/resp')
	def resp(self, error='', location='/', **kwargs):
		self.template = '/errors/resp'
		self.title = 'Error'
		self.set_context_item("error", error)
		self.set_context_item('location', location)


		
__version__ = "$Revision: 1.5 $".split(":")[1][:-1].strip()
