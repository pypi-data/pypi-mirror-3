from Products.Five import BrowserView
from Products.categorynavigator.categoryutils import CategoryUtils
from Acquisition import aq_inner
from zope.component import getUtility
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

try:
    from collective.contentleadimage.config import IMAGE_FIELD_NAME
    from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
    LEADIMAGE_EXISTS = True
except ImportException:
    LEADIMAGE_EXISTS = False
    
    
class SliderView(BrowserView):
    ''' View class for Slider view on collections '''
    
    def leadImageInstalled(self):
        return LEADIMAGE_EXISTS
    
    def trimDescription(self, desc, num):
        if len(desc) > num: 
                res = desc[0:num]
                lastspace = res.rfind(" ")
                res = res[0:lastspace] + " ..."
                return res
        else:
                return desc
    
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