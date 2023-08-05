## Controller Python Script "bastionmerchant_pay"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=amount, reference='', return_url=''
##title=make a payment
##
from Products.BastionBanking.ZCurrency import ZCurrency

context.manage_pay(ZCurrency(amount), 
                   reference, 
                   return_url, 
                   context.REQUEST)

return state
