## Script (Python) "generateRelation"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=state_change
##title=
##
from zExceptions import NotFound
from Products.Relations.exception import ValidationException

wfTool           = context.portal_workflow
relationProposal = state_change.object
srcName          = relationProposal.getSearchKWA()
dstName          = relationProposal.getSearchKWB()
relation         = relationProposal.getRelation()

try:
    srcKP = context.portal_classification.getKeywordProposal(srcName)
    if wfTool.getInfoFor(srcKP, "review_state") == "private":
        wfTool.doActionFor(srcKP, "submit", comment="")
    if wfTool.getInfoFor(srcKP, "review_state") == "pending":
        wfTool.doActionFor(srcKP, "approve", comment="")
except NotFound:
    pass

try:
    dstKP = context.portal_classification.getKeywordProposal(dstName)
    if wfTool.getInfoFor(dstKP, "review_state") == "private":
        wfTool.doActionFor(dstKP, "submit", comment="")
    if wfTool.getInfoFor(dstKP, "review_state") == "pending":
        wfTool.doActionFor(dstKP, "approve", comment="")
except NotFound:
    pass

context.portal_classification.addReference(srcName, dstName, relation)
context.portal_classification.getKeyword(srcName).updateKwMap()
context.portal_classification.getKeyword(dstName).updateKwMap()

if not relationProposal.hasKeywordProposal():
    accepted_kws = context.portal_url.getPortalObject().accepted_kws
    relPropId    = relationProposal.getId()
    accepted_kws.manage_pasteObjects(relationProposal.getParentNode().manage_cutObjects(relPropId))
    raise state_change.ObjectMoved(getattr(accepted_kws, relPropId), relationProposal.aq_parent)
