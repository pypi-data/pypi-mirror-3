from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.app.publisher.interfaces.browser import IBrowserSubMenuItem

class IContenttemplatesSubMenuItem(IBrowserSubMenuItem):
    """The menu item linking to the actions menu.
    """

class IContenttemplatesMenu(IBrowserMenu):
    """The actions menu.

    This gets its menu items from portal_actions.
    """