## Script (Python) "content_edit_apply"
##title=Edit content
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id=''
##
#Save changes normal way
state = context.content_edit_impl(state, id)
state.setNextAction('redirect_to_action:string:edit')
return state
