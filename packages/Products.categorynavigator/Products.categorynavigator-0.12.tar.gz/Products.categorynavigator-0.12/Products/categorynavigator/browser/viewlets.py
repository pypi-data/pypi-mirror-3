from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from Products.categorynavigator.categoryutils import CategoryUtils
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Acquisition import aq_base, aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase
from zope.component import getMultiAdapter
import time
import string
from zope.interface import implements
from Acquisition import aq_inner
from zope.component import getUtility
from Products.CMFPlone.interfaces import IPloneSiteRoot

class BreadCrumbs (BrowserView, CategoryUtils):
    """
    Breadcrumbs for category navigator
    """
    implements(IViewlet)
    render = ViewPageTemplateFile('breadcrumbs.pt')

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager
	
    
    def getUrlWithQueryString(self, item, categories):
        url = ""
        if hasattr(item, 'getURL'):
            url = item.getURL()
        else:
            url = item.absolute_url()
        
        url = url + self.generateQueryString(categories)
        return url 
    
    def getUrlWithQueryStringUpTo(self, cat, categories):
	portal_url = getToolByName(self.context, "portal_url")
	portal = portal_url.getPortalObject()

	url = portal.absolute_url() + '/maatregelen'
	
	newCategories = []
	for item in categories:
	    if item != cat:
		newCategories.append(item)
	    else:
		newCategories.append(item)
		break
        
        url = url + self.generateQueryString(newCategories)
        return url
    
    def getPortalUrl(self):
	portal_url = getToolByName(self.context, "portal_url")
	portal = portal_url.getPortalObject()
	return portal.absolute_url()
