from zope.i18nmessageid import MessageFactory
ExternalEditorMessageFactory = MessageFactory('collective.externaleditor')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
