from zope import component, interface

from zope.traversing.interfaces import TraversalError, ITraversable

from raptus.contenttemplates.interfaces import ITemplate, ITemplateExecutor

class TemplateTraverser(object):
    """Template namespace traverser
    """
    interface.implements(ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        template = component.queryAdapter(self.context, ITemplate, name=name)
        if template:
            if not template.form:
                executor = ITemplateExecutor(self.context)
                return executor.create(template, {})
            return component.getMultiAdapter((self.context, self.request), name=template.form)
        else:
            raise TraversalError(self.context, name)