## Script (Python) "temobj"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ctx, objid
##title=
##

request = container.REQUEST
response =  request.response

# Passing a context and an id
# Return an object

if ctx and objid:
   try:
      obj = ctx.restrictedTraverse(objid,None)
   except:
      obj = None

return obj
