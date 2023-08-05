# Copyright (c) 2009-2011 Simon Kennedy <code@sffjunkie.co.uk>.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import socket
import logging
import glob
from random import randint
from optparse import OptionParser, OptionGroup

from twisted.internet.protocol import DatagramProtocol

from expel.lib.reactor.console import consoleReactor
from expel.message.xpl import xPLMessage
from expel.lib.event import xPLEvent
from expel.lib.filter import xPLFilterList
from expel.lib.config import xPLConfigFile, xPLConfig, xPLConfigError
from expel.lib.plugin import xPLPluginFile
from expel.lib.support import settings
from expel.lib.utility import fairly_unique_identifier, xpl_format_source, \
    find_open_port, find_local_address, \
    indent_print, indent_text

__all__ = ['xPLLooper']

XPL_HUB_PORT = 3865
XPL_HUB_DISCOVERY_INTERVAL = 10 # seconds
XPL_HUB_DISCOVERY_INTERVAL_SLOW = 30 # seconds
XPL_HBEAT_DEFAULT_INTERVAL = 5 # minutes
XPL_PORT_BASE = 50000


class xPLLooper(object, DatagramProtocol):
    """
    xPLLooper is used to process xPL messages.

    The looper waits for messages on a free UDP port and handles the basic
    processing required of an xPL device i.e. it...

     * Discovers a hub.
     * Sends heart-beat messages.
     * Responds to heart-beat requests.
     * Handles device configuration.
     * Sends events when the instance changes, a message is received (both valid
       and invalid ones) or the state of the looper changes.

    The 'instance_changed' event handler is called with a single argument

     * The new instance name

    The 'state_changed' event handler is called with a single argument

     * The state number

       0 = Initialising
       1 = Probing for hub
       2 = Awaiting Configuration
       3 = Running
       4 = Stopped

    The 'message_received' event handler is called with 2 arguments

     * The xPLMessage received and
     * The address from where the message originated.

    Note: We subclass from object as well as DatagramProtocol to add property
    handling as DatagramProtocol is not a new style class.
    """

    INIT = 0
    PROBE_FOR_HUB = 1
    AWAITING_CONFIGURATION = 2
    RUNNING = 3
    STOPPED = 4

    def __init__(self, reactorKlass=consoleReactor):
        self._reactor = reactorKlass()

        self._title = ''
        self._vendor = ''
        self._device = ''
        self._instance = ''
        self._source = ''
        
        self._version = ''
        self._state = xPLLooper.INIT

        self._device = None
        self._config = None
        self._options = None
        
        self._logger = None
        self._log_file = ''
        self._log_level = logging.DEBUG

        self._address = ''
        self._port = -1
        self._broadcast_address = ''

        self._interval = XPL_HBEAT_DEFAULT_INTERVAL
        self._hub_probe_interval = XPL_HUB_DISCOVERY_INTERVAL
        self._hub_probe_total = 0

        self.groups = []
        self.match_filters = xPLFilterList()

        self.MessageReceived = xPLEvent(self)
        self.InvalidMessageReceived = xPLEvent(self)
        self.InstanceChanged = xPLEvent(self)
        self.ConfigChanged = xPLEvent(self)
        self.StateChanged = xPLEvent(self)
        
        self.xpl_settings = settings.xpl()
        self.path_settings = settings.paths()

    def vendor():
        doc = """The vendor ID : 1-8 characters long"""
        
        def fget(self):
            return self._vendor

        def fset(self, value):
            value = str(value)
            if value == '':
                raise ValueError("'vendor' cannot be set to an empty string")
            
            if len(value) > 8:
                self.logger.warning('%s: Vendor ID (%s) > 8 characters - Truncating' % (self.title, value))
                value = value[:8]
    
            self._vendor = value
            
            if self._device != '' and self._instance != '':
                self._source = xpl_format_source(self._vendor, self._device,
                    self._instance)
                self._set_heartbeat()

        return locals()

    vendor = property(**vendor())

    def device():
        doc = """The device ID : 1-8 characters long"""
        
        def fget(self):
            return self._device

        def fset(self, value):
            value = str(value)
            if value == '':
                raise ValueError("'device' cannot be set to an empty string")
            
            if len(value) > 8:
                self.logger.warning('%s: Device ID (%s) > 8 characters - Truncating' % (self.title, value))
                value = value[:8]

            self._device = value
            
            if self._vendor != '' and self._instance != '':
                self._source = xpl_format_source(self._vendor, self._device,
                    self._instance)
                self._set_heartbeat()

        return locals()

    device = property(**device())

    def instance():
        doc = """The instance ID : 1-16 characters long"""
        
        def fget(self):
            return self._instance

        def fset(self, new_instance):
            new_instance = str(new_instance)
            if new_instance == '' and self._instance != '':
                raise ValueError("'instance' cannot be cleared once set.")
            
            if len(new_instance) > 16:
                self.logger.warning('%s: Instance ID (%s) > 16 characters - Truncating' % (self.title, new_instance))
                new_instance = new_instance[:16]

            if new_instance != self.instance:
                old_instance = self.instance
                if self.state == xPLLooper.RUNNING:
                    self._heartbeat_end()
                    self._delete_pid()
                    
                    self._instance = new_instance
                    self._config.instance = new_instance

                    # source must be changed before creating new pid and
                    # sending heartbeat
                    self._source = xpl_format_source(self._vendor, self._device,
                        self._instance)
                    
                    self.logger.info('%s: Instance ID changed to %s' % \
                        (self.title, new_instance))
                    
                    self._create_pid()
                    self._set_heartbeat()
                    self._heartbeat()
                else:
                    self._instance = new_instance
                    self._config.instance = new_instance
                    self._set_heartbeat()

                    self._source = xpl_format_source(self._vendor, self._device,
                        self._instance)

                self.InstanceChanged(new_instance, old_instance)

        return locals()

    instance = property(**instance())

    def version():
        doc = """The looper version - Used in diagnostics messages"""
        
        def fget(self):
            return self._version

        def fset(self, value):
            self._version = value

        return locals()

    version = property(**version())

    def source():
        doc = """Get our formatted source string."""
        
        def fget(self):
            return self._source

        return locals()
        
    source = property(**source())

    def title():
        doc = """The looper title - Used in diagnostics messages"""
        
        def fget(self):
            return self._title

        def fset(self, value):
            if value != self._title:
                self._title = value

        return locals()

    title = property(**title())

    def state():
        doc = """The current state of the looper"""
        
        def fget(self):
            return self._state

        def fset(self, value):
            if value != self._state:
                self._state = value
                self.StateChanged(self._state)

        return locals()

    state = property(**state())

    def state_name():
        doc = """The name of the current state of the looper"""
        
        def fget(self):
            states = ['Initialising', 'Probing For Hub',
                      'Awaiting Configuration',
                      'Running', 'Stopped']
            
            return states[self._state]

        return locals()

    state_name = property(**state_name())

    def interval():
        doc = """The interval between heart-beat messages"""
        
        def fget(self):
            return self._interval

        def fset(self, value):
            self._interval = value

        return locals()

    interval = property(**interval())

    def address():
        doc = """The IP address on which to listen for xPL messages"""
        
        def fget(self):
            return self._address

        def fset(self, address):
            self._address = address

        return locals()

    address = property(**address())

    def port():
        doc = """The port on which to listen for xPL messages"""
        
        def fget(self):
            return self._port

        def fset(self, port):
            self._port = port

        return locals()

    port = property(**port())

    def broadcast_address():
        doc = """The IP address on which to broadcast xPL messages"""
        
        def fget(self):
            return self._broadcast_address

        return locals()

    broadcast_address = property(**broadcast_address())

    def reactor():
        def fget(self):
            return self._reactor
            
        return locals()

    reactor = property(**reactor())

    def logger():
        doc = """The logger to send messages to."""
        
        def fget(self):
            return self._logger

        return locals()

    logger = property(**logger())

    def plugin_device():
        doc = """Our current plugin device."""
        
        def fget(self):
            return self._plugin_device

        def fset(self, value):
            self._plugin_device = value

        return locals()

    plugin_device = property(**plugin_device())

    def config():
        doc = """Our current configuration."""
        
        def fget(self):
            return self._config

        def fset(self, value):
            self._config = value

        return locals()

    config = property(**config())

    def options():
        doc = """The parsed command line options."""
        
        def fget(self):
            return self._options

        return locals()

    options = property(**options())

    def args():
        doc = """The parsed command line args."""
        
        def fget(self):
            return self._args

        return locals()

    args = property(**args())

    def connected(self):
        """Determine if we are connected to a hub."""
        
        return (self._state == xPLLooper.AWAITING_CONFIGURATION or \
            self._state == xPLLooper.RUNNING) 

    def in_group(self, group):
        """Determine if looper is in a specific group"""
        
        return group in self.groups
        
    def add_options(self, parser):
        """Overridden by derived class to add argument handling."""
        
        pass

    def _add_options(self):
        """Add standard looper options to the parser."""

        self._parser = OptionParser()
        
        self.add_options(self._parser)
        
        std_opt = OptionGroup(self._parser, "Standard options")
        std_opt.add_option("-i", "--instance", dest="instance",
                           metavar='INSTANCE', default='',
                           help="Set xpl instance to INSTANCE.")
    
        std_opt.add_option("-e", "--event", action="store_true", default=False,
                           dest="event_log",
                           help="Send messages to the system event logger.")
    
        std_opt.add_option("-d", "--debug", action="store_true", default=False,
                           dest="debug",
                           help="Enable logging of debugging information.")
    
        std_opt.add_option("-f", "--file", dest="log_file", metavar='FILE',
                           default='',
                           help="Log information to FILE.")
            

        self._parser.add_option_group(std_opt)

    def configure(self):
        """Overridden by derived class."""
        
        pass

    def _configure(self):
        """Configure the looper's logging, network and instance id."""

        self._configure_logging()
        self._configure_network()
        
        if self.options.instance != '':
            if self._instance_is_running(self.options.instance):
                self.logger.warning('%s: Instance ID \'%s\' already running. Selecting new instance.' % (self.title, self.options.instance))
                self.instance = ''
            else:
                self.instance = self.options.instance
        
        self._load_plugin()
        self._load_config()

        filter_ = ''
        try:
            for filter_ in self.config['filter']:
                if filter_ != '*.*.*.*.*.*':
                    self.match_filters += filter_
        except ValueError:
            self.logger.warning("%s: Invalid filter '%s' specified - Ignoring." % (self.title, filter_))
        
        self.configure()

    def _configure_logging(self):
        """Configure loggers for the looper"""

        if self.options.debug == True:
            self._log_level = logging.DEBUG
        else:
            self._log_level = logging.INFO

        self._logger = logging.getLogger('expel')
        self._logger.setLevel(self._log_level)
        
        # Create formatter overriding ``datefmt`` to remove milliseconds from stream output
        sf = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
        sh = logging.StreamHandler()
        sh.setFormatter(sf)
        self._logger.addHandler(sh)

        self._log_file = self.options.log_file

        if self._log_file != '':
            ff = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
            fh = logging.FileHandler(self._log_file)
            fh.setFormatter(ff)
            self._logger.addHandler(fh)

        if self.options.event_log:
            ef = logging.Formatter('%(levelname)-8s %(message)s')
            
            if os.name == 'nt':
                from logging.handlers import NTEventLogHandler
                eh = NTEventLogHandler(self.title)
            else:
                from logging.handlers import SysLogHandler
                eh = SysLogHandler()
                
            eh.setFormatter(ef)
            self._logger.addHandler(eh)

    def _configure_network(self):
        """Configure networking properties for the looper"""

        self._address = find_local_address()
        self._port = find_open_port(XPL_PORT_BASE)
        self._listen_to = self.xpl_settings['ListenToAddresses']
        self._broadcast_address = self.xpl_settings['BroadcastAddress']

    def run(self):
        """Overridden by subclass"""
        
        pass

    def __call__(self):
        """Start the looper."""

        self.state = xPLLooper.PROBE_FOR_HUB

        self._add_options()
        (self._options, self._args) = self._parser.parse_args()
        self._configure()

        self.logger.info('%s: Starting %s on %s:%d' % (self.title, self.source,
            self.address, self.port))
        self._create_pid()
        
        self.run()
        
        self.reactor.listen(self)
        self.reactor.run()

    def stop(self):
        """Overridden by subclass"""
        
        pass

    def _stop(self):
        """Stop the looper
        
        Called by the reactor or signal handler.
        """

        if self.state != self.STOPPED:
            if self.connected():
                self._heartbeat_end()
    
            if self.logger is not None:
                self.logger.info('%s: Stopping %s' % (self.title, self.source))
                
            self._save_config()
            self._delete_pid()
            self.stop()
            
            self.port = -1
            self.state = self.STOPPED

    def _instance_is_running(self, instance):
        """Check if an instance is running."""
        
        return instance in self._running_instances()

    def _strip_prefix(self, name):
        file_prefix = '%s-%s.' % (self.vendor, self.device)
        if name.startswith(file_prefix):
            name = name[len(file_prefix):]
            
        return name

    def _running_instances(self):
        """Get a list of all the pid files in the pid directory."""
        
        pid_directory = self.path_settings['PidDirectory']
        files = glob.glob(os.path.join(pid_directory, '*.pid'))
        if len(files) != 0:
            instances = map(lambda x: self._strip_prefix(os.path.splitext(os.path.basename(x))[0]), files)
            return instances
        else:
            return []

    def _create_pid(self):
        """Create a file in the pid directory using our name to indicate that we are running."""
        
        filename = os.path.join(self.path_settings['PidDirectory'], '%s.pid' % self.source)
        self._pid = open(filename, 'w')
        self._pid.write(str(os.getpid()))
        self._pid.flush()

    def _delete_pid(self):
        """Delete our pid file when exiting."""
        
        self._pid.close()
        filename = os.path.join(self.path_settings['PidDirectory'], '%s.pid' % self.source)
        try:
            os.remove(filename)
        except:
            pass

    def _load_plugin(self):
        """Load our plugin."""
        
        filename = os.path.join(self.path_settings['PluginDirectory'], '%s.xml' % self.vendor)

        plugin_file = xPLPluginFile()
        plugin_file.read(filename)
        
        device_name = '%s-%s' % (self.vendor, self.device)

        try:
            self._plugin_device = plugin_file.plugin.device(device_name)
            self.version = self._plugin_device.version
            self._config = self._plugin_device.config()
        except:
            self._device_info = None
            self._config = xPLConfig()
        
        self._config.add_std_items()

    def _load_config(self):
        """Load a configuration.
        
        If a configuration for a non running instance is found then use that
        otherwise generate a new instance."""
        
        directory = self.path_settings['ConfigDirectory']
        filename = '%s-%s.ini' % (self.vendor, self.device)
        filename = os.path.join(directory, filename)
        config_file = xPLConfigFile()
        
        config = None
        try:
            config_file.read(filename)
    
            if self.instance != '':
                config = config_file.get(self.instance)
            else:
                running = self._running_instances()
        
                for c in config_file.configs.values():
                    if c.instance not in running:
                        config = c
                        break
    
        except xPLConfigError:
            config = None
        
        # Update the self._config we created in _load_plugin
        if config is not None:
            self._config.merge(config)
            self.instance = self._config.instance
        else:
            if self.instance != '':
                self._config.instance = self.instance
            else:
                self._config.instance = fairly_unique_identifier(self.address)
                self.instance = self._config.instance
                
            self._config.new = True
            
    def _save_config(self):
        if self._config is None:
            return
        
        if self._config.new or self._config.dirty:
            directory = self.path_settings['ConfigDirectory']
            filename = '%s-%s.ini' % (self.vendor, self.device)
            filename = os.path.join(directory, filename)
            config_file = xPLConfigFile()
            
            try:
                config_file.write(self._config, filename)
                self.logger.debug('%s: Configuration saved to %s.' % (self.title, filename))
            except:
                self.logger.error('%s: Unable to save configuration to %s.' % (self.title, filename))
                raise

    def startProtocol(self):
        """Called by the Twisted framework when the reactor starts."""

        # Convert socket to a broadcast socket
        self.transport.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)

        self.logger.debug('%s: Hub discovery started.' % self.title)
        self._set_heartbeat()
        self._discover_hub()

    def datagramReceived(self, datagram, address):
        """Called by the Twisted framework when a UDP datagram appears on the listening port."""

        if datagram[:4] == 'xpl-':
            try:
                msg = xPLMessage(raw=datagram)
            except Exception, exc:
                self.logger.warning('%s: Incorrectly formed xPL message received from %s:%d' %
                    (self.title, address[0], address[1]))
                indent_print('%s: %s' % (self.title, str(exc)))
                indent_print(datagram)
                self.InvalidMessageReceived(datagram, address)
            else:
                self._handle_message(msg, address)

        elif len(datagram) > 0:
            self.logger.warning('%s: Unrecognised datagram received from %s:%d\n%s' %
                (self.title, address[0], address[1], indent_text(datagram)))

            self.InvalidMessageReceived(datagram, address)

    def _handle_message(self, msg, address):
        """Called by datagramReceived when a valid xPL message is received."""

        source = msg.source.lower()

        if self.state == xPLLooper.PROBE_FOR_HUB:
            if source == self.source:
                self.logger.info('%s: Reply from hub received. Joined xPL network.' % self.title)

                if self._config is None or self._config.is_complete():
                    self.state = xPLLooper.RUNNING
                else:
                    self.state = xPLLooper.AWAITING_CONFIGURATION
                
                self.reactor.call_later(self.interval * 60, self._regular_heartbeat)
        else:
            msg_type = msg.message_type.lower()
            target = msg.target.lower()
            schema_class = msg.schema_class.lower()
            schema_type = msg.schema_type.lower()
    
            address = address[0]
            #port = int(address[1])

            # If we've been sent a `config` message
            if msg_type == 'cmnd' and schema_class == 'config':
                if self._config is not None:
                    # And we've been sent our new configuration
                    if target == self.source and schema_type == 'response':
                        changed = self._config.set_to(msg.items())

                        # Update our instance id
                        # (this may emit an InstanceChanged event)
                        self.instance = self._config.instance
                        
                        if changed:
                            self.ConfigChanged(msg)

                        if self.state == xPLLooper.PROBE_FOR_HUB:
                            # If we now have all the information we need switch
                            # to the running state
                            if self._config.is_complete():
                                self.state = xPLLooper.RUNNING
                            else:
                                self.state = xPLLooper.AWAITING_CONFIGURATION
                            
                        self.instance = self._config.instance
                            
                        self._set_heartbeat()
                        self._heartbeat()
    
                    # Or somebody wants our configuration info
                    elif target == self.source or target == '*':
                        if schema_type == 'list':
                            body = self._config.list_response
                            reply = xPLMessage.CONFIG_LIST_RAW % (self.source, body)
    
                            self.logger.debug('%s: Sending config.list reply %s' % (self.title, reply.replace('\n', ' ')))
                            self._broadcast_datagram(reply)
    
                        elif schema_type == 'current':
                            body = self._config.current_response
                            reply = xPLMessage.CONFIG_CURRENT_RAW % (self.source, body)
    
                            self.logger.debug('%s: Sending config.current reply %s' % (self.title, reply.replace('\n', ' ')))
                            self._broadcast_datagram(reply)
                else:
                    self._heartbeat()

            elif msg_type == 'cmnd' and schema_class == 'hbeat' and schema_type == 'request':
                if target == '*':
                    delay = randint(1, 5) + 1
                    self.reactor.call_later(delay, self._heartbeat)
                else:
                    self._heartbeat()
                    
            elif msg_type == 'cmnd' and schema_class == 'device' and schema_type == 'control':
                command = msg['command'].lower()
                if (command == 'quit' and target == self.source) or command == 'shutdown':
                    self.logger.info('%s: Closing down; %s message received' % (self.title, command))
                    self._reactor.stop()

        if self.match_filters.target_match(msg):
            self.MessageReceived(msg, address)

    def broadcast_message(self, message):
        """Send a message on our broadcast address."""

        if message is not None:
            if isinstance(message, xPLMessage):
                self._broadcast_datagram(message.raw)
            else:
                self._broadcast_datagram(message)

    def _broadcast_datagram(self, datagram):
        """Send a datagram on our broadcast address."""

        if datagram != '':
            try:
                self.transport.write(datagram, (self._broadcast_address, XPL_HUB_PORT))
            except socket.error:
                self.logger.error('%s: Unable to send datagram to %s' % (self.title, self._broadcast_address)) 

    def _discover_hub(self):
        """Send xPL heart-beat message to probe for an xPL hub."""

        if self.state == xPLLooper.PROBE_FOR_HUB:
            self.logger.debug('%s: Sending discovery message' % self.title)
            self._broadcast_datagram(self._heartbeat_raw())

            self._hub_probe_total += self._hub_probe_interval

            if self._hub_probe_total > 120 and self._hub_probe_interval != XPL_HUB_DISCOVERY_INTERVAL_SLOW:
                self.logger.warning('%s: No reply from hub received within 2 minutes. Changing to slow probe rate.' % self.title)
                self._hub_probe_interval = XPL_HUB_DISCOVERY_INTERVAL_SLOW

            self.reactor.call_later(self._hub_probe_interval, self._discover_hub)

    def _heartbeat(self):
        """Send a single heart-beat."""
        
        self.logger.debug('%s: Sending heartbeat', self.title)
        self._broadcast_datagram(self._heartbeat_raw())

    def _regular_heartbeat(self):
        """Send an xPL heart-beat at regular intervals."""

        if self.connected():
            self._heartbeat()
            self.reactor.call_later(self.interval * 60, self._regular_heartbeat)

    def _heartbeat_end(self):
        """Send a heart-beat end"""
        
        self.logger.debug('%s: Sending heart-beat end', self.title)
        self._broadcast_datagram(self._hbeatEnd)

    def _heartbeat_raw(self):
        """Returns the character for a raw xPL heart-beat message"""
        
        if self._state == xPLLooper.AWAITING_CONFIGURATION:
            return self._configApp
        else:
            if self.version == '':
                return self._hbeatApp
            else:
                return self._hbeatAppWithVer

    def _set_heartbeat(self):
        """Set the heart-beat messages based on the looper's properties"""
        
        self._hbeatApp = xPLMessage.HBEAT_APP_RAW % (self.source, self.interval, self.address, self.port)
        self._hbeatAppWithVer = xPLMessage.HBEAT_APPVER_RAW % (self.source, self.interval, self.address, self.port, self.version)
        self._hbeatEnd = xPLMessage.HBEAT_END_RAW % (self.source, self.interval, self.address, self.port)
        self._configApp = xPLMessage.CONFIG_APP_RAW % (self.source, self.interval, self.address, self.port)
        