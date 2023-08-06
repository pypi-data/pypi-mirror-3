
from Acquisition import aq_inner
from plone.app.layout.viewlets.common import ViewletBase
from AccessControl import Unauthorized

from Products.CMFCore.utils import getToolByName

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.HitList import HitListMessageFactory as _
from Products.HitList.utils import getCurrentUsersHitList

class HitListViewlet(ViewletBase):
    """ hitlist viewlet """

    template = ViewPageTemplateFile('templates/viewlet.pt')

    def render(self):
        context = aq_inner(self.context)
        source = getCurrentUsersHitList(context)
        if source is not None:
            if source.hasRelationshipTo(context, relationship='bookmarked'):
                return ""
        return self.template()

class HitList(BrowserView):
    """ hitlist browserview """
    def hasPermission(self):
        context = aq_inner(self.context)
        mship = getToolByName(context,'portal_membership')
        return mship.checkPermission("Add Bookmark", context)

    def add(self):
        context = aq_inner(self.context)
        source = getCurrentUsersHitList(context)
        utils = getToolByName(context,'plone_utils')
        if source is None:
            if not self.hasPermission():
                raise Unauthorized
            else:
                mship = getToolByName(context,'portal_membership')
                homefolder = mship.getHomeFolder()
                if homefolder is None:
                    mship.createMemberarea()
                    homefolder = mship.getHomeFolder()
                typestool = getToolByName(context, 'portal_types')
                typestool.constructContent(type_name='HitList', container=homefolder, id='hitlist')
                source = homefolder['hitlist']
        if source is not None:
            if not source.hasRelationshipTo(context, relationship='bookmarked'):
                source.addReference(context, relationship='bookmarked')
                if source.hasRelationshipTo(context, relationship='bookmarked'):
                    utils.addPortalMessage(_(u'Item successfully added to your hitlist.'), 'info')
                else:
                    utils.addPortalMessage(_(u'Adding the item to your hitlist failed.'), 'error')
            else:
                utils.addPortalMessage(_(u'You already added this item to your hitlist.'), 'info')
        self.request.response.redirect('.')

    def remove(self):
        context = aq_inner(self.context)
        source = getCurrentUsersHitList(context)
        utils = getToolByName(context,'plone_utils')
        if source is None and self.hasPermission():
            raise Unauthorized
        else:
            if source.hasRelationshipTo(context, relationship='bookmarked'):
                source.deleteReference(context, relationship='bookmarked')
                utils.addPortalMessage(_(u'Item successfully removed from your hitlist.'), 'info')
        self.request.response.redirect(source.absolute_url())

