## Script (Python) "extract_login"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=HTTP_HOST, SERVER_NAME, **k
##title=
##
# Example code:
if '8082' in HTTP_HOST:
    return SERVER_NAME + "3"
