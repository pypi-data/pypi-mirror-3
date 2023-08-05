##Controlled Python Script "validate_payee_account"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=payee_account=''
##title=Validates presence and format of payee account details
##
 
if not payee_account:
    state.setError('payee_account', 'Input is required but no input given.', 'input_required')
 
if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')
else:
    return state
 

