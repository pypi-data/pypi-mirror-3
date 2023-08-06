from Products.Archetypes import atapi
from Products.CMFCore import utils as cmfutils

from zope.i18nmessageid import MessageFactory
HitListMessageFactory = MessageFactory('HitList')

from AccessControl import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

from Products.HitList import config

security = ModuleSecurityInfo('Products.HitList')

security.declarePublic('AddBookmark')
AddBookmark = 'Add Bookmark'
setDefaultRoles(AddBookmark, ('Authenticated',))

def initialize(context):

    from content import hitlist

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    for atype, constructor in zip(content_types, constructors):
        cmfutils.ContentInit("%s: %s" % (config.PROJECTNAME, atype.portal_type),
            content_types      = (atype,),
            permission         = AddBookmark,
            extra_constructors = (constructor,),
            ).initialize(context)
