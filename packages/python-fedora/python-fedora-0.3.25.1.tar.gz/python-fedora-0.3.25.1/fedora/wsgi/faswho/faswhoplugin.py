# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2011  Red Hat, Inc.
# This file is part of python-fedora
#
# python-fedora is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# python-fedora is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with python-fedora; if not, see <http://www.gnu.org/licenses/>
#
'''
repoze.who plugin to authenticate against hte Fedora Account System

.. moduleauthor:: John (J5) Palmieri <johnp@redhat.com>
.. moduleauthor:: Luke Macken <lmacken@redhat.com>
.. moduleauthor:: Toshio Kuratomi <toshio@fedoraproject.org>

.. versionadded:: 0.3.17
'''
import os
import sys
from urllib import quote_plus
import logging

import pkg_resources

from beaker.cache import Cache
from bunch import Bunch
from kitchen.text.converters import to_bytes
from paste.httpexceptions import HTTPFound
from repoze.who.middleware import PluggableAuthenticationMiddleware
from repoze.who.classifiers import default_request_classifier
from repoze.who.classifiers import default_challenge_decider
from repoze.who.interfaces import IChallenger, IIdentifier
from repoze.who.plugins.basicauth import BasicAuthPlugin
from repoze.who.plugins.friendlyform import FriendlyFormPlugin
from paste.request import parse_dict_querystring, parse_formvars
import webob

from fedora import _, b_
from fedora.client import AuthError
from fedora.client.fasproxy import FasProxyClient
from fedora.wsgi.csrf import CSRFMetadataProvider, CSRFProtectionMiddleware

log = logging.getLogger(__name__)

FAS_URL = 'https://admin.fedoraproject.org/accounts/'
FAS_CACHE_TIMEOUT = 900 # 15 minutes (FAS visits timeout after 20)

fas_cache = Cache('fas_repozewho_cache', type='memory')

def fas_request_classifier(environ): 
    classifier = default_request_classifier(environ) 
    if classifier == 'browser': 
        request = webob.Request(environ) 
        if not request.accept.best_match(['application/xhtml+xml','text/html']): 
            classifier = 'app' 
    return classifier 

def make_faswho_middleware(app, log_stream=None, login_handler='/login_handler',
        login_form_url='/login', logout_handler='/logout_handler',
        post_login_url='/post_login', post_logout_url=None, fas_url=FAS_URL,
        insecure=False):
    '''
    :app: WSGI app that is being wrapped
    :log_stream: :class:`logging.Logger` to log auth messages
    :login_handler: URL where the login form is submitted
    :login_form_url: URL where the login form is displayed
    :logout_handler: URL where the logout form is submitted
    :post_login_url: URL to redirect the user to after login
    :post_logout_url: URL to redirect the user to after logout
    :fas_url: Base URL to the FAS server
    :insecure: Allow connecting to a fas server without checking the server's
        SSL certificate.  Opens you up to MITM attacks but can be useful
        when testing.  *Do not enable this in production*
    '''

    # Because of the way we override values (via a dict in AppConfig), we
    # need to make this a keyword arg and then check it here to make it act
    # like a positional arg.
    if not log_stream:
        raise TypeError('log_stream must be set when calling make_fasauth_middleware()')

    faswho = FASWhoPlugin(fas_url, insecure)
    csrf_mdprovider = CSRFMetadataProvider()

    form = FriendlyFormPlugin(login_form_url,
                              login_handler,
                              post_login_url,
                              logout_handler,
                              post_logout_url,
                              rememberer_name='fasident')

    form.classifications = { IIdentifier: ['browser'],
                             IChallenger: ['browser'] } # only for browser

    basicauth = BasicAuthPlugin('repoze.who')

    identifiers = [('form', form), ('fasident', faswho), ('basicauth', basicauth)]
    authenticators = [('fasauth', faswho)]
    challengers = [('form', form), ('basicauth', basicauth)]
    mdproviders = [('fasmd', faswho), ('csrfmd', csrf_mdprovider)]

    if os.environ.get('FAS_WHO_LOG'):
        log_stream = sys.stdout

    app = CSRFProtectionMiddleware(app)
    app = PluggableAuthenticationMiddleware(
            app,
            identifiers,
            authenticators,
            challengers,
            mdproviders,
            fas_request_classifier,
            default_challenge_decider,
            log_stream = log_stream,
            )

    return app

class FASWhoPlugin(object):

    def __init__(self, url, insecure=False, session_cookie='tg-visit'):
        self.url = url
        self.insecure = insecure
        self.fas = FasProxyClient(url, insecure=insecure)
        self.session_cookie = session_cookie
        self._session_cache = {}
        self._metadata_plugins = []

        for entry in pkg_resources.iter_entry_points(
                'fas.repoze.who.metadata_plugins'):
            self._metadata_plugins.append(entry.load())

    def keep_alive(self, session_id):
        log.info(b_('Keep alive cache miss'))
        try:
            linfo = self.fas.get_user_info({'session_id': session_id})
        except AuthError, e:
            log.warning(e)
            return None
        try:
            del linfo[1]['password']
        except KeyError:
            # Just make sure the password isn't in the info we return
            pass
        return linfo

    def identify(self, environ):
        log.info(b_('in identify()'))
        req = webob.Request(environ)
        cookie = req.cookies.get(self.session_cookie)

        if cookie is None:
            return None

        log.info(b_('Request identify for cookie %(cookie)s') %
                {'cookie': to_bytes(cookie)})
        linfo = fas_cache.get_value(key=cookie + '_identity',
                                    createfunc=lambda: self.keep_alive(cookie),
                                    expiretime=FAS_CACHE_TIMEOUT)

        if not linfo:
            self.forget(environ, None)
            return None

        if not isinstance(linfo, tuple):
            return None

        try:
            me = linfo[1]
            me.update({'repoze.who.userid': me['username']})
            environ['FAS_LOGIN_INFO'] = linfo
            return me
        except Exception, e: # pylint:disable-msg=W0703
            # For any exceptions, returning None means we failed to identify
            log.warning(e)
            return None

    def remember(self, environ, identity):
        log.info(b_('In remember()'))
        req = webob.Request(environ)
        result = []

        linfo = environ.get('FAS_LOGIN_INFO')
        if isinstance(linfo, tuple):
            session_id = linfo[0]
            set_cookie = '%s=%s; Path=/;' % (self.session_cookie, session_id)
            result.append(('Set-Cookie', set_cookie))
            return result
        return None

    def forget(self, environ, identity):
        log.info(b_('In forget()'))
        # return a expires Set-Cookie header
        req = webob.Request(environ)

        linfo = environ.get('FAS_LOGIN_INFO')
        if isinstance(linfo, tuple):
            session_id = linfo[0]
            log.info(b_('Forgetting login data for cookie %(s_id)s') %
                    {'s_id': to_bytes(session_id)})

            self.fas.logout(session_id)

            result = []
            fas_cache.remove_value(key=session_id + '_identity')
            expired = '%s=\'\'; Path=/; Expires=Sun, 10-May-1971 11:59:00 GMT'\
                    % self.session_cookie
            result.append(('Set-Cookie', expired))
            environ['FAS_LOGIN_INFO'] = None
            return result

        return None

    # IAuthenticatorPlugin
    def authenticate(self, environ, identity):
        log.info(b_('In authenticate()'))
        try:
            login = identity['login']
            password = identity['password']
        except KeyError:
            return None

        err_goto = '/login'
        default_came_from = '/'
        if 'SCRIPT_NAME' in environ:
            sn = environ['SCRIPT_NAME']
            err_goto = sn + err_goto
            default_came_from = sn + default_came_from

        query = parse_dict_querystring(environ)
        form = parse_formvars(environ)
        form.update(query)
        came_from = form.get('came_from', default_came_from)

        user_data = ''
        try:
            user_data = self.fas.get_user_info({'username': login,
                'password': password})
        except AuthError, e:
            log.info(b_('Authentication failed, setting error'))
            log.warning(e)
            err = 1
            environ['FAS_AUTH_ERROR'] = err

            err_app = HTTPFound(err_goto + '?' +
                                'came_from=' + quote_plus(came_from))

            environ['repoze.who.application'] = err_app

            return None

        if user_data:
            if isinstance(user_data, tuple):
                del user_data[1]['password']
                environ['FAS_LOGIN_INFO'] = user_data
                # let the csrf plugin know we just authenticated and it needs
                # to rewrite the redirection app
                environ['CSRF_AUTH_SESSION_ID'] = environ['FAS_LOGIN_INFO'][0]
                return login

        err = _(u'An unknown error happened when trying to log you in.'
                ' Please try again.')
        environ['FAS_AUTH_ERROR'] = err
        err_app = HTTPFound(err_goto + '?' + 'came_from=' + came_from)
                            #'&ec=login_err.UNKNOWN_AUTH_ERROR')

        environ['repoze.who.application'] = err_app

        return None

    def get_metadata(self, environ):
        log.info(b_('Metadata cache miss - refreshing metadata'))
        info = environ.get('FAS_LOGIN_INFO')
        identity = {}

        if info is not None:
            identity.update(info[1])
            identity['session_id'] = info[0]

        for plugin in self._metadata_plugins:
            plugin(identity)

        # we don't define permissions since we don't
        # have any peruser data though other services
        # may wish to add another metadata plugin to do so

        if not identity.has_key('permissions'):
            identity['permissions'] = set()

        # we keep the approved_memberships list because there is also an
        # unapproved_membership field.  The groups field is for repoze.who
        # group checking and may include other types of groups besides
        # memberships in the future (such as special fedora community groups)

        groups = set()
        for g in identity['approved_memberships']:
            groups.add(g['name'])

        identity['groups'] = groups
        return identity

    def add_metadata(self, environ, identity):
        log.info(b_('In add_metadata'))
        req = webob.Request(environ)

        if identity.get('error'):
            log.info(b_('Error exists in session, no need to set metadata'))
            return 'error'

        cookie = req.cookies.get(self.session_cookie)

        if cookie is None:
            cookie = environ.get('CSRF_AUTH_SESSION_ID')
            if cookie is None:
                return None

        log.info(b_('Request metadata for cookie %(cookie)s') %
                {'cookie': to_bytes(cookie)})
        info = fas_cache.get_value(key=cookie + '_metadata',
                createfunc=lambda: self.get_metadata(environ),
                expiretime=FAS_CACHE_TIMEOUT)

        #### FIXME: Deprecate this!!!
        # If we make a new version of fas.who middleware, get rid of saving
        # user information directly into identity.  Instead, save it into
        # user, as is done below
        identity.update(info)

        identity['userdata'] = info
        identity['user'] = Bunch()
        identity['user'].created = info['creation']
        identity['user'].display_name = info['human_name']
        identity['user'].email_address = info['email']
        identity['user'].groups = info['groups']
        identity['user'].password = None
        identity['user'].permissions = info['permissions']
        identity['user'].user_id = info['id']
        identity['user'].user_name = info['username']
        identity['groups'] = info['groups']
        identity['permissions'] = info['permissions']

        if 'repoze.what.credentials' not in environ:
            environ['repoze.what.credentials'] = {}

        environ['repoze.what.credentials']['groups'] = info['groups']
        environ['repoze.what.credentials']['permissions'] = info['permissions']

        # Adding the userid:
        userid = identity['repoze.who.userid']
        environ['repoze.what.credentials']['repoze.what.userid'] = userid

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, id(self))
