# coding: utf-8
from functools import wraps
from werkzeug.contrib.securecookie import SecureCookie
from werkzeug.urls import url_quote
from werkzeug.utils import cached_property, redirect
from werkzeug.wrappers import BaseRequest, Response
from openid.consumer.consumer import Consumer, DiscoveryFailure, SUCCESS
from openid.extensions.ax import FetchRequest, FetchResponse, AttrInfo
from openid.store.memstore import MemoryStore
import re


SESSION_KEY = 'authgoogle'
SECRET_KEY = 'secret'

STORE = MemoryStore()

GOOGLE = u'https://www.google.com/accounts/o8/id'

AX_EMAIL = 'http://axschema.org/contact/email'


DEFAULT_ALLOW = [
    re.compile(r'@gmail\.com$'),
]


RE_TYPE = type(re.compile(r'regular expression'))


class Error(StandardError):
    pass


class Request(BaseRequest):

    @cached_property
    def session(self):
        return SecureCookie.load_cookie(self, SESSION_KEY, SECRET_KEY)

    def save_session(self, response):
        self.session.save_cookie(response, SESSION_KEY)


class AuthGoogleMiddleware(object):

    def __init__(self, app, allow=None):
        self.app = app
        self.allow = allow or DEFAULT_ALLOW

    def __call__(self, environ, start_response):
        request = Request(environ, start_response)
        email = request.session.get('email', [None])[0]

        if email and self.check_auth(email):
            response = self.app
        elif email:
            del request.session['email']
            response = self.unauthorized('Reload page to retry authorization.')
        else:
            try:
                response = self.openid(request)
            except (Error, DiscoveryFailure), e:
                response = self.unauthorized(e)

        environ['AUTHGOOGLE_ACCOUNT'] = email

        request.save_session(response)
        return response(environ, self.start_response_wrapper(start_response, email))

    def start_response_wrapper(self, start_response, email):
        @wraps(start_response)
        def wrapper(status, headers, exc_info=None):
            if email:
                headers.append(('X-Google-Account', email))
            return start_response(status, headers, exc_info)
        return wrapper

    def check_auth(self, email):
        for cond in self.allow:
            if isinstance(cond, basestring) and email == cond:
                return True
            elif isinstance(cond, RE_TYPE) and cond.match(email):
                return True
        return False

    def unauthorized(self, message='401 Unathorized'):
        return Response(message, 401, mimetype='text/plain')

    def openid(self, request):
        consumer = Consumer(request.session, STORE)

        if 'openid.next' in request.args:
            oidresp = consumer.complete(request.values, request.url)
            if oidresp.status != SUCCESS:
                raise Error(oidresp.status)
            axresp = FetchResponse.fromSuccessResponse(oidresp)
            request.session['email'] = axresp.get(AX_EMAIL)
            response = redirect(request.args['openid.next'])

        else:
            oidreq = consumer.begin(GOOGLE)
            axreq = FetchRequest()
            axreq.add(AttrInfo(AX_EMAIL, required=True))
            oidreq.addExtension(axreq)
            response = redirect(oidreq.redirectURL(request.host_url,
                request.base_url + '?openid.next=' + url_quote(request.url)))

        return response
