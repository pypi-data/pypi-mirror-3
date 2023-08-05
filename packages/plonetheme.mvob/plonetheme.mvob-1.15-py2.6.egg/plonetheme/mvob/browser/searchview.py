from Products.Five import BrowserView
from Products.categorynavigator.categoryutils import CategoryUtils
from Acquisition import aq_inner
from zope.component import getUtility, getMultiAdapter
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from plonetheme.mvob.browser.interfaces import ISearchView
from zope.interface import implements, Interface

try:
    from collective.contentleadimage.config import IMAGE_FIELD_NAME
    from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
    LEADIMAGE_EXISTS = True
except ImportException:
    LEADIMAGE_EXISTS = False

class SearchView(BrowserView,):
    implements(ISearchView)
    
    def leadImageInstalled(self):
        return LEADIMAGE_EXISTS
    
    def base_url(self):
        """If context is a default-page, return URL of folder, else
        return URL of context.
        """
        return str(getMultiAdapter((self.context, self.request,), name=u'absolute_url'))
    
    def getDescriptionOrBobySegment(self, item):
        '''Returns a description of the item or, if it does not exist, the first 240 characters of the body'''
        if item.Description == "":
            return self.trimDescription(self.StripTags(self.deleteTag(item.getObject().getText(), "h2")), 240)
        else:
            return item.Description
            
    def StripTags(self, text):
        '''Strips HTML tags and returns text only'''
        finished = 0 
        while not finished: 
            finished = 1 
            start = text.find("<") 
            if start >= 0: 
                stop = text[start:].find(">") 
                if stop >= 0: 
                    text = text[:start] + text[start+stop+1:] 
                    finished = 0 
        return text


    def deleteTag(self, text, tagName):
        '''Strips HTML tags and returns text only'''
        finished = 0 
        while not finished: 
            finished = 1 
            start = text.find("<"+tagName) 
            if start >= 0: 
                stop = text.find("</" + tagName +">") 
                if stop >= 0: 
                    if start == 0:
                        text = text[stop+3+len(tagName):]
                    else:
                        text = text[0:start-1] + text[stop+3+len(tagName):]
                    finished = 0 
        return text
    
    def trimDescription(self, desc, num):
        if len(desc) > num: 
                res = desc[0:num]
                lastspace = res.rfind(" ")
                res = res[0:lastspace] + " ..."
                return res
        else:
                return desc

    def getUrlWithQueryString(self, item, categories):
        url = ""
        if hasattr(item, 'getURL'):
            url = item.getURL()
        else:
            url = item.absolute_url()
        
        url = url + self.generateQueryString(categories)
        return url
        
    def getAllResultsHere(self, context):
        '''Malkes the search for all the items in this folder'''
        catalog = self.tools().catalog()
        folder_path = '/'.join(context.getPhysicalPath())
        types = ('Document', 'Event', 'News Item', 'InfoBlad')
        results = catalog.searchResults(path={'query': folder_path, 'depth': 1}, sort_on="Date", sort_order="reverse", portal_type=types, batch=True)
        return results
    
    def getFirstImage(self, item, scale='mini'):
        '''Get the first image inside a folderish item'''
        plone_utils = getToolByName(self, 'plone_utils')
        if plone_utils.isStructuralFolder(item):
            catalog = getToolByName(self, 'portal_catalog')
            folder_url = '/'.join(item.getObject().getPhysicalPath())
            results = catalog.searchResults(path = {'query': folder_url, 'depth': 1}, sort_on = 'getObjPositionInParent', sort_order='ascending', portal_type = ('Image'))
            if len(results) > 0:
                image = results[0]
                tag = '<img class="tileImage" src="' + image.getURL() + '/image_' + scale + '" />'
                return tag
            else:
                return ''
        
        return ''
    
    @property
    def prefs(self):
        if LEADIMAGE_EXISTS:
            portal = getUtility(IPloneSiteRoot)
            return ILeadImagePrefsForm(portal)
        else:
            return None

    def tag(self, obj, css_class='tileImage', scale='mini'):
        if LEADIMAGE_EXISTS:
            context = aq_inner(obj)
            field = context.getField(IMAGE_FIELD_NAME)
            if field is not None:
                if field.get_size(context) != 0:
                    return field.tag(context, scale=scale, css_class=css_class)
            return ''
        else:
            return ''
	
