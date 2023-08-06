## Script (Python) "generateKeyword"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=state_change
##title=
##
from Products.Relations.exception import ValidationException

# create keyword from proposal
kwProp  = state_change.object
kwTitle = kwProp.getKPTitle()
kwDesc  = kwProp.getKeywordProposalDescription()
kwSAD   = kwProp.getShortAdditionalDescription()
kwName  = kwProp.generateName(kwTitle, kwSAD)
#try:
kw      = context.portal_classification.addKeyword(kwName, kwTitle, kwDesc, kwSAD)
#except ValidationException:
#    state_change.getPortal().state.set(portal_status_message="'%s' is not a valid XML NCName" % kwName)
#    return
#except NameError:
#    state_change.getPortal().state.set(portal_status_message="'%s' already exists in current ontology" % kwName)
#    return
#except AttributeError:
#    pass

# approve all referenced relation proposals
wfTool = context.portal_workflow
for refProp in kwProp.getRefs('hasRelation'):
    if wfTool.getInfoFor(refProp, "review_state") == "pending":
        wfTool.doActionFor(refProp, "approve", commtent="")

kw.updateKwMap()

accepted_kws = context.portal_url.getPortalObject().accepted_kws
kwPropId     = kwProp.getId()
accepted_kws.manage_pasteObjects(kwProp.getParentNode().manage_cutObjects(kwPropId))
raise state_change.ObjectMoved(getattr(accepted_kws, kwPropId), kwProp.aq_parent)
