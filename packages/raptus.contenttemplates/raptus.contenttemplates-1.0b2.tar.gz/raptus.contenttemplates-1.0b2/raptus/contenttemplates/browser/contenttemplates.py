from zope.component import getAdapters

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.memoize.instance import memoize

from raptus.contenttemplates.interfaces import ITemplate

class Contenttemplates(BrowserView):
    """Displays available content templates
    """

    template = ViewPageTemplateFile('templates/contenttemplates.pt')

    def __call__(self):
        return self.template()

    @memoize
    def templates(self):
        results = []
        templates = getAdapters((self.context,), ITemplate)

        for name, template in templates:
            if template.available():
                results.append({ 'title'       : template.title,
                                 'description' : template.description,
                                 'action'      : '%s/++template++%s' % (self.context.absolute_url(), name),
                                 'selected'    : False,
                                 'icon'        : template.icon,
                                 'extra'       : {'id': name, 'separator': None, 'class': None},
                                 'submenu'     : None,
                                 })

        return results