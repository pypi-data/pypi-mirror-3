## Controller Python Script "validate_creditcard"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=validates that credit card details are present and look vaguely ok
##parameters=cc_type='',cc_number='',cc_year='',cc_month='',cc_name='',cc_cvv2=''

if not cc_type:
    state.setError('cc_type', 'No Type')

if not cc_year:
    state.setError('cc_expiry', 'No Expiry Year')

if not cc_month:
    state.setError('cc_expiry', 'No Expiry Month')

if not cc_number:
    state.setError('cc_number', 'No Number')

if not cc_name:
    state.setError('cc_name', 'No Name')

if not cc_cvv2:
    state.setError('cc_cvv2', 'No Card Security Code')


from DateTime import DateTime
from Products.BastionBanking.ZCreditCard import ZCreditCard, CreditCardExpired

try:
    card = ZCreditCard(cc_number, DateTime('%s/%s/01' % (cc_year, cc_month)), cc_type, cc_name, cc_cvv2)
except Exception, e:
    state.setError('cc_number', 'Card details incorrect: %s' % str(e))
else:
    try:
   	card.validate()
    except CreditCardExpired:
        state.setError('cc_expiry', 'Card Expired')
    except Exception, e:
        state.setError('cc_number', 'Invalid Card Number: %s' % str(e))


if state.getErrors():
    context.plone_utils.addPortalMessage('Please correct the indicated credit card errors.', 'error')
    return state.set(status='failure')

return state
