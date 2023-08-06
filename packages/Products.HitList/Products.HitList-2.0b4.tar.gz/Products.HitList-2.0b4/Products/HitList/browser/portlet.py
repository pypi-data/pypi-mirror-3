from Acquisition import aq_inner, aq_parent
from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.HitList.utils import getCurrentUsersHitList
from Products.HitList import HitListMessageFactory as _

class IHitListPortlet(IPortletDataProvider):
    """A portlet showing a users Hitlist
    """

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    implements(IHitListPortlet)
    title = _(u"Hitlist portlet")

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    render = ViewPageTemplateFile('templates/portlet.pt')
    
    @property
    def list(self):
        return getCurrentUsersHitList(self.context)
    
    @property
    def available(self):
        self.update()
        if not self.list:
            return 0
        return bool(self.list.getBookmarks())

    @memoize
    def getBookmarks(self):
        items = []
        for item in self.list.getBookmarks():
            items.append({'title' : item.Title(),
                          'item' : item,
                          'url' : item.absolute_url(),
                          'delete_url' : '%s/@@removefromhitlist' % item.absolute_url()})
        return items

class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
