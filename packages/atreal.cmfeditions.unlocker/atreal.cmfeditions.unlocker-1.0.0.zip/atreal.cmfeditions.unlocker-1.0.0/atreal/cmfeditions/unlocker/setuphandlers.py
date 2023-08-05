from Products.CMFCore.utils import getToolByName
from atreal.cmfeditions.unlocker import UnlockerModifier

def importVarious(context):
    """
    Import various settings.

    Provisional handler that does initialization that is not yet taken
    care of by other handlers.
    """
    # Only run step if a flag file is present
    if context.readDataFile('unlocker_various.txt') is None:
        return
    site = context.getSite()
    portal_modifier = getToolByName(site, 'portal_modifier')
    UnlockerModifier.install(portal_modifier)
