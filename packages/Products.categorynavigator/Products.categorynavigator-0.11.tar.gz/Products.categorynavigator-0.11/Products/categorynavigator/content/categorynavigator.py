"""Definition of the Category Navigator content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from Products.categorynavigator.interfaces import ICategoryNavigator
from Products.categorynavigator.config import PROJECTNAME

CategoryNavigatorSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

CategoryNavigatorSchema['title'].storage = atapi.AnnotationStorage()
CategoryNavigatorSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    CategoryNavigatorSchema,
    folderish=True,
    moveDiscussion=False
)


class CategoryNavigator(folder.ATFolder):
    """type that permits searching and combining categories/subjects"""
    implements(ICategoryNavigator)

    meta_type = "CategoryNavigator"
    schema = CategoryNavigatorSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(CategoryNavigator, PROJECTNAME)
