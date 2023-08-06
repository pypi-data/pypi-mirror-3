"""HitList content holding references to the hit listed objects
"""

from zope.interface import implements
from zope.i18n import translate

from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFPlone.utils import safe_unicode

from Products.Archetypes.public import *

from Products.ATContentTypes.content.base import ATCTMixin

from Products.HitList.config import PROJECTNAME
from Products.HitList.interfaces import IHitList
from Products.HitList import HitListMessageFactory as _

HitListSchema = BaseContentMixin.schema.copy() + Schema((

    ReferenceField(
        name='bookmarks',
        required=0,
        relationship='bookmarked',
        multiValued=1,
        widget=ReferenceWidget(
            label=_('label_bookmarks', default=u'Bookmarks'),
            visible=0,
        ),
    ),

))

HitListSchema.delField('title')


class HitList(BaseContentMixin, ATCTMixin):
    """ A users hitlist
    """
    implements(IHitList)

    portal_type = meta_type = "HitList"

    _at_rename_after_creation = False
    schema = HitListSchema

    def Title(self):
        """
        """
        try:
            return safe_unicode(translate(_('hitlist_title', default=u'Hitlist'), context=self.REQUEST)).encode('utf-8')
        except:
            return 'Hitlist'

registerType(HitList, PROJECTNAME)
