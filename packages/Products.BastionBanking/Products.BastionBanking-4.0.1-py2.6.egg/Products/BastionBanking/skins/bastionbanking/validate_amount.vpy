## Controlled Python Script "validate_amount"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=amount=''
##title=Validates an amount is present and is a ZCurrency
##
from Products.BastionBanking.ZCurrency import ZCurrency

if not amount:
        state.setError('amount', 'failed to convert currency', 'input_required')
elif not isinstance(amount, ZCurrency):
        # see if we can coerce it ...
        try:
            amount = ZCurrency(amount)
        except:
            state.setError('amount', 'failed to convert currency - is the country code present?', 'input_required')

if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated errors.', 'error')
    return state.set(status='failure')

return state

