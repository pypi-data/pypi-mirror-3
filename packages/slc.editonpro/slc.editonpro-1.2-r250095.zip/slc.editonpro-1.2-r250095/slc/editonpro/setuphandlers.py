from zope.component import getUtility
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager

from Products.CMFCore.utils import getToolByName

def setupVarious(context):
    
    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a 
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    
    if context.readDataFile('slc.editonpro_various.txt') is None:
        return
                
    portal = context.getSite()
    #assignPortlets(portal)
        
    portal_props = getToolByName(portal, 'portal_properties')
    site_props = getattr(portal_props,'site_properties', None)
    attrname = 'available_editors'
    if site_props is not None:
        editors = list(site_props.getProperty(attrname)) 
        if 'EditOnPro' not in editors:
            editors.append('EditOnPro')
            site_props._updateProperty(attrname, editors)        
