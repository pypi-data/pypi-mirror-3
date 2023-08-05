## Script (Python) "rendezvous_edit_script"
##title=Edit content
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id=''
##
from Products.CMFCore.utils import getToolByName

#Save changes normal way
state = context.content_edit_impl(state, id)
context = state.getContext()
uid = context.UID()
try:
    del context.REQUEST.SESSION['rendezvous'][uid]
except KeyError:
    pass
state.setNextAction('redirect_to:string:edit_dates')
return state
