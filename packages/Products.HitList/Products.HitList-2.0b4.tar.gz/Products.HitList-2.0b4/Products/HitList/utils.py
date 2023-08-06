from Products.CMFCore.utils import getToolByName
from AccessControl.User import nobody
from Acquisition import aq_parent

def getCurrentUsersHitList(context):
    mtool = getToolByName(context,'portal_membership')
    homefolder = mtool.getHomeFolder()
    if homefolder is not None:
        if 'hitlist' in homefolder.objectIds():
            return homefolder['hitlist']
    return None