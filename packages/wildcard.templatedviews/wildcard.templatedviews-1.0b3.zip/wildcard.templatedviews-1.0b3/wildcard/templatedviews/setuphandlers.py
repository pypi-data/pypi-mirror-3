from Products.CMFCore.utils import getToolByName


_types_to_add_to = (
    'Folder',
    'Large Plone Folder',
    'Document',
    'News Item',
    'Topic',
    'Event'
)

def install(context):
    
    site = context.getSite()
    pt = getToolByName(site, 'portal_types')
    for _type in _types_to_add_to:
        if _type in pt.objectIds():
            _type = pt[_type]
            _type.view_methods = tuple(set(_type.view_methods) | set(['templated-view']))
            
            