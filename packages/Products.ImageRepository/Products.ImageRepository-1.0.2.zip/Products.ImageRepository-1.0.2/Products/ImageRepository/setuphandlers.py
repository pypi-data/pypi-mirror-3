from Products.CMFCore.utils import getToolByName

def setupKupu(context):
    """
    Setup kupu.
    """
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('imagerepository_kupu.txt') is None:
        return
    site = context.getSite()
    kt = getToolByName(site, 'kupu_library_tool', None)
    if kt is None:
        return

    types = kt.queryPortalTypesForResourceType('images')
    if types is None:
        kt.addResourceType('images', ('Image',))
    else:
        if 'Image' not in types:
            kt.addResourceType('images', tuple(types)+('Image',))
