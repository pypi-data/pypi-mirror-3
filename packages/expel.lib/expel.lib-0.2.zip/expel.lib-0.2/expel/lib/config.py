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

from __future__ import with_statement

from types import StringType
from configobj import ConfigObj

__all__ = ['xPLConfigItem', 'xPLConfig', 'xPLConfigFile',
    'xPLConfigError', 'xPLConfigWarning']

class xPLConfigError(StandardError):
    pass


class xPLConfigWarning(UserWarning):
    pass
        
        
class xPLConfigItem(object):
    """A single configuration item.
    
    A configuration item can store multiple items within the value (up to
    ``max_size`` items)"""
    
    CONFIG_TYPE_CONFIG = 'config'
    CONFIG_TYPE_RECONF = 'reconf'
    CONFIG_TYPE_OPTION = 'option'
    CONFIG_TYPES = [CONFIG_TYPE_CONFIG, CONFIG_TYPE_RECONF, CONFIG_TYPE_OPTION]

    def __init__(self, item='', value=[], config_type=CONFIG_TYPE_OPTION, max_size=1):
        """Create an configuration item.
        
        :param item:        Either an xPLConfigItem in which case construct
                            a copy or the name of the item.
        :type item:         xPLConfigItem or str
        :param config_type: The type of config item to construct.
        :type config_type:  One of
                            xPLConfigItem.CONFIG_TYPE_CONFIG, 'config'
                            xPLConfigItem.CONFIG_TYPE_RECONF, 'reconf'
                            xPLConfigItem.CONFIG_TYPE_OPTION, 'option'
        :param max_size:    The maximum number of values to store
        :type max_size:     integer
        :param value:       The initial value to assign
        """
        
        if isinstance(item, xPLConfigItem):
            item_name = item.name
            item_value = item.value
            item_config_type = item.config_type
            item_max_size = item.max_size
        else:
            item_name = item
            item_value = value
            item_config_type = config_type
            item_max_size = max_size
            
        if isinstance(item_value, list):
            item_value = value[:max_size]
            self._as_list = True
        else:
            item_value = [value]
            self._as_list = False

        self._name = item_name
        self._value = item_value
        self._config_type = item_config_type
        self._max_size = item_max_size
        
        self.description = ''
        self.format = ''

        self._dirty = False

    def __getitem__(self, index):
        """Get an item from the value"""
        
        return self._value[index]

    def __setitem__(self, index, value):
        """Set an item in the value"""

        if isinstance(index, slice):
            stop = index.stop
            if stop > self._max_size:
                stop = self._max_size
                for x in range(index.start, stop, index.step):
                    self._value[x] = value
        else:        
            if index > self._max_size:
                raise IndexError('Maximum index is %d' % self._max_size)
            else:
                if index+1 > len(self._value):
                    # Fill in with None values
                    for x in range(index - len(self._value) + 1):
                        self._value.append(None)
    
                self._value[index] = value
                self._dirty = True

    def name():
        def fget(self):
            return self._name

        def fset(self, value):
            self._name = value
            self._dirty = True

        return locals()

    name = property(**name())

    def value():
        def fget(self):
            if self.size == 1 and not self._as_list:
                return self._value[0]
            else:
                return self._value
            
        def fset(self, value):
            if isinstance(value, list):
                if self._max_size != -1:
                    if len(value) > self._max_size:
                        raise xPLConfigWarning('Truncating value: Value specified (%s) has more than \'max_size\' (%d) elements' %
                            (value, self._max_size))

                    self._value = value[:int(self._max_size)]
                self._as_list = True
            else:
                self._value = [value]
                self._as_list = False

            self._dirty = True

        return locals()

    value = property(**value())

    def config_type():
        def fget(self):
            return self._config_type

        def fset(self, value):
            if value not in self.CONFIG_TYPES:
                raise ValueError('config_type must be one of %s' %
                    ', '.join(self.CONFIG_TYPES))
                
            self._config_type = value
            self._dirty = True

        return locals()

    config_type = property(**config_type())

    def size():
        def fget(self):
            return len(self._value)

        return locals()

    size = property(**size())

    def max_size():
        def fget(self):
            return self._max_size

        def fset(self, new_size):
            new_size = int(new_size)
            if new_size < 1:
                raise ValueError('max_size must be greater than 0')
            
            if new_size < self.size:
                self._value = self._value[:new_size]

            self._max_size = new_size
            self._dirty = True

        return locals()

    max_size = property(**max_size())

    def list_response():
        doc = """Return a formatted configuration list response message"""

        def fget(self):
            if self._max_size > 1:
                count = '[%d]' % self._max_size
            else:
                count = ''
    
            return '%s=%s%s\n' % (self._config_type, self._name, count)
            
        return locals()
        
    list_response = property(**list_response())

    def current_response():
        doc = """Return a formatted current configuration response message"""
        
        def fget(self):
            if self._value is None or len(self._value) == 0:
                return '%s=\n' % self._name
            elif isinstance(self._value, StringType):
                return '%s=%s\n' % (self._name, self._value)
            else:
                response = ''
            
                for v in self._value:
                    response += '%s=%s\n' % (self._name, v) 
    
                return response
            
        return locals()
        
    current_response = property(**current_response())

    def __str__(self):
        return self.current_response
    
    def clear(self):
        del self._value
        self._value = []

    def dirty():
        def fget(self):
            return self._dirty

        return locals()

    dirty = property(**dirty())

    def append(self, value):
        if self._max_size > self.size:
            self._value.append(value)
            self._dirty = True
        else:
            raise IndexError(("Attempting to append more than 'max_size'"
                              '(%d) items') % self._max_size)


class xPLConfig(object):
    """Container for a set of xPLConfigItems."""
    
    def __init__(self, instance='', new=False):
        self._items = {}
        self._instance = ''
        self._initial_instance = ''
        self.instance = instance
        
        self.new = new

    def __getitem__(self, key):
        return self._items[key]

    def __setitem__(self, key, value):
        if isinstance(value, xPLConfigItem):
            self._items[key] = value
        else:
            if not isinstance(value, list):
                value = [value]

            item = xPLConfigItem(key, value=value)
            self._items[key] = item

    def __len__(self):
        return len(self._items)
    
    def __iter__(self):
        return self._items.__iter__()

    def items(self):
        return self._items.items()

    def keys(self):
        return self._items.keys()

    def values(self):
        return self._items.values()
    
    def has_key(self, key):
        return self._items.has_key(key)

    def get(self, key, default):
        return self._items.get(key, default)

    def initial_instance():
        doc = """The initial_instance id"""
        
        def fget(self):
            return self._initial_instance

        return locals()

    initial_instance = property(**initial_instance())

    def instance():
        doc = """The instance for which we are holding the configuration"""
        
        def fget(self):
            return self._instance

        def fset(self, value):
            if value != '':
                if self._initial_instance == '':
                    self._initial_instance = value

                self._instance = value

        return locals()

    instance = property(**instance())

    def list_response():
        doc = """Return a formatted configuration list response message"""
        
        def fget(self):
            body = 'reconf=newconf\n'
            
            for item in self.values():
                body += '%s' % item.list_response
    
            return body
            
        return locals()
        
    list_response = property(**list_response())

    def current_response():
        doc = """Return a formatted current configuration response message"""
        
        def fget(self):
            body = 'newconf=%s\n' % self.instance
            
            for item in self.values():
                body += '%s' % item.current_response
    
            return body
            
        return locals()
        
    current_response = property(**current_response())

    def dirty():
        doc = """Returns True if anything has changed"""
        
        def fget(self):
            if self._instance != self._initial_instance:
                return True
            
            dirty = False
            for item in self._items.values():
                if item.dirty:
                    dirty = True
                    break
                
            return dirty

        return locals()

    dirty = property(**dirty())

    def append(self, item, value=[], config_type=xPLConfigItem.CONFIG_TYPE_OPTION, max_size=1):
        """Append an xPLConfigItem to this config
        
        If `item` is an xPLConfigItem then it is added directly otherwise it
        is changed to its string representation and used as the name of a
        'config' item with the other values provided.
        """
        
        if isinstance(item, xPLConfigItem):
            if item.name == '':
                raise KeyError('Item has no name. Can only add a xPLConfigItem with a name')
    
            self._items[item.name] = item
        else:
            i = xPLConfigItem(str(item))
            i.config_type = config_type
            i.max_size = max_size
            if value is not None:
                i.value = value
    
            self._items[item] = i
        
        self._dirty = True

    def remove(self, item):
        """Remove an item form this config"""
        
        if isinstance(item, xPLConfigItem):
            if self.has_key(item.name):
                del self._items[item.name]
        else:
            del self._items[item]

        self._dirty = True

    def copy(self, with_id=None):
        """Return a copy of this config"""
        
        c = xPLConfig(self._name)
        for item in self.values():
            i = xPLConfigItem(item)
            c.append(i)
        
        if with_id is not None:
            c.name = with_id
            
        return c

    def set_to(self, msg, add=False):
        """Set our items to the values in ``msg``
        
        :param msg: A list of (name, value) tuples
        :param add: If ``add`` is True and the item ``name`` does not exist
                    then add a new xPLConfigItem.
                    If the current list of config items is empty then ``add``
                    is assumed to be True

        :rtype:     True = A non standard configuration item has changed.
        """
        
        changed = False
        add = add or len(self._items) == 0

        for k, v in msg:
            i = self._items.get(k, None)
            if i is not None:
                i.clear()
                        
        for key, v in msg:
            value_is_list = isinstance(v, list)
            
            if key == 'newconf' and v != self.instance:
                if value_is_list:
                    self.instance = v[0]
                else:
                    self.instance = v
            else:
                i = None
                try:
                    i = self._items[key]
                except KeyError:
                    if add:
                        i = xPLConfigItem(key)
                
                if i is not None:
                    if i.value != v:
                        if value_is_list:
                            i.max_size += len(v)
                            i._value.extend(v)
                        else:
                            i.max_size += 1
                            i._value.extend([v])
                            
                        self._items[key] = i
                        
                        if not self.is_standard_item(key):
                            changed = True

        return changed

    def merge(self, config):
        """Merge `config` into our configuration."""
        
        for item in config.values():
            if item.name in self.keys():
                self._items[item.name].value = item.value
            else:
                print('Item \'%s\' not in `config` - Item not updated' % item.name)

        self.new = config.new
        self.instance = config.instance

    def add_std_items(self):
        """Add any standard xPL message items not already included"""
        
        keys = self.keys()
        
        if 'interval' not in keys:
            item = xPLConfigItem('interval', '5', xPLConfigItem.CONFIG_TYPE_OPTION, 1)
            self._items['interval'] = item
            
        if 'filter' not in keys:
            item = xPLConfigItem('filter', '*.*.*.*.*.*', xPLConfigItem.CONFIG_TYPE_OPTION, max_size=16)
            self._items['filter'] = item
        
        if 'group' not in keys:
            item = xPLConfigItem('group', '', config_type=xPLConfigItem.CONFIG_TYPE_OPTION, max_size=16)
            self._items['group'] = item

    def is_standard_item(self, item):
        """Return True if the specified item is a standard one."""
        
        return item in ['interval', 'filter', 'group']

    def is_complete(self):
        """Return True if all configuration items have a required value
        
        'config' & 'reconf' items require a value, 'option' values do not
        """ 
        
        for item in self.values():
            if (item.config_type == xPLConfigItem.CONFIG_TYPE_CONFIG or item.config_type == xPLConfigItem.CONFIG_TYPE_RECONF) and item.size == 0:
                return False

        return True


#TODO: Check that we can handle multiple lines with the same name
class xPLConfigFile(object):
    """An xPL config file.
    
    A standard INI file readable by ConfigObj instances with a section
    for each xPLLooper configuration.
    """
    
    def __init__(self):
        self._filename = ''
        self._default = None
        self._configs = {}
    
    def __len__(self):
        return len(self._configs)
    
    def __getitem__(self, key):
        return self._configs[key]
    
    def __setitem__(self, key, value):
        self._configs[key] = value
    
    def __delitem__(self, key):
        del self._configs[key]
    
    def __iter__(self):
        return self._configs.__iter__()

    def configs():
        doc = """Access to the list of configurations."""
        
        def fget(self):
            return self._configs
            
        return locals()
        
    configs = property(**configs())

    def read(self, filename):
        """Read a config file."""
        
        self._filename = filename

        try:
            i = ConfigObj(self._filename)

            for section_name in i.sections:
                config = xPLConfig(section_name)
                
                section = i[section_name]
                for name in section.scalars:
                    if name != 'newconf':
                        value = section[name]
                        
                        item = xPLConfigItem(name, value)
                        config.append(item)

                self._configs[section_name] = config
        except Exception, exc:
            raise xPLConfigError('Unable to read %s: %s' % (self._filename, exc.message))
    
    def write(self, config, filename=None):
        """Save `config` back to it's file by reading the current state,
        updating the values and re-saving.
        
        We need to read the current state as another looper may have updated
        their configuration section.
        """ 
        
        if filename is None:
            filename = self._filename
            
        if filename == '':
            raise StandardError('You must supply a filename as configuration not previously loaded from a configuration file.') 

        i = ConfigObj(filename)
        i.list_values = True
        i.write_empty_values = True

        if config.initial_instance in i.sections and config.initial_instance != config.instance:
            i.rename(config.initial_instance, config.instance)
        else:            
            i[config.instance] = {}

        for item in config.values():
            value = item.value
            if isinstance(value, list):
                if len(value) == 0:
                    value = ''
                elif len(value) == 1:
                    value = value[0]
            else:
                value = str(value)
            
            # We don't need to write our instance as it is stored in the
            # section name.    
            if item.name != 'newconf':
                i[config.instance][item.name] = value

        with open(filename, 'w') as fp:
            i.write(fp)
        
        config._initial_instance = config._instance

    def parse_item(self, name, value):
        """Parse a name and value into a xPLConfigItem."""

        size = 1
        i = name.find('[')
        
        if i != -1 and name[-1] == ']':
            size = int(name[i+1:-1], 10)    
            name = name[:i]

        if len(value) > 2 and value[0] == '[' and value[-1] == ']':
            value = value.strip('[]')
    
        value = [x.strip().strip("'\"") for x in value.split(',')]

        return xPLConfigItem(name, value, xPLConfigItem.CONFIG_TYPE_CONFIG, size)
