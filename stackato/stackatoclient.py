# -*- coding: utf-8 -*-

from .restclient import RestClient
from .exceptions import cloud_error
from . import __version__


CLOUD_INFO_PATH     = '/info'
CLOUD_SERVICE_PATH  = '/info/services'
CLOUD_RUNTIME_PATH  = '/info/runtimes'
APPS_PATH           = '/apps'
RESOURCES_PATH      = '/resources'
SERVICES_PATH       = '/services'
USERS_PATH          = '/users'
USER_PATH           = '/users/%(email)s'
USER_TOKENS_PATH    = '/users/%(email)s/tokens'
GROUPS_PATH         = '/groups'
STACKATO_PATH       = '/stackato'


class StackatoClient(RestClient):
    @property
    def auth_token(self):
        return self.config.get('auth_token', None)

    @auth_token.setter
    def auth_token(self, token):
        if token:
            self.login_using_token(token)
            self._verify_cloud_info()
        else:
            del self.config['auth_token']

    @property
    def user(self):
        return self.config.get('user', None)

    @user.setter
    def user(self, email):
        if email:
            self.login(email)
            self._verify_cloud_info()
        else:
            del self.config['user']

    def request(self, method, path, **kwargs):
        headers = {
            'User-Agent': 'PyStackato/%s' % __version__,
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8'
        }

        rconf = dict()
        rconf.update(self.config)
        rconf.update(kwargs)

        if rconf.has_key('auth_token'):
            headers['AUTHORIZATION'] = rconf['auth_token']
        if rconf.has_key('service_token'):
            headers['X-VCAP-Service-Token'] = rconf['service_token']
        if rconf.has_key('proxy_user'):
            headers['PROXY-USER'] = rconf['proxy_user']
        if rconf.has_key('trace_key'):
            headers['X-VCAP-Trace'] = '22' if rconf['trace_key'] is True else rconf['trace_key']

        if kwargs.has_key('headers'):
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers

        return_response = True
        if kwargs.has_key('return_response'):
            return_response = kwargs['return_response']
        
        retval = super(StackatoClient, self).request(method, path, **kwargs)
        if return_response:
            cloud_error(retval)
        return retval

    def create_auth_token(self, email, password=None, **kwargs):
        if not password:
            self._require_login()
            self._require_admin()
        path = USER_TOKENS_PATH % {'email': email}
        kwargs['data'] = {'ssh_privkey': '1'}
        if password:
            kwargs['data']['password'] = password
        response = self.post(path, **kwargs)
        return response.json
    create_token = create_auth_token

    def login(self, email, password=None, **kwargs):
        data = self.create_auth_token(email, password, **kwargs)
        self.config['auth_token'] = data.get('token', None)
        self.config['user'] = email
        self.config['sshkey'] = data.get('sshkey', None)
        self.config['cloud_info_verified'] = False
        return self

    def login_using_token(self, token):
        self.config['auth_token'] = token
        del self.config['user']
        del self.config['sshkey']
        self.config['cloud_info_verified'] = False
        return self

    def is_logged_in(self):
        return self.config.get('auth_token', None) is not None

    def _require_login(self):
        if not self.is_logged_in():
            raise Exception()

    def proxy_as(self, email):
        if email:
            self.config['proxy_user'] = email
        else:
            del self.config['proxy_user']
        del self.config['cloud_info_verified']
        return self

    def is_proxying_user(self):
        return self.config.get('proxy_user', None) is not None

    def cloud_info(self, **kwargs):
        response = self.get(CLOUD_INFO_PATH, **kwargs)
        data = response.json
        if data:
            self.config['user'] = data.get('user', None)
            self.config['groups'] = data.get('groups', None)
            self.config['is_admin'] = data.get('admin', False)
        self.config['cloud_info_verified'] = True
        return data
    
    def _verify_cloud_info(self, **kwargs):
        if not self.config.get('cloud_info_verified', False):
            self.cloud_info(**kwargs)

    def is_admin(self):
        self._verify_cloud_info()
        return self.config.get('is_admin', False)

    def _require_admin(self):
        if not self.is_admin():
            raise Exception()

    def cloud_runtime_info(self, **kwargs):
        response = self.get(CLOUD_RUNTIME_PATH, **kwargs)
        return response.json

    def cloud_service_info(self, **kwargs):
        self._require_login()
        response = self.get(CLOUD_SERVICE_PATH, **kwargs)
        return response.json

    def list_users(self, **kwargs):
        self._require_login()
        self._require_admin()
        response = self.get(USERS_PATH, **kwargs)
        return response.json

    def user_info(self, email=None, **kwargs):
        self._require_login()
        if email is None:
            email = self.config['user']
        path = USER_PATH % {'email':email}
        response = self.get(path, **kwargs)
        return response.json

    def create_user(self, email, password, **kwargs):
        data = {'email': email, 'password': password}
        kwargs['data'] = data
        response = self.post(USERS_PATH, **kwargs)
        return response.json

    def update_user(self, email, password, **kwargs):
        self._require_login()
        if email != self.config['user']:
            self._require_admin()
        user_info = self.user_info(email)
        user_info['password'] = password
        path = USER_PATH % {'email':email}
        response = self.put(path, user_info, **kwargs)
        return response.json

    def delete_user(self, email, **kwargs):
        self._require_login()
        self._require_admin()
        if email == self.config['user']:
            raise Exception()
        path = USER_PATH % {'email':email}
        response = self.delete(path, **kwargs)
        return response.json
