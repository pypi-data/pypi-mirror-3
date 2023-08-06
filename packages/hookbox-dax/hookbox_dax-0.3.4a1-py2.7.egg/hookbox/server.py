import collections
import errno
import logging
import os
import socket
import sys
import urllib
import urlparse
import eventlet
from paste import urlmap, urlparser

eventlet.monkey_patch(all=False, socket=True, select=True)

from restkit import Resource

import eventlet.wsgi
import eventlet.websocket

from csp_eventlet import Listener
import rtjp_eventlet

from errors import ExpectedException
import channel
import protocol
from user import User
from admin.admin import HookboxAdminApp

from api.internal import HookboxAPI
from api.web import HookboxWebAPI
try:
    import json
except:
    import simplejson as json

from __init__ import __version__

class EmptyLogShim(object):
    def write(self, *args, **kwargs):
        return

logger = logging.getLogger('hookbox')

access_logger = logging.getLogger('access')


class HookboxServer(object):

    def __init__(self, bound_socket, bound_api_socket, config, outputter):
        self.config = config
        self._bound_socket = bound_socket
        self._bound_api_socket = bound_api_socket
        self._rtjp_server = rtjp_eventlet.RTJPServer()
#        self.identifer_key = 'abc';
        self.base_host = config['cbhost']
        self.base_port = config['cbport']
        self.base_path = config['cbpath']

        self._root_wsgi_app = urlmap.URLMap()
        self.csp = Listener()
        self._root_wsgi_app['/csp'] = self.csp
        self._root_wsgi_app['/ws'] = self._ws_wrapper
        self._ws_wsgi_app = eventlet.websocket.WebSocketWSGI(self._ws_wsgi_app)

        static_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'static')
        self._root_wsgi_app['/static'] = urlparser.StaticURLParser(static_path)

        self.api = HookboxAPI(self, config)
        self._web_api_app = HookboxWebAPI(self.api)


        self.admin = HookboxAdminApp(self, config, outputter)
        self._root_wsgi_app['/admin'] = self.admin
        self.channels = {}
        self.conns_by_cookie = {}
        self.conns = {}
        self.users = {}

        self.user_channel_presence = {}
        self._http = None
        self._url = None
        #connection hack to increase connection limit, linux only for now
        try:
            import resource
            #get soft limit of max number of open files
            self.max_conn = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
        except ImportError:
            self.max_conn = 1024


    def _ws_wrapper(self, environ, start_response):
        environ['PATH_INFO'] = environ['SCRIPT_NAME'] + environ['PATH_INFO']
        environ['SCRIPT_NAME'] = ''
        return self._ws_wsgi_app(environ, start_response)

    def _ws_wsgi_app(self, ws):
        access_logger.info("Incoming WebSocket connection\t%s\t%s",
            ws.environ.get('REMOTE_ADDR', ''), ws.environ.get('HTTP_HOST'))
        sock = SockWebSocketWrapper(ws)
        rtjp_conn = rtjp_eventlet.RTJPConnection(sock=sock)
        self._accept(rtjp_conn)

    def run(self):
        # dlg -- debugging backdoor hack
        try:
            import eventlet.backdoor
            eventlet.spawn(eventlet.backdoor.backdoor_server, eventlet.listen(('localhost', 3000)), locals={'server':self})
        except Exception:
            logger.exception("Problem spawning debug backdoor")
        # end debugging

        if not self._bound_socket:
            self._bound_socket = eventlet.listen((self.config.interface, self.config.port))
        eventlet.spawn(eventlet.wsgi.server, self._bound_socket, self._root_wsgi_app, log=EmptyLogShim(), max_size=self.max_conn)
        
        # We can't get the main interface host, port from config, in case it
        # was passed in directly to the constructor as a bound sock.
        main_host, main_port = self._bound_socket.getsockname()
        logger.info("Listening to hookbox on http://%s:%s", main_host, main_port)

        # Possibly create bound_api_socket
        if not self._bound_api_socket:
            api_host, api_port = self.config.web_api_interface, self.config.web_api_port
            if api_host is None: api_host = main_host
            if api_port is None: api_port = main_port
            if (main_host, main_port) != (api_host,  api_port):
                self._bound_api_socket = eventlet.listen((api_host, api_port))

        # If we have a _bound_api_socket at this point, (either from constructor,
        # or previous block) we should turn it into a wsgi server.
        if self._bound_api_socket:
              logger.info("Listening to hookbox/webapi on http://%s:%s", *self._bound_api_socket.getsockname())
              api_url_map = urlmap.URLMap()
              # Maintain /web path
              api_url_map['/web'] = self._web_api_app
              # Might as well expose it over / as well
              api_url_map['/'] = self._web_api_app
              eventlet.spawn(eventlet.wsgi.server, self._bound_api_socket, api_url_map, log=EmptyLogShim())

        # otherwise, expose the web api over the main interface/wsgi app
        else:
            self._root_wsgi_app['/web'] = self._web_api_app

        ev = eventlet.event.Event()
        self._rtjp_server.listen(sock=self.csp)
        eventlet.spawn(self._run, ev)
        return ev

    def __call__(self, environ, start_response):
        return self._root_wsgi_app(environ, start_response)

    def _accept(self, rtjp_conn):
        conn = protocol.HookboxConn(self, rtjp_conn, self.config, rtjp_conn._sock.environ.get('HTTP_X_FORWARDED_FOR', ''))
        conn.run()

    def _run(self, ev):
        # NOTE: You probably want to call this method directly if you're trying
        #       To use some other wsgi server than eventlet.wsgi
        while True:
            try:
                rtjp_conn = self._rtjp_server.accept().wait()
                if not rtjp_conn:
                    continue
                access_logger.info("Incoming CSP connection\t%s\t%s",
                    rtjp_conn._sock.environ.get('HTTP_X_FORWARDED_FOR', rtjp_conn._sock.environ.get('REMOTE_ADDR', '')),
                    rtjp_conn._sock.environ.get('HTTP_HOST'))
                eventlet.spawn(self._accept, rtjp_conn)
#                conn = protocol.HookboxConn(self, rtjp_conn, self.config)
            except:
                logger.exception("Unknown Exception occurred at top level")
#                ev.send_exception(*sys.exc_info())
#                break
        logger.info("Hookbox Daemon Stopped")

    def http_request(self, path_name=None, cookie_string=None, form={}, full_path=None, conn=None):
        if not full_path and self.config['cb_single_url']:
            full_path = self.config['cb_single_url']
        if full_path:
            u = urlparse.urlparse(full_path)
            scheme, host, port, path = u.scheme, u.hostname, u.port or 80, u.path
            if self.config['cbtrailingslash'] and not path.endswith('/'):
                path += '/'
            if u.query:
                path += '?' + u.query
        else:
#            if self.config.get('cb_single_url'):
#                path = self.config["cbpath"]
#                host = self.base_host
#            else:
            path = self.base_path + '/' + self.config.get('cb_' + path_name)
            if self.config['cbtrailingslash'] and not path.endswith('/'):
                path += '/'
            scheme = self.config["cbhttps"] and "https" or "http"
            host = self.config["cbhost"]
            port = self.config["cbport"]

        if path_name:
            form['action'] = path_name
        if self.config['webhook_secret']:
            form['secret'] = self.config['webhook_secret']
        # TODO: The following code creates a hideously bloated form_body. I'm
        #       not sure we actually have to use urlencode for this.
        for key, val in form.items():
            new_key = key
            if isinstance(key, unicode):
                del form[key]
                new_key = key.encode('utf-8')
            new_val = val
            if isinstance(val, unicode):
                new_val = val.encode('utf-8')
            form[new_key] = new_val

        form_body = urllib.urlencode(form)

        # for logging
        if port != 80:
            host = "%s:%s" % (host, port)
        url = urlparse.urlunparse((scheme, host, '', '', '', ''))

        headers = {'content-type': 'application/x-www-form-urlencoded'}
        if cookie_string:
            headers['Cookie'] = cookie_string
        if conn:
            headers['X-Real-IP'] = conn.get_remote_addr()
        if self.config["cbsendhookboxversion"]:
            headers['X-Hookbox-Version'] = __version__
        body = None
        try:
            try:
                #check and change url if necessary
                if self._url is None or self._url != url:
                    self._http = Resource(url)
                    self._url = url
                http = self._http

                response = http.request(method='POST', path=path, payload=form_body, headers=headers)
                body = response.body_string()
            except socket.error, e:
                if e.errno == errno.ECONNREFUSED:
                    raise Exception("Connection refused for HTTP request to %s" % (url))
                raise e
        except Exception, e:
            logger.warn('Caught error in http request %s' % repr(e))
            self.admin.webhook_event(path_name, url, 0, False, body, form_body, cookie_string, e)
            logger.warn('Exception with webhook %s%s' % (url, path), exc_info=True)
            return False, { 'error': 'failure: %s' % (e,) }

        logger.info("%s%s/%s ==> %s %s"%(url, path,form_body, response.status, body))

        if response.status_int != 200:
            self.admin.webhook_event(path_name, url, response.status_int, False, body, form_body, cookie_string, "Invalid status")
            raise ExpectedException("Invalid callback response, status=%s (%s), body: %s" % (response.status_int, path, body))

        try:
           output = json.loads(body)
        except:
            self.admin.webhook_event(path_name, url, response.status_int, False, body, form_body, cookie_string, "Invalid json response")
            raise ExpectedException("Invalid json: " + body)
        #print 'response to', path, 'is:', output
        if not isinstance(output, list) or len(output) != 2:
            self.admin.webhook_event(path_name, url, response.status_int, False, body, form_body, cookie_string, "len(response) != 2 (list)")
            raise ExpectedException("Invalid response (expected json list of length 2)")
        if not isinstance(output[1], dict):
            self.admin.webhook_event(path_name, url, response.status_int, False, body, form_body, cookie_string, "response[1] != json object")
            raise ExpectedException("Invalid response (expected json object in response index 1)")
        output[1] = dict([(str(k), v) for (k,v) in output[1].items()])
        err = ""
        if not output[0]:
            err = output[1].get('msg', "(No reason given)")
        self.admin.webhook_event(path_name, url, response.status_int, output[0], body, form_body, cookie_string, err)

        if conn:
            set_cookie = dict(response.headerslist).get('Set-Cookie', '')
            if set_cookie:
                conn.send_frame('SET_COOKIE', {'cookie': set_cookie})

        return output

        # type, url, response status, success/failture, raw_output

#    def _webhook_error

    def connect(self, conn, payload):
        try:
            decoded_payload = json.loads(payload)
        except:
            raise ExpectedException("Invalid json for payload")
        form = { 'conn_id': conn.id, 'payload': json.dumps(decoded_payload) }
        success, options = self.http_request('connect', conn.get_cookie(), form, conn=conn)
        if not success:
            raise ExpectedException(options.get('error', 'Unauthorized'))
        user_name = options.pop('name', None)
        if not user_name:
            raise ExpectedException('Unauthorized (missing name parameter in server response)')
        payload = options.pop('override_payload', payload)
        self.conns[conn.id] = conn
        user = self.get_user(user_name)
        user.update_options(**user.extract_valid_options(options))
        user.add_connection(conn)
        self.admin.user_event('connect', user.get_name(), conn.serialize())
        self.admin.connection_event('connect', conn.id, conn.serialize())
        conn.send_frame('CONNECTED', { 'name': user.get_name(), 'payload': payload })
        eventlet.spawn(self.maybe_auto_subscribe, user, options, conn=conn)

    def disconnect(self, conn):
        self.admin.user_event('disconnect', conn.user.get_name(), { "id": conn.id})
        self.admin.connection_event('disconnect', conn.id, conn.serialize())
        del self.conns[conn.id]

    def get_connection(self, id):
        return self.conns.get(id, None)

    def serialize(self):
        return {
            'channels': self.channels.keys(),
            'connections': self.conns.keys(),
        }

    def exists_user(self, name):
        return name in self.users

    def get_user(self, name):
        if name not in self.users:
            self.users[name] = User(self, name)
            self.admin.user_event('create', name, self.users[name].serialize())
            if name in self.user_channel_presence:
                for channel in self.user_channel_presence[name]:
                    channel.state_set(name, True)
        return self.users[name]

    def remove_user(self, name):
        if name in self.users:
            self.admin.user_event('destroy', name, {})
            user = self.users[name]
            del self.users[name]
            form = { 'name': name }
            try:
                self.http_request('disconnect', user.get_cookie(), form)
            except ExpectedException, e:
                pass
            except Exception, e:
                self.logger.warn("Unexpected error when removing user: %s", e, exc_info=True)

            if name in self.user_channel_presence:
                for channel in self.user_channel_presence[name]:
                    channel.state_set(name, False)
        
    def create_channel(self, conn, channel_name, options={}, needs_auth=True):
        local_options = options.copy()
        if channel_name in self.channels:
            raise ExpectedException("Channel already exists")
        if needs_auth:
            cookie_string = conn and conn.get_cookie() or None
            form = {
                'channel_name': channel_name,
            }
            success, callback_options = self.http_request('create_channel', cookie_string, form)
            if success:
                local_options.update(callback_options)
            else:
                raise ExpectedException(callback_options.get('error', 'Unauthorized'))

        chan = self.channels[channel_name] = channel.Channel(self, channel_name, **local_options)

        #If channel needs to know about server presence, register channel with users
        if chan.server_presenceful:
            user_state = {}
            for user in chan.server_user_presence:
                user_state[user] = user in self.users
                if user not in self.user_channel_presence:
                    self.user_channel_presence[user] = [chan]
                else:
                    self.user_channel_presence[user].append(chan)
            chan.state_multi_set(user_state)

        self.admin.channel_event('create_channel', channel_name, chan.serialize())

    def destroy_channel(self, channel_name, needs_auth=True):
        if channel_name not in self.channels:
            return None
        channel = self.channels[channel_name]
        if channel.destroy(needs_auth):
            if channel.server_presenceful:
                for user in channel.server_user_presence:
                    self.user_channel_presence[user].remove(channel)
                
            del self.channels[channel_name]
            self.admin.channel_event('destroy_channel', channel_name, None)

    def exists_channel(self, channel_name):
        return channel_name in self.channels

    def get_channel(self, conn, channel_name):
        if channel_name not in self.channels:
            self.create_channel(conn, channel_name)
        return self.channels[channel_name]

    def maybe_auto_subscribe(self, user, options, conn=None):
        #print 'maybe autosubscribe....'
        use_conn = conn if conn else user
        for destination in options.get('auto_subscribe', ()):
            #print 'subscribing to', destination
            channel = self.get_channel(use_conn, destination)
            channel.subscribe(user, conn=conn, needs_auth=False)
        for destination in options.get('auto_unsubscribe', ()):
            channel = self.get_channel(use_conn, destination)
            channel.unsubscribe(user, conn=conn, needs_auth=False)



class SockWebSocketWrapper(object):
    def __init__(self, ws):
        self._ws = ws

    def recv(self, num):
        # not quite right (ignore num)... but close enough for our use.
        data = self._ws.wait()
        if data:
            data = data.encode('utf-8')
        return data

    def send(self, data):
        self._ws.send(data)
        return len(data)
        
    def sendall(self, data):
        self.send(data)

    def __getattr__(self, key):
        return getattr(self._ws, key)
