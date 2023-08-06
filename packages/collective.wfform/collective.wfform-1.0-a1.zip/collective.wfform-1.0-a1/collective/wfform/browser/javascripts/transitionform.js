jQuery(function($){

    $('#plone-contentmenu-workflow dd.actionMenuContent a[href*=workflow_transition_form]').prepOverlay(
        {
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: 'form',
            closeselector: '[name=form.buttons.cancel]',
            noform: 'reload'
        }
    );
});
