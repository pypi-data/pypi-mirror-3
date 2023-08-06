## Python Script "object_rename"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Show the rename form for an object
##

url = '%s/@@multilanguage_rename' % (context.absolute_url())

context.REQUEST.RESPONSE.redirect(url)
