from Acquisition import aq_parent
from OFS.ObjectManager import checkValidId

from zope import interface
from zope.i18n import translate
from zope.i18nmessageid.message import Message

from raptus.contenttemplates.interfaces import IAction

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString

class FieldDataRetriever(object):
    """
    Helper class to pass attributes to actions which
    depend on data of the form
    """
    def __init__(self, field):
        self.field = field
    def __call__(self, data):
        return data.get(self.field, None)
    
def RetrieveFieldData(obj, data):
    """Method to convert FieldDataRetrievers to real data
    """
    for attr, value in obj.__dict__.items():
        if isinstance(value, FieldDataRetriever):
            setattr(obj, attr, value(data))
        if isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, FieldDataRetriever):
                    value[k] = v(data)
            setattr(obj, attr, value)

class ActionChain(object):
    """
    A Chain of actions which respects the context returned
    by it's containing actions and uses it to execute the next
    action.
    """
    interface.implements(IAction)
    
    def __init__(self, actions):
        self.actions = actions
    
    def execute(self, context, data):
        base = context
        for action in self.actions:
            context = action.execute(context, data)
            if not context:
                return False
        return base

class CreateContent(object):
    """Creates a content object
    """
    interface.implements(IAction)
    
    def __init__(self, id, type, data=None):
        self.id = id
        self.type = type
        self.data = data
        
    def execute(self, context, data):
        RetrieveFieldData(self, data)
        if self.data is None:
            self.data = data
        else:
            for k, v in data.items():
                if not self.data.has_key(k):
                    self.data[k] = v
        for k, v in self.data.items():
            if isinstance(v, Message):
                self.data[k] = translate(v, context=context.REQUEST)
        id = self.getId(context)
        typestool = getToolByName(context, 'portal_types')
        typestool.constructContent(type_name=self.type, container=context, id=id)
        context = context[id]
        context.update(**self.data)
        return context
    
    def getId(self, context):
        id = normalizeString(self.id, context)
        if context.check_id(id, 1, context) is None:
            try:
                checkValidId(context, id)
                return id
            except:
                pass
        new_id = id + '-%s'
        i = 1
        while not context.check_id(new_id % i, 1, context) is None:
            i += 1
        return new_id % i
    
class RenameContent(CreateContent):
    """Renames an existing content object
    """
    
    def __init__(self, id):
        self.id = id
        
    def execute(self, context, data):
        RetrieveFieldData(self, data)
        context.setId(self.getId(context))
        return context
    
class EditContent(object):
    """Edits an existing content object
    """
    interface.implements(IAction)
    
    def __init__(self, data):
        self.data = data
        
    def execute(self, context, data):
        RetrieveFieldData(self, data)
        context.update(**self.data)
        return context
    
class WorkflowTransition(object):
    """Executes a workflow transition
    """
    interface.implements(IAction)
    
    def __init__(self, transition):
        self.transition = transition
        
    def execute(self, context, data):
        RetrieveFieldData(self, data)
        wftool = getToolByName(context, 'portal_workflow')
        try:
            wftool.doActionFor(context, self.transition)
        except:
            return False
        return context
    
class AddGroup(object):
    """Creates a group with the specified roles
    """
    interface.implements(IAction)
    
    def __init__(self, name, roles=()):
        self.name = name
        self.roles = roles
        
    def execute(self, context, data):
        RetrieveFieldData(self, data)
        groupstool = getToolByName(context, 'portal_groups')
        name = normalizeString(self.name, context)
        if not groupstool.getGroupById(name):
            groupstool.addGroup(name, self.roles)
        return context
    
class LocalRoleAcquire(object):
    """Whether local roles shall be acquired or not
    """
    interface.implements(IAction)
    
    def __init__(self, acquire=True):
        self.acquire = acquire
        
    def execute(self, context, data):
        if not self.acquire and not bool(getattr(context, '__ac_local_roles_block__', False)):
            context.__ac_local_roles_block__ = True
            context.reindexObjectSecurity()
        return context
    
class AddLocalRole(object):
    """Adds a local role
    """
    interface.implements(IAction)
    
    def __init__(self, role, user=None):
        self.role = role
        self.user = user
        
    def execute(self, context, data):
        RetrieveFieldData(self, data)
        user = normalizeString(self.user, context)
        roles = dict(context.get_local_roles()).get(user, [])
        if not self.role in roles:
            roles.append(self.role)
        context.manage_addLocalRoles(user, tuple(roles))
        context.reindexObjectSecurity()
        return context
    
class ObjectProvides(object):
    """Make an object implement a specific interface
    """
    interface.implements(IAction)
    
    def __init__(self, interface):
        self.interface = interface
        
    def execute(self, context, data):
        RetrieveFieldData(self, data)
        interface.alsoProvides(context, self.interface)
        context.reindexObject()
        return context
    
class SetViewTemplate(object):
    """Sets the view template for an object
    """
    interface.implements(IAction)
    
    def __init__(self, view):
        self.view = view
        
    def execute(self, context, data):
        RetrieveFieldData(self, data)
        context.setLayout(self.view)
        return context
    
class CopyFrom(object):
    """Copies from a specific content object
    """
    interface.implements(IAction)
    
    def __init__(self, source):
        self.source = source
        
    def _source(self, context):
        uid_catalog = getToolByName(context, 'uid_catalog')
        return uid_catalog(UID=self.source)[0].getObject()
        
    def execute(self, context, data):
        RetrieveFieldData(self, data)
        source = self._source(context)
        data = aq_parent(source).manage_copyObjects([source.getId()])
        result = context.manage_pasteObjects(data)
        return context._getOb(result[0]['new_id'])
    
class SyncWorkflowState(CopyFrom):
    """Recursively sync workflow states
    """
    interface.implements(IAction)
    
    def _recurse_execute(self, context, source):
        try:
            transitions = [r['action'] for r in self.wftool.getInfoFor(source, 'review_history') if r['action']]
        except: # no workflow assigned
            return
        for transition in transitions:
            try:
                self.wftool.doActionFor(context, transition)
            except:
                pass
    
    def _recurse(self, context, source):
        self._recurse_execute(context, source)
        context.reindexObjectSecurity()
        if hasattr(context, 'objectIds'):
            for child in context.objectIds():
                if child in source.objectIds():
                    self._recurse(context._getOb(child), source._getOb(child))
        
    def execute(self, context, data):
        RetrieveFieldData(self, data)
        self.wftool = getToolByName(context, 'portal_workflow')
        self._recurse(context, self._source(context))
        return context
    
class SyncLocalRoles(SyncWorkflowState):
    """Recursively sync local roles
    """
    interface.implements(IAction)
    
    def __init__(self, source, old=None, new=None):
        self.source = source
        self.old = old
        self.new = new
        
    def _recurse_execute(self, context, source):
        local_roles = source.get_local_roles()
        for name, roles in local_roles:
            if name == self.old:
                name = self.new
            context.manage_addLocalRoles(name, tuple(roles))
