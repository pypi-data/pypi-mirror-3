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

__all__ = ['xPLPlugin', 'xPLDevice', 'xPLCommand', 'xPLElement',
           'xPLPluginFile', 'xPLPluginFileManager']

import os.path

from urlparse import urlparse
from urllib import urlopen, urlretrieve
from urllib2 import URLError
from xml.sax.handler import ContentHandler
from xml.sax import make_parser

from expel.lib.config import xPLConfig, xPLConfigItem


class xPLPlugin(object):
    def __init__(self):
        self.vendor = ''
        self.version = ''
        self.plugin_url = ''
        self.info_url = ''
        self.devices = {}

    def device(self, id):
        return self.devices[id]


class xPLDevice(object):
    def __init__(self):
        self.id = ''
        self.description = ''
        self.version = ''
        self.url = ''
        self.commands = []
        self.triggers = []
        self.items = []

    def config(self):
        c = xPLConfig()
        
        for item in self.items:
            ci = xPLConfigItem(item['name'])
            ci.description = item.get('description', '')
            ci.format = item.get('format', '')
            c.append(ci)
            
        return c


class xPLCommand(object):
    def __init__(self):
        self.name = ''
        self.description = ''
        self.msg_type = ''
        self.msg_schema = ''
        self.elements = []


class xPLElement(object):
    def __init__(self):
        self.name = ''
        self.default = ''
        self.label = ''
        self.control_type = ''
        self.regexp = ''
        self.options = {}


class xPLPluginFile(object):
    def __init__(self):
        self.filename = ''
    
    def read(self, filename):
        self._plugin = xPLPlugin()
        
        self.filename = filename
        self._fp = open(filename)
        
        self._handler = self.PluginHandler(self._plugin)
        self._parser = make_parser()
        self._parser.setContentHandler(self._handler)
        
        self._parser.parse(self._fp)

    def plugin():
        def fget(self):
            return self._plugin
        
        return locals()
    
    plugin = property(**plugin())

    class PluginHandler(ContentHandler):
        IN_NONE = 0
        IN_REGEXP = 1
        
        def __init__(self, plugin):
            self.state = self.IN_NONE
            self.plugin = plugin
        
        def startElement(self, name, attrs):
            if name == 'xpl-plugin':
                self.plugin.version = attrs.get('version', '')
                self.plugin.vendor = attrs.get('vendor', '')
                self.plugin.plugin_url = attrs.get('plugin_url', '')
                self.plugin.info_url = attrs.get('info_url', '')
                
            elif name == 'device':
                self.device = xPLDevice()
                
                id = attrs['id']
                self.device.id = id
                self.device.description = attrs.get('description', '')
                self.device.version = attrs.get('version', '')
                self.device.url = attrs.get('url', '')
                
                self.plugin.devices[id] = self.device
                
            elif name == 'command':
                self.cmd = xPLCommand()
                
                self.cmd.name = attrs.get('name', '')
                self.cmd.description = attrs.get('description', '')
                self.cmd.msg_type = attrs.get('msg_type', '')
                self.cmd.msg_schema = attrs.get('msg_schema', '')
                
                self.device.commands.append(self.cmd)
                
            elif name == 'trigger':
                self.cmd = xPLCommand()
                
                self.cmd.name = attrs.get('name', '')
                self.cmd.description = attrs.get('description', '')
                self.cmd.msg_type = attrs.get('msg_type', '')
                self.cmd.msg_schema = attrs.get('msg_schema', '')
                
                self.device.triggers.append(self.cmd)

            elif name == 'element':
                self.elem = xPLElement()
                
                self.elem.name = attrs.get('name', '')
                self.elem.default = attrs.get('default', '')
                self.elem.label = attrs.get('label', '')
                self.elem.control_type = attrs.get('control_type', '')
                
                self.cmd.elements.append(self.elem)
                
            elif name == 'regexp':
                self.state = self.IN_REGEXP
            
            elif name == 'option':
                label = attrs['label']
                value = attrs['value']
                self.elem.options[label] = value
            
            elif name == 'configItem':
                item = {'name': attrs.get('name', ''),
                        'description': attrs.get('description', ''),
                        'format': attrs.get('format', '')}

                self.device.items.append(item)
            
        def endElement(self, name):
            if name == 'xpl-plugin':
                pass
            elif name == 'device':
                pass
            elif name == 'command':
                pass
            elif name == 'element':
                pass
            elif name == 'regexp':
                if self.state == self.IN_REGEXP:
                    self.state = self.IN_NONE
            elif name == 'option':
                pass
            elif name == 'configItem':
                pass
            elif name == 'trigger':
                pass

        def characters(self, chars):
            if self.state == self.IN_REGEXP:
                self.elem.regexp += chars


class xPLPluginFileManager(object):
    PLUGIN_LIST_URLS = ['http://www.xplproject.org.uk/plugins.xml',
                             'http://www.xpl.myby.co.uk/support/xplhalweb/plugins.xml']
    
    def __init__(self):
        self.plugins = []
        self.locations = []
    
    def download(self, directory):
        stream = None
        for list_url in self.PLUGIN_LIST_URLS:
            try:
                stream = urlopen(list_url)
                break
            except URLError:
                continue
            
        if stream is None:
            raise IOError('Unable to download plugin list')

        self._parser = make_parser()
        self._parser.setContentHandler(self.PluginListHandler(self))
        self._parser.parse(stream)
        stream.close()
        
        failed_plugins = []
        for plugin in self.plugins:
            url = ''
            try:
                url = '%s.xml' % plugin['url']
                filename = self.url_to_filename(url)
                filename = os.path.join(directory, filename)
                urlretrieve(url, filename)
            except:
                failed_plugins.append((plugin['name'], url))
                
        if len(failed_plugins) > 0:
            err_msg = 'Failed to download the following plugins\n'
            for info in failed_plugins:
                err_msg += '    %s from %s\n' % info
                
            raise IOError(err_msg)

    def url_to_filename(self, url):
        p = urlparse(url)
        filename = p.path.rsplit('/', 1)[1]
        return filename
    
    class PluginListHandler(ContentHandler):
        def __init__(self, manager):
            self.manager = manager
        
        def startElement(self, name, attrs):
            if name == 'plugin':
                plugin = {}
                plugin['name'] = attrs.get('name', '')
                plugin['type'] = attrs.get('type', '')
                plugin['url'] = attrs.get('url', '')
                plugin['description'] = attrs.get('description', '')
                self.manager.plugins.append(plugin)
            elif name == 'location':
                url = attrs.get('url', '')
                if url != '' and url not in self.manager.locations:
                    self.manager.locations.append(url)
