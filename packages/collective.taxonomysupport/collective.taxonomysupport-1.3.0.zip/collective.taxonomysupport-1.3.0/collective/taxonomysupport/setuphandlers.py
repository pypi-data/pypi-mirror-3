# -*- coding: utf-8 -*-
"""
@author: andrea cecchi
"""

def Handlers(context):
    if context.readDataFile('collective.taxonomysupport_various.txt') is None:
        return
    portal = context.getSite()
    addKeyToCatalog(context, portal)

def addKeyToCatalog(context, portal):
    '''
    @summary: takes portal_catalog and adds a key to it
    @param context: context providing portal_catalog 
    '''
    pc = portal.portal_catalog
    pl = portal.plone_log

    indexes = pc.indexes()
    for idx in getKeysToAdd():
        if idx[0] in indexes:
            pl("Found the '%s' index in the catalog, nothing changed.\n" % idx[0])
        else:
            pc.addIndex(name=idx[0], type=idx[1], extra=idx[2])
            pl("Added '%s' (%s) to the catalog.\n" % (idx[0], idx[1]))
 
def getKeysToAdd():
    '''
    @author: andrea cecchi
    @summary: returns a tuple of keys that should be added to portal_catalog
    '''
    return (('SiteAreas','KeywordIndex',{'indexed_attrs': 'SiteAreas', }),
            ('getSiteAreas','KeywordIndex',{'indexed_attrs': 'getSiteAreas', }),)
