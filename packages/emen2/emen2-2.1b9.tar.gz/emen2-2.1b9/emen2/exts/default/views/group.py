# $Id: group.py,v 1.11 2012/07/11 06:22:36 irees Exp $
import time

from emen2.web.view import View


@View.register
class Groups(View):

	@View.add_matcher(r'^/groups/$')
	def main(self,q=None):
		self.template="/pages/groups"
		self.title = "User group directory"
		self.set_context_item("q","")
		groupnames = self.db.group.names()
		groups = self.db.group.get(groupnames)
		admin = self.db.auth.check.admin()
		self.set_context_item("admin",admin)

		if groups == None:
			self.template="/simple"
			self.set_context_item("content","""No user groups found, or insufficient permissions to view user group list.""")
			return
		
		self.ctxt['groupnames'] = groupnames
		self.ctxt['groups'] = groups



@View.register
class Group(View):
	
	@View.add_matcher(r'^/group/(?P<name>[\w\- ]+)/$')
	def main(self, name=None):
		group = self.db.group.get(name)
		self.title = "User group: %s"%(group.displayname)
		self.template = "/pages/group"
		self.ctxt['group'] = group
		self.ctxt['new'] = False
		self.ctxt['edit'] = False


	@View.add_matcher(r'^/group/(?P<name>[\w\- ]+)/edit/$')
	def edit(self, name=None, **kwargs):
		group = self.db.group.get(name)
		self.title = "User group: %s"%(group.displayname)
		self.template = "/pages/group"
		self.ctxt['group'] = group
		self.ctxt['new'] = False
		self.ctxt['edit'] = True

		if self.request_method != 'post':
			return

		group.update(kwargs)
		group = self.db.group.put(group)
		self.ctxt['group'] = group
		self.redirect('/group/%s/'%group.name)
		

	# @View.add_matcher(r'^/group/(?P<name>[\w\- ]+)/new/$')
	@View.add_matcher(r'^/groups/new/$')
	def new(self, name=None, **kwargs):
		# We have to supply a group name.. just use a random string.
		group = self.db.group.new(name=name)		
		self.ctxt['group'] = group
		self.ctxt['new'] = True
		self.ctxt['edit'] = True
		self.title = "New group"
		self.template = "/pages/group"

		if self.request_method != 'post':
			return
			
		group.update(kwargs)
		group = self.db.group.put(group)
		self.ctxt['group'] = group
		self.redirect('/group/%s/'%group.name)
		
		

		
__version__ = "$Revision: 1.11 $".split(":")[1][:-1].strip()
