# $Id: workflow.py,v 1.8 2012/07/28 06:31:18 irees Exp $
from emen2.web.view import View

@View.register
class Workflow(View):

    @View.add_matcher(r'^/workflow/$')    
    def main(self,*_, **__):
        self.template = "/simple"
        self.title = "User Queries &amp; Workflows"
        self.set_context_item("content","Workflow:<br /><br />")

        wf = self.db.workflow.get()
        self.set_context_item("content", self.ctxt["content"] + str(wf))


__version__ = "$Revision: 1.8 $".split(":")[1][:-1].strip()
