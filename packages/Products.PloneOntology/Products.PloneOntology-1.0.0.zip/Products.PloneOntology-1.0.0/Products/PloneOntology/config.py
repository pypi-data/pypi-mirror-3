from Globals import package_home
from Products.CMFCore import permissions as CMFCorePermissions


view_permission = CMFCorePermissions.ManagePortal

PROJECTNAME = 'PloneOntology'
GLOBALS = globals()
SKINS_DIR = 'skins'
ADD_CONTENT_PERMISSION = CMFCorePermissions.AddPortalContent

# Dependency products
# format is (productname, URL)
DEPENDENCIES = (
	("Relations", "http://plone.org/products/relations"),
	)


### graphviz configuration

# path to the graphviz layouter binaries (i.e. dot, neato, ...)
GV_BIN_PATH = ''
