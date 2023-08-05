from zope import interface

class ITemplateExecutor(interface.Interface):
    """Responsible for executing the actions provided by a template
    """
    
    def create(template):
        """Executes the actions of the template in the adapted context
        """

class ITemplate(interface.Interface):
    """A template providing the actions for the executor
    """
    
    title = interface.Attribute("title", 
                                """The userfriendly name of this template""")
    description = interface.Attribute("description", 
                                      """A userfriendly description of this template""")
    icon = interface.Attribute("icon", 
                               """Path to an icon (image) for this template""")
    form = interface.Attribute("form", 
                               """
                               Name of a z3c.form to be filled before executing the actions.
                               
                               The form has to be a subclass of raptus.contenttemplates.browser.form.BaseTemplateForm,
                               wrapped using plone.z3cform.layout.wrap_form and registered with the name specified.
                               
                               The data of the form will be available to the actions.
                               
                               If this attribute is None, the actions will be executed right away without any data passed.
                               """)
        
    def available():
        """Whether this template is available or not
        """
        
    def actions():
        """List of actions (objects implementing IAction)
        
        see raptus.contenttemplates.actions for the available actions.
        """
        
    def success():
        """What to be done on success
        """
        
    def success_message(data):
        """The message to be presented to the user on success
        """
        
    def fail_message(data):
        """The message to be presented to the user if creating the template failed
        """
        
class IAction(interface.Interface):
    """An action to be executed
    """
    
    def execute(context, data):
        """Called by the executor
        
        context: the context this actions is to be executed
        data: the data of the form specified by the template
        
        Either returns a new context if a new object is created or
        the received one if not. Returns False if the action failed
        """