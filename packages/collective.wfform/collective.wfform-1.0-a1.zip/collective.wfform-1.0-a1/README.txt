Introduction
============

collective.wfform gives a developer the ability to present a z3c.form 
during a workflow transition.

To implement this for a transition in a particular workflow, 
change the transition url from:

%(content_url)s/content_status_modify?workflow_action=submit

to:

%(content_url)s/workflow_transition_form?workflow_action=submit

This will give you a jQuery popup form with a comments field. 
To add your own fields, add a method to your content type which 
returns a z3c schema based on the transition.

    security.declareProtected(permissions.ModifyPortalContent, 'getSchemaForTransition')
    def getSchemaForTransition(self, transition):
        """Return a fieldset depending on the transition"""
        if transition == 'my_transition':
            return IMyTransitionForm

IMyTransitionForm should be a standard interface class with a zope3 schema.

To process the data from the form, add another method onto your class to manage this.

    security.declareProtected(permissions.ModifyPortalContent, 'processTransitionForm')
    def processTransitionForm(self, data):
        """Return a fieldset depending on the transition"""
        if data.has_key('my_field'):
            self.setMyField(data['my_field'])

