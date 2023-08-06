import monkeypatches

from collective.editskinswitcher import permissions
from zope.i18nmessageid import MessageFactory
SwitcherMessageFactory = MessageFactory('editskinswitcher')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
