## Controller Python Script "bastionmerchant_payments"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ids=[]
##title=do payment actions
##
request = context.REQUEST

if request.has_key('form.button.Reconcile'):
    for id in ids:
        pmt = getattr(context, id)
        context.manage_reconcile(pmt)
elif request.has_key('form.button.Refund'):
    for id in ids:
        pmt = getattr(context, id)
        context.manage_refund(pmt)
elif request.has_key('form.button.Cancel'):
    for id in ids:
        pmt = getattr(context, id)
        pmt.manage_changeStatus('cancel')
elif request.has_key('form.button.Accept'):
    for id in ids:
        pmt = getattr(context, id)
	pmt.manage_changeStatus('accept')

return state
