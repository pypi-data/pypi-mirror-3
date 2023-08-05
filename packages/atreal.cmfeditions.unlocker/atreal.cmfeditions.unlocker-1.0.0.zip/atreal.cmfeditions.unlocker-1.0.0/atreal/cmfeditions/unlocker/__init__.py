from atreal.cmfeditions.unlocker import UnlockerModifier
from Products.CMFCore.utils import getToolByName


def initialize(context):
    # initialize standard modifiers to make them addable through the ZMI
    UnlockerModifier.initialize(context)
