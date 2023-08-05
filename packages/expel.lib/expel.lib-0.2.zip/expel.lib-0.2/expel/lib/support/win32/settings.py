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

from os import makedirs
from os.path import exists
import ctypes
import _winreg

class paths(object):
    def __init__(self):
        MAX_PATH = 260
        CSIDL_COMMON_APPDATA = 0x23
        
        SHGetSpecialFolderPath = ctypes.windll.shell32.SHGetSpecialFolderPathW
        buf = ctypes.create_unicode_buffer(MAX_PATH)
        if not SHGetSpecialFolderPath(None, buf, CSIDL_COMMON_APPDATA, 0):
            raise IOError('Unable to locate common application data folder')
        
        xpl_directory = '%s\\xPL' % buf.value
        
        self._items = {
            'xPLDirectory': xpl_directory, 
            'PluginDirectory': '%s\\plugins' % xpl_directory,
            'ConfigDirectory': '%s\\config' % xpl_directory,
            'PidDirectory': '%s\\pid' % xpl_directory,
        }

    def __getitem__(self, key):
        return self._items[key]

    def get(self, key, default):
        return self._items.get(key, default)
        
    def create(self):
        for d in self._items.values():
            if d != '':
                if not exists(d):
                    makedirs(d)


class xpl(object):
    def __init__(self):
        self._items = None
    
        self.xpl_key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
            'SOFTWARE\\xPL')

    def __getitem__(self, key):
        if self._items is None:
            self._load()
            
        return self._items[key]

    def get(self, key, default):
        if self._items is None:
            self._load()
            
        return self._items.get(key, default)
    
    def _load(self):
        self._items = {}
        self._items['BroadcastAddress'] = _winreg.QueryValueEx(self.xpl_key,
            'BroadcastAddress')[0]
    
        self._items['ListenOnAddress'] = _winreg.QueryValueEx(self.xpl_key,
            'ListenOnAddress')[0]
    
        self._items['ListenToAddresses'] = _winreg.QueryValueEx(self.xpl_key,
            'ListenToAddresses')[0]

    def create(self):
        xpl_key = None
        try:
            xpl_key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                'SOFTWARE\\xPL')
        except:
            key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE')
            xpl_key = _winreg.CreateKey(key, 'xPL')

        try:
            _winreg.QueryValueEx(xpl_key, 'BroadcastAddress')[0]
        except:
            _winreg.SetValueEx(xpl_key, 'BroadcastAddress', 0,
                _winreg.REG_SZ, '255.255.255.255')

        try:
            _winreg.QueryValueEx(xpl_key, 'ListenOnAddress')[0]
        except:
            ip_address =  'ANY_LOCAL'
            _winreg.SetValueEx(xpl_key, 'ListenOnAddress', 0, _winreg.REG_SZ,
                ip_address)

        try:
            _winreg.QueryValueEx(xpl_key, 'ListenToAddresses')[0]
        except:
            _winreg.SetValueEx(xpl_key, 'ListenToAddresses', 0, _winreg.REG_SZ,
                'ANY')
    