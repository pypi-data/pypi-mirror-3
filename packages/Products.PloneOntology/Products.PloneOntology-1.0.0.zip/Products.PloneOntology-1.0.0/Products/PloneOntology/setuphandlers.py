# an 'import_various' step to deal with form controller settings
# as there seems to be no support for doing this via GS at the moment
# (December 7, 2007)
# also handling the creation of the archive for now

from Products.CMFCore.utils import getToolByName

def importVarious(context):
    """ Import various settings for PloneOntology

    This provisional handler will be removed again as soon as
    full handlers are implemented for this step.
    """
    site = context.getSite()
    addPFCsettings(site)
    addArchive(site)

    return "Added controls for the 'classify' action to " \
           "the form controller. Added the proposal archive."


def addPFCsettings(site):
    """Add controls for the 'classify' action to the form controller"""

    pfc = getToolByName(site, 'portal_form_controller')

    pfc.addFormAction('relations_adddelete', 'success','',
                      'Save', 'traverse_to',
                      'string:updateMap')
    pfc.addFormAction('relations_adddelete', 'failure','',
                      'Save', 'traverse_to',
                      'string:updateMap')
    pfc.addFormAction('base_edit', 'success','',
                      'search', 'traverse_to',
                      'string:base_edit')
    pfc.addFormAction('base_edit', 'success','',
                      'search2', 'traverse_to',
                      'string:base_edit')
    pfc.addFormAction('base_edit', 'success','',
                      'search3', 'traverse_to',
                      'string:classification_edit')
    pfc.addFormAction('base_edit', 'failure','',
                      'search4', 'traverse_to',
                      'string:classification_edit')
    pfc.addFormAction('base_edit', 'failure','',
                      'search5', 'traverse_to',
                      'string:classification_edit')
    pfc.addFormAction('base_edit', 'success','',
                      'search4', 'traverse_to',
                      'string:classification_edit')
    pfc.addFormAction('base_edit', 'success','',
                      'search5', 'traverse_to',
                      'string:classification_edit')
    pfc.addFormAction('base_edit', 'success','',
                      'add', 'traverse_to',
                      'string:classification_edit')
    pfc.addFormAction('base_edit', 'success','',
                      'delete', 'traverse_to',
                      'string:classification_edit')
    pfc.addFormAction('base_edit', 'success','',
                      'sel', 'traverse_to',
                      'string:classification_edit')
    pfc.addFormAction('base_edit', 'success','',
                      'sel2', 'traverse_to',
                      'string:classification_edit')
    pfc.addFormAction('base_edit', 'failure','',
                      'sel2', 'traverse_to',
                      'string:classification_edit')
    pfc.addFormAction('base_edit', 'success','',
                      'sel3', 'traverse_to',
                      'string:classification_edit')
    pfc.addFormAction('base_edit', 'failure','',
                      'sel3', 'traverse_to',
                      'string:classification_edit')
    pfc.addFormAction('base_edit', 'success','',
                      'add_search', 'traverse_to',
                      'string:classification_edit')
    


def addArchive(site):
    """ the keyword proposal storage """

    if 'accepted_kws' in site.objectIds():
        return
    pt=getToolByName(site, 'portal_types')
    pt.getTypeInfo('ProposalArchive').global_allow=True
    site.invokeFactory('ProposalArchive', id = 'accepted_kws',
                       title='Accepted Keyword Proposals',)
    getattr(site, 'accepted_kws')._updateProperty('exclude_from_nav', 1)
    catalog = getToolByName(site, 'portal_catalog')
    catalog.reindexObject(getattr(site, 'accepted_kws'))
    pt.getTypeInfo('ProposalArchive').global_allow=False

