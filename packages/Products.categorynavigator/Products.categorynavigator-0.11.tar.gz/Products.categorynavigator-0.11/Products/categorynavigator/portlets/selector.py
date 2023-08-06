from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.categorynavigator.categoryutils import CategoryUtils

from Products.categorynavigator import categorynavigatorMessageFactory as _

class ICategoryNavigatorPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    navigator = schema.TextLine(
        title=_(u"Send search to"),
        description=_(u"Which navigator should receive the search querys for this portlet"),
        default=u'search',
        required=True
    )
    
    description = schema.TextLine(
        title=_(u"Description"),
        description=_(u"Text to show on top of the category selector."),
        default=u'',
        required=False
    )
    
class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ICategoryNavigatorPortlet)

    def __init__(self, navigator=u'search', description=u''):
	self.navigator = navigator
	self.description = description

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Category Navigator Portlet"


class Renderer(base.Renderer, CategoryUtils):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('cn_portlet.pt')
    
    @property
    def available(self):
        if len(self.getSiteCategoriesAsList()) == 0:
            return False
        else:
            return True
    
    @property
    def Description(self):
	return self.data.description
    
    def generateQueryString(self, categories, adding=None, subtracting=None):
        '''Generates a URL querystring from a list of categories'''
        query = "/" + self.data.navigator + "?"
        finalCategories = list()
        
        if categories is not None:
            finalCategories = categories[:]
        
        if adding is not None:
            finalCategories.append(adding)
            
        if subtracting is not None:
            if subtracting in finalCategories:
                finalCategories.remove(subtracting)
        
        for cat in finalCategories:
            query = query + "Subject%3Alist=" + cat + "&"
        
        return query[:-1]


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ICategoryNavigatorPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ICategoryNavigatorPortlet)
