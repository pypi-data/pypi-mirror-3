from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.memoize.instance import memoize

class HitList(BrowserView):
    """personal hitlist
    """

    template = ViewPageTemplateFile('templates/hitlist.pt')

    def __call__(self):
        self.request.set('disable_border', True)

        return self.template()

    @memoize
    def getBookmarks(self):
        context = aq_inner(self.context)
        items = []
        for item in context.getBookmarks():
            items.append({'title' : item.Title(),
                          'item' : item,
                          'url' : item.absolute_url(),
                          'delete_url' : '%s/@@removefromhitlist' % item.absolute_url()})
        return items