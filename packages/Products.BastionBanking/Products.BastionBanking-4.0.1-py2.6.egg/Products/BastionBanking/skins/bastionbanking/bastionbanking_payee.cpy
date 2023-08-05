## Controller Python Script "bastionbanking_payee"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=payee_account,payee_instructions=''
##title=edit payee details
##

context.updateProperty('payee_account', payee_account)
if payee_instructions:
   context.updateProperty('payee_instructions', payee_instructions)

return state
