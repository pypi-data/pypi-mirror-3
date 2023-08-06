from zope.interface import Interface
from zope import schema

from collective.wfform import _

class IComment(Interface):

    comment = schema.Text(
        title=_(u"Comment"),
        description=_(u"Please enter a comment for this state change."),
        required=False)

class IWorkflowAction(Interface):

    workflow_action = schema.Text(
        title=_(u"Workflow action"),
        required=True)
