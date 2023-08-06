# $Id: map.py,v 1.14 2012/03/12 10:34:33 irees Exp $
from emen2.web.view import View

def dfs(root, tree, recurse=1):
	def inner(stack, children, depth=0):
		if recurse > 0 and depth >= recurse:
			return
		for child in children:
			newchildren = tree.get(child, set())
			stack |= newchildren
			inner(stack, newchildren, depth=depth+1)

	stack = set()
	inner(stack, tree.get(None, [root]))
	return stack



@View.register
class Tree(View):

	@View.add_matcher(r'^/sitemap/$', name='root')
	@View.add_matcher(r'^/sitemap/(?P<root>\w+)/$')
	def main(self, root=0, *args, **kwargs):
		kwargs['recurse'] = kwargs.get('recurse', 3)
		self.embed(root=root, *args, **kwargs)
		self.template = '/pages/tree.sitemap'


	@View.add_matcher(r'^/tree/(?P<keytype>\w+)/(?P<root>\w+)/(?P<mode>\w+)/$', name='embed')
	def embed(self, root=None, recurse=1, keytype="record", action=None, mode="children", rectype=None, expandable=True, collapse_rectype=None, collapsed=None, id=''):
		self.template = '/pages/tree'
		self.title = 'Sitemap'

		root = root
		keytype = keytype
		recurse = int(recurse)
		mode = mode
		expandable = expandable
		collapsed = collapsed or set()

		# Expand all nodes. -3 turns into -1...
		if action=="expand" or recurse == -1:
			recurse = -3

		# Bug workaround (fix properly)
		if keytype == 'record':
			root = int(root)

		parents = set()

		# add 2 to recurse to get enough info to draw the next level
		if mode == "children":
			tree = self.db.getchildtree(root, recurse=recurse+2, keytype=keytype, rectype=rectype)
			# get one level of parents as well..
			parents = self.db.getparents(root, keytype=keytype)
		else:
			tree = self.db.getparenttree(root, recurse=recurse+2, keytype=keytype)

		if collapse_rectype:
			collapsed |= self.db.getchildren(root, recurse=-1, rectype=collapse_rectype)

		# connect the root to "None" to simplify drawing..
		tree[None] = [root]
		
		# Get all the names we need to render
		stack = dfs(root, tree, recurse=recurse)
		stack.add(root)
		stack |= parents

		recnames = {}
		if keytype == "record":
			recnames.update(self.db.renderview(stack))
		elif keytype == "paramdef":
			pds = self.db.getparamdef(stack)
			for pd in pds:
				recnames[pd.name] = pd.desc_short
		elif keytype == "recorddef":
			rds = self.db.getrecorddef(stack)
			for rd in rds:
				recnames[rd.name] = rd.desc_short

	
		self.ctxt['mode'] = mode
		self.ctxt['root'] = root
		self.ctxt['tree'] = tree
		self.ctxt['recurse'] = recurse
		self.ctxt['recnames'] = recnames
		self.ctxt['keytype'] = keytype
		self.ctxt['parents'] = parents
		self.ctxt['expandable'] = expandable
		self.ctxt['collapsed'] = collapsed
		self.ctxt['collapse_rectype'] = collapse_rectype
		self.ctxt['id'] = id


__version__ = "$Revision: 1.14 $".split(":")[1][:-1].strip()
