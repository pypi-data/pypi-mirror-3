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

__all__ = ['xPLFilter', 'xPLFilterList']

class xPLFilter(object):
    """Defines an filter for xPL messages.

    A filter filters on the following message components :-
        - Message Type (cmnd, stat and trig)
        - Vendor Name
        - Device Name
        - Instance Name
        - Message Class
        - Message Type"""

    def __init__(self, filter_):
        """Create a filter from a string.

        The string should be of the form

            Type.Vendor.Device.Instance.Class.Type"""

        items = filter_.split('.')

        if len(items) != 6:
            raise ValueError('Invalid filter %s. Expecting 6 elements got %d' % (filter_, len(items)))

        self.msgtype = items[0].lower()
        self.vendor = items[1].lower()
        self.device = items[2].lower()
        self.instance = items[3].lower()
        self.class_ = items[4].lower()
        self.type_ = items[5].lower()

    def __repr__(self):
        return '%s.%s.%s.%s.%s.%s' % (self.msgtype, self.vendor, self.device, self.instance,
        self.class_, self.type_)

    def source_match(self, msg):
        """Return True if a message source matches the filter."""

        return (self.msgtype == '*' or self.msgtype == msg.message_type) and \
            (self.vendor == '*' or self.vendor == msg.source_vendor) and \
            (self.device == '*' or self.device == msg.source_device) and \
            (self.instance == '*' or self.instance == msg.source_instance) and \
            (self.class_ == '*' or self.class_ == msg.schema_class) and \
            (self.type_ == '*' or self.type_ == msg.schema_type)

    def target_match(self, msg):
        """Return True if a message target matches the filter."""

        return (self.msgtype == '*' or self.msgtype == msg.message_type) and \
            (msg.target_is_all or \
            ((self.vendor == '*' or self.vendor == msg.target_vendor) and \
            (self.device == '*' or self.device == msg.target_device) and \
            (self.instance == '*' or self.instance == msg.target_instance))) and \
            (self.class_ == '*' or self.class_ == msg.schema_class) and \
            (self.type_ == '*' or self.type_ == msg.schema_type)


class xPLFilterList(object):
    def __init__(self):
        self._filters = []

    def __iadd__(self, filter_):
        return self.add_filter(filter_)

    def __isub__(self, filter_):
        return self.remove_filter(filter_)

    def __len__(self):
        return len(self._filters)

    def add_filter(self, filter_):
        if isinstance(filter_, xPLFilter):
            self._filters.append(filter_)
        else:
            self._filters.append(xPLFilter(filter_))
            
        return self

    def remove_filter(self, filter_):
        if filter_ in self._filters:
            self._filters.remove(filter_)
            return self

    def source_match(self, msg):
        if len(self._filters) == 0:
            return True

        for filter_ in self._filters:
            if filter_.source_match(msg):
                return True

        return False

    def target_match(self, msg):
        if len(self._filters) == 0:
            return True

        for filter_ in self._filters:
            if filter_.target_match(msg):
                return True

        return False

