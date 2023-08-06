#!/usr/bin/env python

# Copyright (c) 2011-2012 Ben Croston
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from json import loads, dumps
import traceback
import sys
from webob import Request, Response, exc

class AuthRPCApp(object):
    """
    Serve the given object via json-rpc (http://json-rpc.org/)
    """

    def __init__(self, obj, auth=None):
        """
        obj  - a class containing functions available using jsonrpc
        auth - an authentication function (optional)
        """
        self.obj = obj
        self.auth = auth

    def __call__(self, environ, start_response):
        req = Request(environ)
        try:
            resp = self._process(req)
        except exc.HTTPException as e:
            resp = e
        return resp(environ, start_response)

    def _process(self, req):
        """
        Process the JSONRPC request.
        req - a webob Request object
        """
        if not req.method == 'POST':
            raise exc.HTTPMethodNotAllowed("Only POST allowed")

        try:
             json = loads(req.body.decode())
        except ValueError as e:
            raise exc.HTTPBadRequest('Bad JSON: %s' % e)

        if isinstance(json, list):
            # batch request
            try:
                username = json[0]
                password = json[1]
                cmds = json[2:]
            except IndexError:
                raise exc.HTTPBadRequest('JSON body missing parameters')
            self._check_auth(username, password, req.user_agent)
            result = []
            for c in cmds:
                if 'method' in c and 'params' in c and 'id' in c:
                    self._process_single(c['method'], c['params'], c['id'])
                else:
                    raise exc.HTTPBadRequest('JSON body missing parameter')
                result.append(self._process_single(c['method'], c['params'], c['id']))
        else:
            # single request
            try:
                username = json['username'] if 'username' in json else None
                password = json['password'] if 'password' in json else None
                id = json['id']
                method = json['method']
                params = json['params']
            except KeyError as e:
                raise exc.HTTPBadRequest("JSON body missing parameter: %s" % e)
            self._check_auth(username, password, req.user_agent, id)

            if method == '__getfile__':
                try:
                    with open(params[0],'rb') as f:
                        body = f.read()
                except IOError:
                    raise exc.HTTPNotFound('File not found: %s'%params[0])
                return Response(content_type='application/octet-stream',
                                body=body)

            result = self._process_single(method, params, id)

        return Response(content_type='application/json',
                        body=dumps(result).encode())

    def _check_auth(self, username, password, user_agent, id=None):
        if self.auth is None:
            return
        try:
            auth_result = self.auth(username, password, user_agent)
        except:
            text = traceback.format_exc()
            exc_value = sys.exc_info()[1]
            error_value = dict(
                name='JSONRPCError',
                code=100,
                message=str(exc_value),
                error=text)
            return Response(
                status=500,
                content_type='application/json',
                body=dumps(dict(result=None,
                                error=error_value,
                                id=id)))
        if not auth_result:
            raise exc.HTTPUnauthorized()

    def _process_single(self, method, params, id):
        retval = {}
        retval['id'] = id
        retval['result'] = None
        retval['error'] = None

        if params is None:
            params = []

        obj = self.obj
        if isinstance(self.obj, tuple) or isinstance(self.obj, list):
            for x in self.obj:
                if method.startswith('%s.'%x.__class__.__name__):
                   obj = x
                   method = method.replace('%s.'%obj.__class__.__name__,'',1)
                   break
        elif method.startswith('%s.'%self.obj.__class__.__name__):
            method = method.replace('%s.'%self.obj.__class__.__name__,'',1)
        if method.startswith('_') and method != '__getfile__':
            retval['error'] = 'Bad method name %s: must not start with _' % method
            return retval
        try:
            method = getattr(obj, method)
        except AttributeError as e:
            raise exc.HTTPBadRequest(str(e))

        try:
            if isinstance(params, list):
                retval['result'] = method(*params)
            else:
                retval['result'] = method(**params)
        except:
            text = traceback.format_exc()
            exc_value = sys.exc_info()[1]
            error_value = dict(
                name='JSONRPCError',
                code=100,
                message=str(exc_value),
                error=text)
            retval['result'] = None
            retval['error'] = error_value

        return retval

