# coding: utf-8
from functools import wraps
from werkzeug.contrib.securecookie import SecureCookie
from werkzeug.exceptions import Forbidden, Unauthorized, InternalServerError
from werkzeug.urls import url_quote, url_encode
from werkzeug.utils import cached_property, redirect
from werkzeug.wrappers import BaseRequest
from openid.consumer.consumer import Consumer, SUCCESS
from openid.extensions.ax import FetchRequest, FetchResponse, AttrInfo
from openid.store.memstore import MemoryStore
import re
import uuid


GOOGLE = u'https://www.google.com/accounts/o8/id'

AX_EMAIL = 'http://axschema.org/contact/email'

DEFAULT_ALLOW = [
    re.compile(r'@gmail\.com$'),
]


class Request(BaseRequest):

    @cached_property
    def session_secret(self):
        return self.environ.get('SESSION_SECRET')

    @cached_property
    def session(self):
        return SecureCookie.load_cookie(self, secret_key=self.session_secret)

    def save_session(self, response):
        if hasattr(response, 'set_cookie'):
            self.session.save_cookie(response)


class AuthGoogleMiddleware(object):

    def __init__(self, app, allow=None, secret=None):
        self.app = app
        self.allow = allow or DEFAULT_ALLOW
        self.secret = secret or str(uuid.uuid4())
        self.openid_store = MemoryStore()

    def __call__(self, environ, start_response):
        environ['SESSION_SECRET'] = self.secret

        request = Request(environ, start_response)
        email = self.get_email(request)

        if email and 'logout' in request.args:
            response = self.logout(request)
        elif email and self.check_auth(request):
            response = self.app
        elif email:
            args = request.args.copy()
            args.update({'logout': ''})
            response = Forbidden('''
                    <p><strong>%s</strong></p>
                    <p>You are not authorized to access this place. <a href="%s?%s">Retry?</a></p>
            ''' % (email, request.path, url_encode(args)))
        else:
            try:
                response = self.openid(request)
            except Exception, e:
                response = InternalServerError(e)

        environ['AUTHGOOGLE_ACCOUNT'] = email

        request.save_session(response)
        return response(environ, self.start_response_wrapper(start_response, email))

    def start_response_wrapper(self, start_response, email):
        @wraps(start_response)
        def wrapper(status, headers, exc_info=None):
            if email:
                headers.append(('X-Google-Account', email.encode('ascii')))
            return start_response(status, headers, exc_info)
        return wrapper

    def get_email(self, request):
        return request.session.get('email', [None])[0]

    def get_allowed(self, request):
        """ May be overriden in subclass to implement tricky permissions model """
        return self.allow

    def check_auth(self, request):
        email = self.get_email(request)
        for cond in self.get_allowed(request):
            if hasattr(cond, 'match'):
                if cond.match(email):
                    return True
            elif email == cond:
                return True
        return False

    def openid(self, request):
        consumer = Consumer(request.session, self.openid_store)

        if 'openid.next' in request.args:
            oidresp = consumer.complete(request.values, request.url)
            if oidresp.status == SUCCESS:
                axresp = FetchResponse.fromSuccessResponse(oidresp)
                request.session['email'] = axresp.get(AX_EMAIL)
                response = redirect(request.args['openid.next'])
            else:
                response = Unauthorized(oidresp.status)
        else:
            oidreq = consumer.begin(GOOGLE)
            axreq = FetchRequest()
            axreq.add(AttrInfo(AX_EMAIL, required=True))
            oidreq.addExtension(axreq)
            response = redirect(oidreq.redirectURL(request.host_url,
                request.base_url + '?openid.next=' + url_quote(request.url)))

        return response

    def logout(self, request):
        del request.session['email']
        args = request.args.copy()
        args.pop('logout')
        if args:
            return redirect('%s?%s' % (request.path, url_encode(args)))
        return redirect(request.path)
