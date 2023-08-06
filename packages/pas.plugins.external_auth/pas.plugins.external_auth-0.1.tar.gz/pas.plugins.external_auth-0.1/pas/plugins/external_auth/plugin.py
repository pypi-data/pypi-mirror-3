"""PAS plugin for external authentication"""

import re, random
from string import letters, digits, punctuation
from urllib import quote
from urllib2 import urlopen, ProxyHandler, ProxyBasicAuthHandler, \
                HTTPBasicAuthHandler, HTTPPasswordMgrWithDefaultRealm as pwd_mgr
from logging import getLogger
from time import sleep
from random import randint

from zope.interface import implements, Interface
import transaction
from ZODB.POSException import ConflictError
from OFS.Folder import Folder
import Products
from AccessControl import ClassSecurityInfo
try:
    from AccessControl.class_init import InitializeClass
except ImportError: # plone 3.3
    from Globals import InitializeClass
from AccessControl.Permissions import manage_users
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.Expression import Expression
from Products.PageTemplates.Expressions import getEngine, SecureModuleImporter
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin, \
        ILoginPasswordHostExtractionPlugin, IAuthenticationPlugin, \
        IUserEnumerationPlugin, IGroupEnumerationPlugin, IChallengePlugin, \
        ICredentialsResetPlugin

def manage_add(container, id="external_auth", title='', REQUEST=None):
    """Add a  to a Pluggable Authentication Services."""
    o = ExternalAuthPlugin(id, title)
    id = o.getId()
    container._setObject(id, o)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(
               '%s/manage_workspace?manage_tabs_message=%s+successfully+added.'
                % (id, container.absolute_url()))

tal_doc = ('TALES expression. Headers are available in context as variables, '
           'as are more common "here", "modules", and "re" (the '
           'standard re module). Are also avilable login except in '
           'login_header, and user_id in group_header.')

def expr_context(context, headers, **data):
    '''%s
    
    ''' % tal_doc

    data['here'] = context
    data['modules'] = SecureModuleImporter
    data['re'] = re
    data['headers'] = headers
    data.update(headers)
    return getEngine().getContext(data)

random.seed()

def _make_pass():
    chars = letters + digits + punctuation
    return ''.join(random.sample(chars, 8))

_external_auth = _make_pass()

log = getLogger('ExternalAuthPlugin')

class IExternalAuthPlugin(Interface): pass

class ExternalAuthPlugin(BasePlugin, Folder):
    """This plugin implements authentication."""

    implements(IExternalAuthPlugin, ILoginPasswordHostExtractionPlugin,
               IAuthenticationPlugin, IChallengePlugin, ICredentialsResetPlugin)

    meta_type = "External authentication"
    security  = ClassSecurityInfo()

    manage_options = ({'label': 'configure',
                       'action': 'manage_configure'},
                     ) + (Folder.manage_options[0],
                     ) + BasePlugin.manage_options

    _properties = Folder._properties + BasePlugin._properties + (
                {'id': 'user_container',
                 'label': "External User Folder",
                 'type': 'string', 'mode': 'w'},
                {'id': 'group_container',
                 'label': "External Group Manager (works with "
                          "IZODBManagerInterface for removePrincipalFromGroup "
                          "and addPrincipalToGroup, a shame we don't have some "
                          "IGroupContainer)",
                 'type': 'string', 'mode': 'w'},
                {'id': 'uid_header',
                 'label': "Header to take the uid from." + tal_doc,
                 'type': 'string', 'mode': 'w'},
                {'id': 'login_header',
                 'label': "Header to take the login from." + tal_doc,
                 'type': 'string', 'mode': 'w'},
                {'id': 'groups_header',
                 'label': "Header to take the list of groups from." + tal_doc,
                 'type': 'string', 'mode': 'w'},
                {'id': 'use_in_session_cache',
                 'label': "Whether to cache credentials in SESSION object.",
                 'type': 'boolean', 'mode': 'w'},
                {'id': 'log_error_message',
                 'label': "Whether to log errors in tales expressions.",
                 'type': 'boolean', 'mode': 'w'},
                {'id': 'login_script_name',
                 'type': 'string', 'mode': 'w'},
                {'id': 'uid_script_name',
                 'type': 'string', 'mode': 'w'},
                {'id': 'groups_script_name',
                 'type': 'string', 'mode': 'w'},
                {'id': 'up_script_name',
                 'type': 'string', 'mode': 'w'},
                {'id': 'redirect_to_external_auth',
                 'type': 'boolean', 'mode': 'w'},
                {'id': 'external_login_url',
                 'type': 'string', 'mode': 'w'},
                {'id': 'redirect_logout',
                 'type': 'boolean', 'mode': 'w'},
                {'id': 'external_logout_url',
                 'type': 'string', 'mode': 'w'},
                {'id': 'http_login',
                 'type': 'string', 'mode': 'w'},
                {'id': 'http_password',
                 'type': 'string', 'mode': 'w'},
                {'id': 'proxy_url',
                 'type': 'string', 'mode': 'w'},
                {'id': 'proxy_login',
                 'type': 'string', 'mode': 'w'},
                {'id': 'proxy_password',
                 'type': 'string', 'mode': 'w'})

    def __init__(self, id, title=''):
        self.id = id
        self.title = title
        self.user_container = ''
        self.group_container = ''
        self.uid_header = ''
        self.login_header = ''
        self.groups_header = ''
        self.use_in_session_cache = False
        self.log_error_message = True
        self.login_script_name = ''
        self.uid_script_name = ''
        self.groups_script_name = ''
        self.up_script_name = ''
        self.redirect_to_external_auth = False
        self.external_login_url = ''
        self.redirect_logout = False
        self.external_logout_url = ''
        self.http_login = ''
        self.http_password = ''
        self.proxy_url = ''
        self.proxy_login = ''
        self.proxy_password = ''
 
    security.declarePublic('all_meta_types')
    def all_meta_types(self):
        "Container filter"
        allow = ('Script (Python)', 'External Method','Z SQL Method')
        return (x for x in Products.meta_types if x['name'] in allow)

    # PAS interface

    security.declarePrivate('resetCredentials')
    def resetCredentials(self, request, response):
        tales = self.external_logout_url
        rget = request.get
        if tales:
            from_ = rget('HTTP_REFERER', '')
            from_ = from_ or rget('ACTUAL_URL', '')
            try:
                url = Expression(tales)(expr_context(self, {},
                                        came_from=quote(from_)))
            except Exception, e:
                self._error_occured_in_tales('Error evaluating expression "%s" '
                     'determining external auth url used to logout.' % tales, e)
            if self.redirect_logout:
                response.redirect(url, lock=1)
            else:
                http_auth = HTTPBasicAuthHandler(pwd_mgr())
                if self.http_login:
                    http_auth.add_password(realm=None, uri=url,
                                           user=self.http_login,
                                           passwd=self.http_password)

                proxy_auth = ProxyBasicAuthHandler(pwd_mgr())
                if self.proxy_url:
                    proxy_support = ProxyHandler({'http': self.proxy_url,
                                                  'https': self.proxy_url})
                    if self.proxy_login:
                        proxy_auth.add_password(realm=None, uri=self.proxy_url,
                                                user=self.proxy_login,
                                                passwd=self.proxy_password)

                else: # take it from env
                    proxy_support = ProxyHandler()

                opener = build_opener(proxy_support, http_auth, proxy_auth)
                res = urlopen(url)

    security.declarePrivate('challenge')
    def challenge(self, request, response, **kw ):
        '''Largely inspired by PAS cookie auth helper.'''
 
        # redirect to external url
        if self.redirect_to_external_auth:
            url = self.get_login_url(request)
            if not (url and url.strip()) \
           and request.AUTHENTICATED_USER.getUserName() != 'Anonymous User':
                # Could not challenge.
                return 0
            response.redirect(url, lock=1)
            return 1

        # let visitors choice how to login
        else:
            # For simplicity let other plugins manage challenge, EA profiles
            # should override templates of those plugins to implement link to
            # external auth
            return 0

    security.declarePublic('get_login_url')
    def get_login_url(self, request):

        rget = request.get

        tales = self.external_login_url
        came_from = rget('came_from', None)

        if came_from is None:
            came_from = rget('ACTUAL_URL', '')
            query = rget('QUERY_STRING')
            if query:
                if not query.startswith('?'):
                    query = '?' + query
                came_from = came_from + query

        url = ''
        try:
            url = Expression(tales)(expr_context(self, request.environ,
                                    came_from=quote(came_from)))
        except Exception, e:
            self._error_occured_in_tales('Error evaluating expression "%s" '
                         'determining external auth url.' % tales, e)
        return url

    security.declarePrivate('extractCredentials')
    def extractCredentials(self, request):
        env = request.environ
        rget = env.get

        # extract login
        tales = self.login_header
        try:
            login = Expression(tales)(expr_context(self, env))
        except Exception, e:
            self._error_occured_in_tales('Error evaluating expression "%s" for '
                                'determining login of user.' % tales, e)
            return {}
        if not login:
            return {}

        # ILoginPasswordHostExtractionPlugin
        remote_host = rget('REMOTE_HOST', '')
        password = _external_auth + self.id
        try:
            remote_address = request.getClientAddr()
        except AttributeError:
            remote_address = ''

        # compute user
        user_id = self.uid_header
        if user_id:
            try:
                user_id = Expression(user_id)(expr_context(self, env,
                                                           login=login))
            except Exception, e:
                self._error_occured_in_tales('Error evaluating expression "%s" '
                                     'for id of user "%s".' % (tales, login), e)
                return {}
        else:
            user_id = login

        creds =  {'login': login, 'password': password,
                  'remote_host': remote_host, 'remote_address': remote_address,
                  'user_id': user_id}

        if self.use_in_session_cache:
            session = request.SESSION
            creds['session'] = session
            if session.has_key(login):
                return creds

        # compute groups
        tales = self.groups_header
        try:
            groups = Expression(tales)(expr_context(self, env, login=login,
                                                    user_id=user_id))
        except Exception, e:
            self._error_occured_in_tales('Error evaluating expression "%s" '
                                'for groups of user "%s".' % (tales, login), e)
            groups = ()

        creds['groups'] = groups and set(groups) or set()

        # compute user properties
        creds['user_properties'] = {}
        for prop in (e for e in self.propertyIds() if e.startswith('uprop_')):
            name = prop[6:]
            tales = self.getProperty(prop)
            # execution is retarded after user construction
            creds['user_properties'][name] = env, tales

        return creds

    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
      try:
        password = credentials.get('password', '')
        if password != _external_auth + self.id: # not for us
            return 

        login = credentials['login']
        user_id = credentials['user_id']

        if self.use_in_session_cache:
            session = credentials['session']

            if session.has_key(login):
                uid = session[login]
                if uid == user_id:
                    return user_id, login
                else: # something wrong
                    return

        groups = credentials['groups']

        pas = self._getPAS()
        pas_get = pas._getOb

        # create user if he doesn't exists
        user = pas.getUserById(user_id)
        if not user:
            try:
                cu = pas_get(self.user_container)
                cu.addUser(user_id, login, _make_pass())
            except Exception, e:
                log.error('Could not add user "%s" with login "%s" for the '
                          'following reason:' % (user_id, login))
                log.exception(e)
                return
            user = pas.getUserById(user_id)

        # update user property sheets if necessary
        none = object()
        for prop, (env, tales) in credentials['user_properties'].items():
            try:
                orig = none
                for s in user.listPropertysheets():
                    tries = 0
                    while True:
                        if user[s].hasProperty(prop):
                            orig = user[s].getProperty(prop)
                            value = Expression(tales)(expr_context(self, env,
                                                      groups=groups,
                                                      login=login,
                                                      user_id=user_id,
                                                      property=prop,
                                                      current=orig))
                            if orig != value:
                                try:
                                    transaction.begin()
                                    # <FIXME>
                                    # This from PlonePas MutablePropertySheet
                                    # API better idea ?
                                    user[s].setProperty(user, prop, value)
                                    # </FIXME>
                                    transaction.commit()
                                    log.debug('Update property "%s" : "%s" -> '
                                              '"%s" of %s' % (prop, orig,
                                                              value, login))
                                except ConflictError:
                                    transaction.abort()
                                    tries += 1
                                    if tries > 2:
                                        log.error('Not updating %s for %s due '
                                                  'to too much conflicts.'
                                                  % (prop, login))
                                        break
                                    else:
                                        sleep(randint(1, 9)/10.)
                                break
                            break
                        break
                if orig is none:
                    log.error('No such a property "%s" defined for user %s"'
                              % (prop, login))
                    continue
            except Exception, e:
                log.error('Could not retrieve or update property "%s" defined '
                          'for user %s"' % (prop, login))
                log.exception(e)
                continue

        # update groups for user
        gc = groups and self.group_container
        if gc:
            # create groups if they doesn't exists
            existing = set(g['groupid'] for g in pas.searchGroups())
            for g in groups - existing:
                try:
                    pas_get(gc).addGroup(g, title=g, description='Automatically'
                                                      ' added by %s.' % self.id)
                except Exception, e:
                    log.error('Could not add group "%s" for the '
                              'following reason:' % g)
                    log.exception(e)

        # update groups properties

        # original PAS doesn't define add/remove group for principal API
        gms = pas.plugins.listPlugins(IGroupEnumerationPlugin)
        gms = [ e for e in pas.plugins.listPlugins(IGroupsPlugin) if e in gms ]
        # retrieve the groups for principal but only for groups manager that
        # support addition/deletion (AutoGroups for example doesn't).
        def duck_type(obj):
            return hasattr(obj, 'removePrincipalFromGroup'
             ) and hasattr(obj, 'addPrincipalToGroup')
        old_groups = set.union(*(set(gm.getGroupsForPrincipal(user))
                              for _, gm in gms if duck_type(gm)))

        # remove user from old groups
        for g in old_groups - groups:
            for _, gm in gms:
                if g in (e['id'] for e in gm.enumerateGroups()):
                    try:
                        gm.removePrincipalFromGroup(user_id, g)
                    except Exception, e:
                        log.error('Could not remove %s to group "%s" for the '
                                  'following reason:' % (user_id, g))
                        log.exception(e)
                    log.debug('Removed %s from %s in %s.' % (user_id, g, _))

        # add user to new groups
        for g in groups - old_groups:
            for _, gm in gms:
                if g in (e['id'] for e in gm.enumerateGroups()):
                    try:
                        gm.addPrincipalToGroup(user_id, g)
                    except Exception, e:
                        log.error('Could not add %s to group "%s" for the '
                                  'following reason:' % (user_id, g))
                        log.exception(e)
                    log.debug('Added %s to %s in %s.' % (user_id, g, _))

        log.debug('Authenticated as %s.' % user_id)
        if self.use_in_session_cache:
            session[login] = user_id
        return user_id, login
      except Exception, e: log.exception(e)

    # utility

    def _error_occured_in_tales(self, msg, exc):
        if self.log_error_message:
            log.error(msg)
            log.exception(exc)

    # zmi methods

    security.declareProtected(manage_users, 'manage_configure')
    manage_configure = PageTemplateFile("manage_configure.pt", globals())

    security.declareProtected(manage_users, 'user_containers')
    def user_containers(self):
        list_plugins = self._getPAS().plugins.listPlugins
        return tuple(e for e, _ in list_plugins(IUserEnumerationPlugin))

    security.declareProtected(manage_users, 'group_containers')
    def group_containers(self):
        list_plugins = self._getPAS().plugins.listPlugins
        return tuple(e for e, _ in list_plugins(IGroupEnumerationPlugin))

    security.declareProtected(manage_users, 'get_managed_user_properties')
    def get_managed_user_properties(self):
        return tuple(dict((('name', e[6:]), ('id', e),
                           ('use_default', self.getProperty(e.replace(
                                                'uprop_', 'udef_', 1))),
                           ('tal', self.getProperty(e)),
                                       )) for e in self.propertyIds()
                                           if e.startswith('uprop_'))

    security.declareProtected(manage_users, 'manage_update_ea')
    def manage_update_ea(self, user_container, group_container,
                               login_script_name, uid_script_name,
                               groups_script_name, up_script_name,
                               **form):
        fg = form.get

        # global section
        self.use_in_session_cache = bool(fg('use_in_session_cache', False))
        self.log_error_message = bool(fg('log_error_message', False))
        self.redirect_to_external_auth = bool(fg('redirect_to_external_auth',
                                                 False))
        self.external_login_url = fg('external_login_url', '')
        self.redirect_logout = bool(fg('redirect_logout', False))
        self.external_logout_url = fg('external_logout_url', '')
        self.http_login = fg('http_login', '')
        self.http_password = fg('http_password', '')
        if fg('use_proxy', False):
            self.proxy_url = fg('proxy_url', '')
            self.proxy_login = fg('proxy_login', '')
            password = fg('proxy_password', '')
            if password.strip():
                self.proxy_password = fg('proxy_password', '')
        else:
            self.proxy_url = ''
            self.proxy_login = ''
            self.proxy_password = ''

        # tales definition

        def call_expr(script, params):
            return 'python: here.%s(%s)' % (script, ', '.join(params))

        login_params = '**headers',
        user_id_params = ('login=login',) + login_params
        groups_params = ('user_id=user_id',) + user_id_params
        up_params = ('groups=groups', 'current=current', 'property=property',
                    ) + groups_params

        # user section

        self.user_container = user_container.strip()
        if login_script_name.strip():
            self.login_script_name = login_script_name
            self.login_header = call_expr(login_script_name, login_params)
        else:
            self.login_script_name = ''
            self.login_header = fg('login_header', '')

        if uid_script_name.strip():
            self.uid_script_name = uid_script_name
            self.uid_header = call_expr(uid_script_name, uid_params)
        else:
            self.uid_script_name = ''
            self.uid_header = fg('uid_header', '')

        # group section 

        self.group_container = group_container.strip()

        if groups_script_name.strip():
            self.groups_script_name = groups_script_name
            self.groups_header = call_expr(groups_script_name, groups_params)
        else:
            self.groups_script_name = ''
            self.groups_header = fg('groups_header', '')

        # user properties section

        if up_script_name.strip():
            self.up_script_name = up_script_name
            _up_expr = call_expr(up_script_name, up_params)
        else:
            _up_expr = None
            self.up_script_name = ''

        for m in self.get_managed_user_properties():
            id = m['id']
            id_def = m['id'].replace('uprop_', 'udef_', 1)
            if fg('delete_' + id, False):
                self.manage_delProperties((id, id_def))
            else:
                use_default = fg('use_default_' + id, False)
                self.manage_changeProperties(**{id_def: use_default})
                if use_default:
                    self.manage_changeProperties(**{id: _up_expr})
                else:
                    self.manage_changeProperties(**{id: fg('tal_' + id)})

        add_prop = fg('add_prop', '')
        if add_prop.strip():
            self.manage_addProperty('uprop_' + add_prop, '', 'string')
            self.manage_addProperty('udef_' + add_prop, True,
                                    'boolean')

    # strange bug on my zope/plone 4.1 where self.objectIds is
    # Folder.objectValues
    objectIds = Folder.objectIds
    objectItems = Folder.objectItems

InitializeClass(ExternalAuthPlugin)
