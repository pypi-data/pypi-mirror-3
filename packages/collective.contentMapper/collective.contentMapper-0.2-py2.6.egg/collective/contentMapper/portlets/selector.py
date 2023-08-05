from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from collective.contentMapper.categoryutils import CategoryUtils
from collective.contentMapper.interfaces import ICoordinatesList
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from collective.contentMapper import contentMapperMessageFactory as _

class IMapNavigatorPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    visualTitle = schema.TextLine(
        title=_(u"Title of the portlet"),
        description=_(u"The title that appears on top of the map'"),
        default=u'Locations',
        required=True
    )
    
    navigator = schema.TextLine(
        title=_(u"Send search to"),
        description=_(u"Which navigator should receive the search querys for this portlet. leave 'search' to use Plone search result page'"),
        default=u'search',
        required=True
    )
    
    rootCategory = schema.TextLine(
        title=_(u"Category"),
        description=_(u"Which virtual tree category root contains the region names to map"),
        default=u'',
        required=False
    )
    
class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IMapNavigatorPortlet)

    def __init__(self, navigator=u'search', rootCategory=u'', visualTitle=u'Locations'):
	self.navigator = navigator
	self.rootCategory = rootCategory
	self.visualTitle = visualTitle

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Map Navigator Portlet"


class Renderer(base.Renderer, CategoryUtils):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('mapNavigator.pt')
    
    @property
    def available(self):
        if len(self.getSiteCategoriesAsList()) == 0:
            return False
        else:
            return True
    
    @property
    def rootCategory(self):
	return self.data.rootCategory
    
    def Title(self):
	return self.data.visualTitle
    
    def getXPosition(self, region=None):
	if region is not None:
	    registry = getUtility(IRegistry)
	    list = registry.forInterface(ICoordinatesList)
	    for location in list.locations:
		values = location.split(",")
		if values[0] == region:
		    return int(values[1])
	    
	    return -1
	
    def getYPosition(self, region=None):
	if region is not None:
	    registry = getUtility(IRegistry)
	    list = registry.forInterface(ICoordinatesList)
	    for location in list.locations:
		values = location.split(",")
		if values[0] == region:
		    return int(values[2])
	    
	    return -1
	
    def getPositionCSSFor(self, cat):
	x = self.getXPosition(cat) - 4
	y = self.getYPosition(cat) - 4
	if x != -5:
	    return 'position:absolute; top:%spx; left:%spx;'%(y, x)
	else:
	    return 'display:none'
	    
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
    form_fields = form.Fields(IMapNavigatorPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IMapNavigatorPortlet)
