from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin, IUserEnumerationPlugin, IRolesPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from OFS.Cache import Cacheable
from App.class_init import default__class_init__ as InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo

import config

manage_addEasyUserAuthenticationForm = PageTemplateFile(
    'www/addEasyUserAuthentication', globals(),
    __name__='manage_addEasyUserAuthenticationForm' )

def manage_addEasyUserAuthentication( context,
                                      id, title=None, REQUEST=None ):
    " "

    eua = EasyUserAuthentication(id, title)
    context._setObject(eua.getId(), eua)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
                                '%s/manage_workspace'
                                '?manage_tabs_message='
                                'EasyUserAuthentication+added.'
                            % context.absolute_url())

import imaplib

cache = {}

def authenticate(login, password):
    # Fairly safe to put cache here, as there is no
    # known way to access that variable from regular
    # Zope.
    #
    # OTOH, the cache isn't used it seems, as some
    # sort of caching is happening before authenticate
    # is called.
    global cache
    if cache.has_key(login):
        print 'getting from cache'
        return cache[login] == password
    connection = imaplib.IMAP4(config.authentication_server)
    connection.login(login, password)
    cache[login] = password

class EasyUserAuthentication(BasePlugin):
    """ PAS plugin for easy user authentication systems, intended for copying
        and implementation of connectivity with other authentication backends.
    """

    meta_type = 'Easy User Authenticaton plugin'

    security = ClassSecurityInfo()

    def __init__(self, id, title=''):

        self._id = self.id = id
        self.title = title
        self._known_users = ()

    # Activate interfaces;  anyone know a more correct approach?
    def manage_afterAdd(self, *arguments, **keywords):
        from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
        import cStringIO
        activatePluginInterfaces(self, self.id, cStringIO.StringIO())

    #   IAuthenticationPlugin interface support
    security.declarePrivate( 'authenticateCredentials' )
    def authenticateCredentials( self, credentials ):
        " "
        login = credentials.get('login').strip()
        password = credentials.get('password').strip()

        if None in (login, password):
            return None

        for domain in config.authentication_domains:
            if login.endswith(domain): break
        else:
            return None

        try:
            # Authenticate method should raise an error
            # if login fails, or some other error occurs
            authenticate(login, password)
            if not login in self._known_users:
                # Register username, so that enumerateUsers has
                # something to return, and we have something to
                # look up to see whether the plugin should give
                # a user roles.
                self._known_users = self._known_users + (login,)
                # Set email address in memberdata, because we can;
                # this would have to go if the user isn't authenticating
                # with an email address.
                #
                # OTOH, you see how you can get properties from another
                # system and set them locally.
                #self.portal_membership.getMemberById(memberid=login).setMemberProperties(
                #    {'email':login})
            return login, login
        except:
            return None

    #    IUserEnumerationPlugin interface support
    def enumerateUsers(self, id=None, login=None, exact_match=False,
        sort_by=None, max_results=None, **kw):
        ' '
        users = []
        for user in self._known_users:
            users.append({'id' : user,'login' : user,
                          'pluginid' : self.getId()})
        if id or login:
            if id:
                for user in users:
                    if user['id'] == id: return [user]
            if login:
                for user in users:
                    if user['login'] == login: return [user]
        return users

    #    IRolesPlugin interface support
    def getRolesForPrincipal(self, principal, request=None):

        """ Return a sequence of role names which the principal has.
        """
        user_id = principal.getId()
        if user_id in self._known_users:
            return config.authentication_roles
        else:
            return None
    
classImplements(EasyUserAuthentication, IAuthenticationPlugin,
                IUserEnumerationPlugin, IRolesPlugin)
InitializeClass(EasyUserAuthentication)
