from Globals import InitializeClass

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.permissions import ManagePortal

from Products.CMFEditions.interfaces.IModifier import ISaveRetrieveModifier
from Products.CMFEditions.interfaces.IModifier import IConditionalTalesModifier
from Products.CMFEditions.Modifiers import ConditionalTalesModifier


#----------------------------------------------------------------------
# Product initialziation, installation and factory stuff
#----------------------------------------------------------------------

def initialize(context):
    """Registers modifiers with zope (on zope startup).
    """
    for m in modifiers:
        context.registerClass(
            m['wrapper'], m['id'],
            permission = ManagePortal,
            constructors = (m['form'], m['factory']),
            icon = m['icon'],
        )

def install(portal_modifier):
    """Registers modifiers in the modifier registry (at tool install time).
    """
    # Detecting Plone 4 and higher
    try: 
        import plone.app.upgrade 
        # PLONE_VERSION = 4
        providedBy = IConditionalTalesModifier.providedBy
    except ImportError: 
        # PLONE_VERSION = 3
        providedBy = IConditionalTalesModifier.isImplementedBy
    
    for m in modifiers:
        id = m['id']
        if id in portal_modifier.objectIds():
            continue
        title = m['title']
        modifier = m['modifier']()
        wrapper = m['wrapper'](id, modifier, title)
        enabled = m['enabled']
        
        if providedBy(wrapper):
            wrapper.edit(enabled, m['condition'])
        else:
            wrapper.edit(enabled)

        portal_modifier.register(m['id'], wrapper)


# silly modifier just for demos
manage_UnlockerModifierAddForm =  \
    PageTemplateFile('www/UnlockerModifierAddForm.pt', globals(),
                     __name__='manage_UnlockerModifierAddForm')

def manage_addUnlockerModifier(self, id, title=None,
                                            REQUEST=None):
    """Add a External Editor modifier
    """
    modifier = UnlockerModifier()
    self._setObject(id, ConditionalTalesModifier(id, modifier, title))

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


#----------------------------------------------------------------------
# Unlocker modifier implementation
#----------------------------------------------------------------------

class UnlockerModifier:
    """ 
    """

    __implements__ = (ISaveRetrieveModifier, )

    def beforeSaveModifier(self, obj, clone):
        clone.__dict__['_dav_writelocks'] = None
        return {}, [], []

    def afterRetrieveModifier(self, obj, repo_clone, preserve=()):
        return [], [], {}

InitializeClass(UnlockerModifier)


#----------------------------------------------------------------------
# Unlocker modifier configuration
#----------------------------------------------------------------------

modifiers = (
    {
        'id': 'UnlockerModifier',
        'title': "Unlock the clone before saving it",
        'enabled': True,
        'condition': "python: True",
        'wrapper': ConditionalTalesModifier,
        'modifier': UnlockerModifier,
        'form': manage_UnlockerModifierAddForm,
        'factory': manage_addUnlockerModifier,
        'icon': 'www/modifier.gif',
    },
)
