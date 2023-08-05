## Script (Python) "renderSource"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=lines
##title=format source text as html
##
from Products.PythonScripts.standard import html_quote

return '<br>'.join( map(lambda x: html_quote(x), lines) )


