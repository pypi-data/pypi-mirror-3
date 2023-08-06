import logging
import uuid
import eventlet
from errors import ExpectedException
import rtjp_eventlet

class HookboxConn(object):
    logger = logging.getLogger('HookboxConn')
    
    def __init__(self, server, rtjp_conn, config, remote_addr):
        self._rtjp_conn = rtjp_conn
        self.server = server
        self.state = 'initial'
        self.cookies = None
        self.cookie_string = None
        self.cookie_id = None
        self.cookie_identifier = config['cookie_identifier']
        self.id = str(uuid.uuid4()).replace('-', '')
        self.user = None
        self.remote_addr = remote_addr
        
    def serialize(self):
        return {
            "id": self.id,
            "user": self.user and self.user.get_name(),
            "cookie": self.cookie_string
        }
        
    def send_frame(self, *args, **kw):
        try:
            self._rtjp_conn.send_frame(*args, **kw).wait()

        except Exception, e:
            if 'closed' in str(e).lower() or 'not connected' in str(e).lower():
                pass
            else:
                self.logger.warn("Unexpected error: %s", e, exc_info=True)
                self.logger.warn("Unexpected error: connection %s" % self.id)
                self.logger.warn("Unexpected error: frame args %s" % (args,))
                self.logger.warn("Unexpected error: frame kwargs %s" % kw)
                self.logger.warn("Unexpected error: user %s" % self.user.name)
                self.logger.warn("Unexpected error: other connections for user: %s" % [c.id for c in self.user.connections])
            return False

    def send_error(self, *args, **kw):
        return self._rtjp_conn.send_error(*args, **kw)

    def get_cookie(self):
        return self.cookie_string
        
    def get_id(self):
        return self.id
    
    def get_cookie_id(self):
        return self.cookie_id
    
    def get_remote_addr(self):
        return self.remote_addr

    def _close(self):
        if self.state == 'connected':
            self.server.closed(self)
        
    def run(self):
        while True:
            try:
                result = self._rtjp_conn.recv_frame().wait()

                if isinstance(result, rtjp_eventlet.errors.ConnectionLost):
                    self.logger.debug('received connection lost message')
                    break

                fid, fname, fargs = result

            except rtjp_eventlet.errors.ConnectionLost, e:
                self.logger.info('received connection lost exception')
                break

            except:
                self.logger.warn("Error reading frame", exc_info=True)
                continue

            f = getattr(self, 'frame_' + fname, None)
            if f:
                try:
                    f(fid, fargs)
                except ExpectedException, e:
                    self.send_error(fid, e)
                except Exception, e:
                    self.logger.warn("Unexpected error: %s", e, exc_info=True)
                    self.send_error(fid, e)
            else:
                self._default_frame(fid, fname, fargs)

        # cleanup
        self.logger.debug('loop done')
        if self.user:
            self.logger.debug('cleanup user')
            self.user.remove_connection(self)
            self.server.disconnect(self)
        
    def _default_frame(fid, fname, fargs):
        pass
    
    def frame_CONNECT(self, fid, fargs):
        if self.state != 'initial':
            return self.send_error(fid, "Already logged in")
        if 'cookie_string' not in fargs:
            raise ExpectedException("Missing cookie_string")

        self.cookie_string = fargs['cookie_string']
        self.cookies = parse_cookies(fargs['cookie_string'])
        self.cookie_id = self.cookies.get(self.cookie_identifier, None)
        self.server.connect(self, fargs.get('payload', 'null'))
        self.state = 'connected'
    
    def frame_SUBSCRIBE(self, fid, fargs):
        if self.state != 'connected':
            return self.send_error(fid, "Not connected")
        if 'channel_name' not in fargs:
            return self.send_error(fid, "channel_name required")
        channel = self.server.get_channel(self, fargs['channel_name'])
        channel.subscribe(self.user, conn=self)
            
    def frame_UNSUBSCRIBE(self, fid, fargs):
        if self.state != 'connected':
            return self.send_error(fid, "Not connected")
        if 'channel_name' not in fargs:
            return self.send_error(fid, "channel_name required")
        channel = self.server.get_channel(self, fargs['channel_name'])
        channel.unsubscribe(self.user, conn=self)
    
    def frame_PUBLISH(self, fid, fargs):
        if self.state != 'connected':
            return self.send_error(fid, "Not connected")
        if 'channel_name' not in fargs:
            return self.send_error(fid, "channel_name required")
        channel = self.server.get_channel(self, fargs['channel_name'])
        channel.publish(self.user, fargs.get('payload', 'null'), conn=self)

    def frame_MESSAGE(self, fid, fargs):
        if self.state != 'connected':
            return self.send_error(fid, "Not connected")
        if 'name' not in fargs:
            return self.send_error(fid, "name required")
        self.user.send_message(fargs['name'], fargs.get('payload', 'null'), conn=self)
        
        
def parse_cookies(cookieString):
    output = {}
    for m in cookieString.split('; '):
        try:
            k,v = m.split('=', 1)
            output[k] = v
        except:
            continue
    return output
