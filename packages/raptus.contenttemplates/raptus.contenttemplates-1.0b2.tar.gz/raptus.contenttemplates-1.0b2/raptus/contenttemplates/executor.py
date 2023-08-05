import transaction
from zope import interface, component

from Products.statusmessages.interfaces import IStatusMessage

from raptus.contenttemplates.interfaces import ITemplateExecutor, ITemplate
from raptus.contenttemplates import raptusContenttemplatesMessageFactory as _

class TemplateExecutor(object):
    interface.implements(ITemplateExecutor)
    component.adapts(interface.Interface)
    
    def __init__(self, context):
        self.context = context
    
    def create(self, template, data):
        statusmessage = IStatusMessage(self.context.REQUEST)
        
        if not ITemplate.providedBy(template):
            statusmessage.addStatusMessage(_(u'Invalid template'), u'error')
            return self.context.REQUEST.RESPONSE.redirect(self.context.absolute_url())
        
        actions = template.actions()
        transaction.begin()
        try:
            for action in actions:
                if not action.execute(self.context, data):
                    raise
        except:
            transaction.abort()
            statusmessage.addStatusMessage(template.fail_message(data), u'error')
            return self.context.REQUEST.RESPONSE.redirect(self.context.absolute_url())
            
        statusmessage.addStatusMessage(template.success_message(data), u'info')
        return template.success(data)