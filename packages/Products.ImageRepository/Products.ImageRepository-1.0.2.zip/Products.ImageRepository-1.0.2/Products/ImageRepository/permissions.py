from Products.CMFCore.permissions import setDefaultRoles

AddImageRepositoryContent = 'ImageRepository: Add content'
setDefaultRoles(AddImageRepositoryContent, ('Manager',))
