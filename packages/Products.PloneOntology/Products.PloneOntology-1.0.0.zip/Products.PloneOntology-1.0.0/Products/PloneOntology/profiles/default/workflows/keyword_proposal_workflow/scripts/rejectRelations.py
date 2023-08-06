## Script (Python) "rejectRelations"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=state_change
##title=
##
# this script shall make all the referenced relationproposals of the keywordproposal to move along with it through the workflow

for refProp in state_change.object.getRefs('hasRelation'):
    context.portal_workflow.doActionFor(refProp, "reject", comment="")
