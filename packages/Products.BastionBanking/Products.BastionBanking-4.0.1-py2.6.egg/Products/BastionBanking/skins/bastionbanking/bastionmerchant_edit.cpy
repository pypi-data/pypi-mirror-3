## Controller Python Script "bastionmerchant_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=mode,number_retention,store_identifier='',store_name='',title='',
##title=edit merchant attributes
##
context.manage_changeProperties(title=title,
                                mode=mode,
                                number_retention=number_retention,
				store_name=store_name,
                                store_identifier=store_identifier)

return state
