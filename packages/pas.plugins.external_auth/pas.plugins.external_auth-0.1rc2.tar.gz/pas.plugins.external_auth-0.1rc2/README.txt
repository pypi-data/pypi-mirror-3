Introduction
============

This package propose a plugin for Zope PAS not only to manage authentication
from an external source, mostly HTTP headers provided by some SSO, thing it
does in a scriptable and highly configurable manner, but also to manage groups
definition, groups belonging, and users properties .

The use case this package was created for was to integrate a Shibboleth SSO for
Plone coupled with a group management application known as GROUPER, at
University of geneva. In our case, Shibboleth, the SSO, fill up headers from
GROUPER groups definitions and we needed them in Plone to manage local roles
and permissions.

Known Bugs
==========

The principle of solution relies on the ability of PAS to have multiple source
of users and group plugins. Unfortunatly ther is a bug in this feature
implementation both in Zope and Plone rewrite see `bug #12794`_ . Once this will be corrected undoubtely but
for those versions of plone and PAS for which it is not, you could use the
following monkey patch in __init__.py (this one is for Plone GroupsTool):

.. _`bug #12794`: http://dev.plone.org/ticket/12794

::

    from Products.PlonePAS.tools.groups import GroupsTool
    from AccessControl.requestmethod import postonly
    if not hasattr(GroupsTool, '_patched_ea__'):

        @postonly
        def removeGroup(self, group_id, keep_workspaces=0, REQUEST=None):
            """Remove a single group, including group workspace, unless
            keep_workspaces==true.
            """
            retval = False
            managers = self._getGroupManagers()
            if not managers:
                raise NotSupported, 'No plugins allow for group management'

            for mid, manager in managers:
                if manager.getGroupById(group_id):
                    if manager.removeGroup(group_id):
                        retval = True

            gwf = self.getGroupWorkspacesFolder()
            if retval and gwf and not keep_workspaces:
                grouparea = self.getGroupareaFolder(group_id)
                if grouparea is not None:
                    workspace_id = grouparea.getId()
                    if hasattr(aq_base(gwf), workspace_id):
                        gwf._delObject(workspace_id)

            self.invalidateGroup(group_id)
            return retval

        @postonly
        def addPrincipalToGroup(self, principal_id, group_id, REQUEST=None):
            managers = self._getGroupManagers()
            if not managers:
                raise NotSupported, 'No plugins allow for group management'
            for mid, manager in managers:
                if manager.getGroupById(group_id):
                    if manager.addPrincipalToGroup(principal_id, group_id):
                        return True
            return False

        @postonly
        def removePrincipalFromGroup(self, principal_id, group_id, REQUEST=None):
            managers = self._getGroupManagers()
            if not managers:
                raise NotSupported, 'No plugins allow for group management'
            for mid, manager in managers:
                if manager.getGroupById(group_id):
                    if manager.removePrincipalFromGroup(principal_id, group_id):
                        return True
            return False

        GroupsTool.removeGroup = removeGroup
        GroupsTool.addPrincipalToGroup = addPrincipalToGroup
        GroupsTool.removePrincipalFromGroup = removePrincipalFromGroup

        GroupsTool._patched_ea__ = True


Also, we just need to test the proxy part which we don't use actually, or
remove it. If you experience problem with it you should use the redirect to
external url scheme. Also with some versions of python this could not work
with https (because of a bug in old urllib2).

TODO
====

* Unit tests
* More Documentation
* redirect on logout url doesn't work
* Consistent profiles for use without Plone.

COPYLEFT
========
Copyright (C) 2012 Smile Suisse
See COPYING for copyright informations and LICENSE.txt for a copy of GPLv3
license in source package "docs" directory.
