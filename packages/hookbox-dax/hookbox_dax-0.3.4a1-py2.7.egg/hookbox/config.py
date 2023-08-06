from optparse import OptionParser

class NoDefault(object):

    def __nonzero__(self):
        return False

class DefaultObject(object):
    pass

class HookboxOptionParser(object):

    def __init__(self, defaults):
        parser = OptionParser()
        self._add_logging_options(parser, defaults)
        self._add_csp_options(parser, defaults)
        self._add_callback_interface_options(parser, defaults)
        self._add_callback_path_options(parser, defaults)
        self._add_admin_options(parser, defaults)
        self._parser = parser

    def parse_arguments(self, arguments):
        options, args = self._parser.parse_args(arguments)
        option_dict = dict((attr, getattr(options, attr))
                           for attr in dir(options)
                           if self._is_hookbox_attr(attr))
        return (option_dict, args)

    def _is_hookbox_attr(self, attr):
        return (not attr.startswith('_')) and \
            (attr not in ('ensure_value', 'read_file', 'read_module'))

    def _add_logging_options(self, parser, defaults):
        parser.add_option("-E", "--log-file-errors",
                          dest="log_file_err", type="string",
                          default=defaults._log_file_err, metavar="LOG_FILE",
                          help="Log all warnings/errors to LOG_FILE, (default: %default)")
        parser.add_option("-A", "--log-file-access",
                          dest="log_file_access", type="string",
                          default=defaults._log_file_access, metavar="LOG_FILE",
                          help="Log all access events to LOG_FILE, (default: %default)")
        parser.add_option("-L", "--log-level",
                          dest="log_level_name", type="string",
                          default=defaults._log_level_name, metavar="LOG_LEVEL",
                          help="Set logging level to LOG_LEVEL, (default: %default)")


    def _add_csp_options(self, parser, defaults):
        """ add options specific to the CSP interface """
        parser.add_option("-i", "--interface",
                          dest="interface", type="string",
                          default=defaults._interface, metavar="IFACE",
                          help="bind listening socket to IFACE, (default: %default)")
        parser.add_option("-p", "--port",
                          dest="port", type="int",
                          default=defaults._port, metavar="PORT",
                          help="bind listening socket to PORT, (default: %default)")
        parser.add_option("-w", "--web-api-port",
                          dest="web_api_port", type="int",
                          default=defaults._web_api_port, metavar="WEBAPIPORT",
                          help="bind web api listening socket to WEBAPIPORT, (default: %default)")
        parser.add_option("-W", "--web-api-interface",
                          dest="web_api_interface", type="string",
                          default=defaults._web_api_interface, metavar="WEBAPIINTERFACE",
                          help="bind web api listening socket to WEBAPIINTERFACE, (default: %default)")
        parser.add_option('-x', '--ignore-publish-non-existing-channels',
                          dest="ignore_publish_non_existing_channels",
                          default=defaults._ignore_publish_non_existing_channels,
                          help="ignore if publishing to a not existing channels")
    
    def _add_callback_interface_options(self, parser, defaults):
        """ add options related to the hookbox callbacks """
        parser.add_option("--cbport",
                          dest="cbport", type="int",
                          default=defaults._cbport, metavar="PORT",
                          help="Make http callbacks to PORT, (default: %default)")
        parser.add_option("--cbhost",
                          dest="cbhost", type="string",
                          default=defaults._cbhost, metavar="HOST",
                          help="Make http callbacks to HOST, (default: %default)")
        parser.add_option("--cbpath",
                          dest="cbpath", type="string",
                          default=defaults._cbpath, metavar="PATH",
                          help="Make http callbacks to base PATH, (default: %default)")
        parser.add_option("-c", "--cookie-identifier",
                          dest="cookie_identifier", type="string",
                          metavar="COOKIE_IDENTIFIER",
                          help="The name of the cookie field used to identify unique sessions.")
        parser.add_option("-s", "--webhook-secret",
                          dest="webhook_secret", type="string",
                          metavar="WEBHOOK_SECRET",
                          help="The WEBHOOK_SECRET token to pass to all webhook callbacks as form variable \"secret\".")
        parser.add_option("--cbhttps",
                          dest="cbhttps", action="store_true",
                          default=defaults._cbhttps, metavar="HTTPS",
                          help="Use https (instead of http) to make callbacks.")
        parser.add_option("--cbtrailingslash",
                          dest="cbtrailingslash", action="store_true",
                          default=defaults._cbtrailingslash,
                          help="Append a trailing slash to the callback URL.")
        parser.add_option("--cbsendhookboxversion",
                          dest="cbsendhookboxversion", action="store_true",
                          default=defaults._cbsendhookboxversion, metavar="SEND_HOOKBOX_VERSION",
                          help="Send hookbox version info to webhook callbacks using X-Hookbox-Version header.")
    
    def _add_callback_path_options(self, parser, defaults):
        parser.add_option('--cb-connect', 
                          dest='cb_connect', type='string', 
                          default=defaults._cb_connect,
                          help='relative path for connect webhook callbacks. (default: %default)')
        parser.add_option('--cb-disconnect', 
                          dest='cb_disconnect', type='string', 
                          default=defaults._cb_disconnect,
                          help='relative path for disconnect webhook callbacks. (default: %default)')
        parser.add_option('--cb-create_channel', 
                          dest='cb_create_channel', type='string', 
                          default=defaults._cb_create_channel,
                          help='name for create_channel webhook callbacks. (default: %default)')
        parser.add_option('--cb-destroy_channel', 
                          dest='cb_destroy_channel', type='string', 
                          default=defaults._cb_destroy_channel,
                          help='name for destroy_channel webhook callbacks. (default: %default)')
        parser.add_option('--cb-subscribe', 
                          dest='cb_subscribe', type='string', 
                          default=defaults._cb_subscribe,
                          help='name for subscribe webhook callbacks. (default: %default)')
        parser.add_option('--cb-unsubscribe', 
                          dest='cb_unsubscribe', type='string', 
                          default=defaults._cb_unsubscribe,
                          help='relative path for unsubscribe webhook callbacks. (default: %default)')
        parser.add_option('--cb-publish', 
                          dest='cb_publish', type='string', 
                          default=defaults._cb_publish,
                          help='relative path for publish webhook callbacks. (default: %default)')
        parser.add_option('--cb-message', 
                          dest='cb_message', type='string', 
                          default=defaults._cb_message,
                          help='relative path for message webhook callbacks. (default: %default)')
                          
        parser.add_option("--cb-single-url",
                          dest='cb_single_url', type='string', 
                          default=defaults._cb_single_url,
                          help='Override to send all callbacks to given absolute url.')
        
    def _add_admin_options(self, parser, defaults):
        parser.add_option("-r", "--api-security-token", 
                          dest="api_security_token", type="string", 
                          default=defaults._rest_secret, metavar="SECRET",
                          help="The SECRET token that must be in present in all web/rest api calls as the form variable \"secret\".")
        parser.add_option("-a", "--admin-password", 
                          dest="admin_password", type="string", 
                          default=defaults._admin_password,
                          help='password used for admin web access.')
        parser.add_option("-d", "--debug", 
                          dest="debug", action="store_true", 
                          default=defaults._debug,
                          help="Run in debug mode (recompiles hookbox.js whenever the source changes)")
        parser.add_option("-o", "--objgraph", 
                          dest="objgraph", type="int",
                          default=defaults._objgraph,
                          help="turn on objgraph")

class HookboxConfig(object):
    """ The hookbox config holds server configuration data
    """

    # define the defaults here
    defaults = DefaultObject()
    defaults._log_file_err = None
    defaults._log_file_access = None
    defaults._log_level_name = 'INFO'
    defaults._interface = '0.0.0.0'
    defaults._port = 8001
    defaults._web_api_port = None
    defaults._web_api_interface = None
    defaults._cbport = 80
    defaults._cbhost = '127.0.0.1'
    defaults._cbpath = '/hookbox'
    defaults._cookie_identifier = NoDefault()
    defaults._webhook_secret = NoDefault()
    defaults._cbhttps = False
    defaults._cbtrailingslash = False
    defaults._cbsendhookboxversion = False
    defaults._cb_connect = 'connect'
    defaults._cb_disconnect = 'disconnect'
    defaults._cb_create_channel = 'create_channel'
    defaults._cb_destroy_channel = 'destroy_channel'
    defaults._cb_subscribe = 'subscribe'
    defaults._cb_unsubscribe = 'unsubscribe'
    defaults._cb_publish = 'publish'
    defaults._cb_message = 'message'
    defaults._cb_single_url = NoDefault()
    defaults._rest_secret = NoDefault()
    defaults._admin_password = NoDefault()
    defaults._debug = False
    defaults._objgraph = 0
    defaults._ignore_publish_non_existing_channels = False
    
    def __init__(self):
        config_items = [attr for attr in dir(self.defaults)
                        if not attr.startswith('__')]
        for config_item in config_items:
            setattr(self, config_item[1:],
                    getattr(self.defaults, config_item))

    def update_from_commandline_arguments(self, args):
        parser = HookboxOptionParser(self.defaults)
        options, arguments = parser.parse_arguments(args)
        for attr in options:
            setattr(self, attr, options[attr])

    get = __getitem__ = lambda self, attr: getattr(self, attr)
    set = __setitem__ = lambda self, attr, val: setattr(self, attr, val)
