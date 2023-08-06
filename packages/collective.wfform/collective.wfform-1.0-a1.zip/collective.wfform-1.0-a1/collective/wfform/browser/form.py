import urllib

from zope import interface, schema
from z3c.form import form, field, button
from z3c.form.interfaces import HIDDEN_MODE
from plone.app.z3cform.layout import wrap_form

from Products.CMFCore.utils import getToolByName

from collective.wfform import _
from collective.wfform.interfaces import IComment
from collective.wfform.interfaces import IWorkflowAction

class WorkflowTransitionForm(form.Form):
    ignoreContext = True
    next_url = None

    def getSchemaFromContext(self):
        try:
            transition = self.request['workflow_action']
        except KeyError:
            transition = self.request['form.widgets.workflow_action']
        # update the form title based on the transition
        self.label = self.getFormTitle(transition)
        try:
            fields = self.context.getSchemaForTransition(transition)
            if fields:
                fields = field.Fields(fields)
        except AttributeError:
            pass
        if fields:
            fields = fields + field.Fields(IComment)
        else:
            fields = field.Fields(IComment)
        fields = fields + field.Fields(IWorkflowAction)
        fields['workflow_action'].mode = HIDDEN_MODE
        return fields

    def getFormTitle(self, transition):
        workflow_tool = getToolByName(self.context, "portal_workflow")
        chain = workflow_tool.getChainFor(self.context)
        workflow_name = chain[0]
        workflow = workflow_tool.getWorkflowById(workflow_name)
        transition = workflow['transitions'][transition]
        transition_title = transition.title
        return transition_title + ' for ' + self.context.Title()

    def updateActions(self):
        form.Form.updateActions(self)
        self.actions["save"].addClass("context")
        self.actions["cancel"].addClass("standalone")

    def updateWidgets(self):
        self.fields = self.getSchemaFromContext()
        form.Form.updateWidgets(self)
        if 'workflow_action' in self.request:
            self.widgets['workflow_action'].value = (
                self.request['workflow_action'])

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        try:
            data = self.context.processTransitionForm(data)
        except AttributeError:
            pass
        comment = data['comment'] or u""
        comment = comment.strip()
        try:
            comment = comment.encode('utf-8')
        except UnicodeDecodeError:
            pass
        params = urllib.urlencode({'workflow_action': data['workflow_action'],
                                   'comment': comment})
        self.request.response.redirect("%s/content_status_modify?%s" % (self.context.absolute_url(), params,))

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        pass

WorkflowTransitionForm = wrap_form(WorkflowTransitionForm)  
