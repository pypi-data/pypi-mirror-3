## Script (Python) "properties"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=property, current, login, user_id, **k
##title=
##
# Example code:

# allow users to overwrite their own properties
# in this case the propertysheet is just initialized once
#if current:
#    return current

# preferred to any if .. elif construct in case we have A LOT of properties
# to manage... not likely the case though
lazy = {
           'email': lambda: "%s@example.com" % login.lower(),
           'fullname': lambda: "%s %s" % (login.upper(), user_id.capitalize())
       }

return lazy.get(property, lambda: '')()
