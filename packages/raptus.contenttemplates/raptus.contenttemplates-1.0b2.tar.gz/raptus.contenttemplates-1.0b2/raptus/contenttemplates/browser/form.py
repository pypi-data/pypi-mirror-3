from AccessControl import Unauthorized

from z3c.form import interfaces, form, button
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from raptus.contenttemplates.interfaces import ITemplateExecutor
from raptus.contenttemplates import raptusContenttemplatesMessageFactory as _

class BaseTemplateForm(form.Form):
    mode = interfaces.INPUT_MODE
    ignoreContext = True
    ignoreRequest = False
    index = ViewPageTemplateFile('templates/form.pt')
    
    def __call__(self):
        if not self.adapter().available():
            raise Unauthorized
        return super(BaseTemplateForm, self)()
    
    @property
    def label(self):
        return self.adapter().title
    
    @property
    def description(self):
        return self.adapter().description
    
    @property
    def icon(self):
        return self.adapter().icon
    
    @button.buttonAndHandler(_(u'Create'))
    def handleCreate(self, action):
        executor = ITemplateExecutor(self.context)
        return executor.create(self.adapter(), self.extractData()[0])
    
    @button.buttonAndHandler(_(u'Cancel'))
    def handleCancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())
        
    def adapter(self):
        raise NotImplemented()