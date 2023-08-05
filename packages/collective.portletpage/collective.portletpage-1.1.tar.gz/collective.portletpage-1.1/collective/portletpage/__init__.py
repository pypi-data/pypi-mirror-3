import zope.i18nmessageid
from collective.portletpage import config

from Products.Archetypes import atapi
from Products.CMFCore import utils

MessageFactory = zope.i18nmessageid.MessageFactory('collective.portletpage')


def initialize(context):
    """Intializer called when used as a Zope 2 product.
    """

    import content

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit("%s: %s" % (config.PROJECTNAME, atype.portal_type),
            content_types = (atype, ),
            permission = config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors = (constructor, ),
            ).initialize(context)
