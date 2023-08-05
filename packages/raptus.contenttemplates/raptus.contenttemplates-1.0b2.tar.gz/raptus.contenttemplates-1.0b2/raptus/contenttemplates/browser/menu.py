from urllib import quote_plus
from zope.interface import implements
from zope.component import getAdapters
from zope.app.publisher.browser.menu import BrowserMenu
from zope.app.publisher.browser.menu import BrowserSubMenuItem

from plone.memoize.instance import memoize

from interfaces import IContenttemplatesSubMenuItem
from interfaces import IContenttemplatesMenu

from raptus.contenttemplates.interfaces import ITemplate
from raptus.contenttemplates import raptusContenttemplatesMessageFactory as _

class ContenttemplatesSubMenuItem(BrowserSubMenuItem):
    implements(IContenttemplatesSubMenuItem)

    title = _(u'label_contenttemplates_menu', default=u'Templates')
    description = _(u'title_contenttemplates_menu', default=u'Content templates available in this context')
    submenuId = 'plone_contentmenu_contenttemplates'

    order = 25
    extra = {'id': 'plone-contentmenu-contenttemplates'}

    @property
    def action(self):
        return self.context.absolute_url() + '/contenttemplates'

    @memoize
    def available(self):
        templates = getAdapters((self.context,), ITemplate)
        for name, template in templates:
            if template.available():
                return True
        return False

    def selected(self):
        return False

class ContenttemplatesMenu(BrowserMenu):
    implements(IContenttemplatesMenu)

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        results = []
        templates = getAdapters((context,), ITemplate)

        for name, template in templates:
            if template.available():
                results.append({ 'title'       : template.title,
                                 'description' : template.description,
                                 'action'      : '%s/++template++%s' % (context.absolute_url(), name),
                                 'selected'    : False,
                                 'icon'        : template.icon,
                                 'extra'       : {'id': name, 'separator': None, 'class': None},
                                 'submenu'     : None,
                                 })

        return results
