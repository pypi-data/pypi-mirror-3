from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple
from Products.PloneOntology.config import PROJECTNAME


def install(self):
    out = StringIO()

    tool=getToolByName(self, "portal_setup")

    if getFSVersionTuple()[:3]>=(3,0,0):
        tool.runAllImportStepsFromProfile(
                "profile-Products.PloneOntology:default",
                purge_old=False)
    else:
        plone_base_profileid = "profile-CMFPlone:plone"
        tool.setImportContext(plone_base_profileid)
        tool.setImportContext("profile-Products.PloneOntology:default")
        tool.runAllImportSteps(purge_old=False)
        tool.setImportContext(plone_base_profileid)

    print >> out, "Successfully installed %s" % PROJECTNAME

    return out.getvalue()
