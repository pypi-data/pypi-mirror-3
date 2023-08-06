'''OpenLCB over CAN

Classes for creating, manipulating, and parsing CAN frames as OpenLCB
messages.

:author: Dustin C. Hatch
:author: Timothy C. Hatch
'''
# Copyright 2012 Dustin C. Hatch, Timothy C. Hatch
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class NodeAlias(object):
    '''Utility class for handling node alias

    * Calling ``int`` on an instance of :py:class:NodeAlias will return
       the integer value.
    * Calling ``str`` on an instance of :py:class:NodeAlias will return
      a hexidecimal number.
    '''

    def __init__(self, alias):
        self._alias = int(alias)

    def __int__(self):
        return self._alias

    def __str__(self):
        return '0x{0:X}'.format(self._alias)

    def __repr__(self):
        return 'NodeAlias(0x{0:X})'.format(self._alias)

class InvalidMessage(Exception):
    '''Raised when attempting to parse an improperly-formatted frame'''

    def __init__(self, frame):
        super(InvalidMessage, self).__init__(
            '{0} is not a valid CAN frame'.format(frame))


class IncorrectMTI(Exception):
    '''Raised when creating a message from a string with the wrong MTI'''

    def __init__(self, mti, cls):
        super(IncorrectMTI, self).__init__(
            '{0:X} is incorrect MTI for {1}'.format(mti, cls.__name__)
        )


class CANMessage(object):
    '''Base class for Controller Area Network messages

    Calling ``str()`` on ``CANMessage`` instances returns a string
    containing the CAN frame.

    .. py:attribute:: header

       The value of the header that would be sent in the frame

    .. py:attribute:: body

       The value of the body that would be sent with the frame
    '''

    def __init__(self, header='', body=''):
        self.header = header
        self.body = body

    def __str__(self):
        return ':X{header}N{body};'.format(
            header=self.header,
            body=self.body,
        )

    @classmethod
    def parse_frame(cls, frame):
        '''Parse a string containing a CAN frame into its parts

        :returns dict: A dictionary containing the valuable message parts

        Subclasses of :py:class:`CANMessage` should override this method
        and provide their own unique logic for parsing the header and
        body into usable properties.
        '''

        try:
            header, body = frame.split('N')
        except ValueError:
            raise InvalidMessage(frame)
        if header.startswith(':X'):
            header = header[2:]
        else:
            raise InvalidMessage(frame)
        body = body.strip()
        if body.endswith(';'):
            body = body[:-1]
        else:
            raise InvalidMessage(frame)

        return {
            'header': header,
            'body': body
        }

    @classmethod
    def from_string(cls, frame):
        '''Create a :py:class:`CANMessage` instance from a frame string

        :param str frame: The complete CAN frame, including
           control characters
        :returns: A new instance of the :py:class:`CANMessage` subclass

        Subclasses of :py:class:`CANMessage` should *not* override this
        method, but rather :py:meth:`parse_frame` instead.
        '''

        parts = cls.parse_frame(frame)

        return cls(**parts)

    @classmethod
    def from_sequence(cls, seq):
        '''Convert a sequence (list, etc.) of strings to Message objects

        :param sequence seq: A sequence of OpenLCB frame strings
        :yields: Instances of the :py:class:`CANMessage` subclass
        '''

        for frame in seq:
            yield cls.from_string(frame)


_registered_messages = {}
class RegisteredMessage(type):
    '''Metaclass for OpenLCB message classes

    Classes using :py:class:`RegisteredMessage` as their metaclass will
    automatically have their MTIs registered, which creates a reverse
    mapping from MTI to class. This registration is required for
    :py:func:`parse_frame` to discover a message class based on the MTI
    and return an instance of it.
    '''

    def __new__(mcs, name, bases, attrs):
        cls = super(RegisteredMessage, mcs).__new__(mcs, name, bases, attrs)

        try:
            mti = attrs['MTI']
        except KeyError:
            return cls

        if 0x1c <= mti <= 0x1f:
            can_data = attrs.get('CAN_DATA', None)
            if mti in _registered_messages:
                _registered_messages[mti][can_data] = cls
            else:
                _registered_messages[mti] = {can_data: cls}
        else:
            _registered_messages[mti] = cls

        return cls


def parse_frame(frame):
    '''Parse an OpenLCB Message from a CAN frame

    :param str frame: CAN frame as a string, including control characters
    :returns: An instance of the class registered for the MTI specified
        in the frame
    '''

    try:
        header, body = frame.split('N')
    except (AttributeError, ValueError):
        raise InvalidMessage(frame)

    try:
        header = int(header.strip()[2:], 16)
    except ValueError:
        raise InvalidMessage(frame)

    mti = header >> 12
    can_data = None
    if mti > 0x1e000:
        mti >>= 12
        if body.strip():
            can_data = int(body.strip()[:2], 16)
    try:
        cls = _registered_messages[mti]
    except KeyError:
        cls = type('UnknownMessage', (OpenLCBMessage,), {})
        cls.MTI = mti
        if mti > 0x1e000:
            cls.CAN_DATA = can_data
    else:
        if isinstance(cls, dict):
            cls = cls[can_data]

    return cls.from_string(frame)


class OpenLCBMessage(CANMessage):
    '''Base class for all OpenLCB CAN messages

    :param int src_alias: The alias of the node from which messages
       originate

    .. py:attribute:: src_alias

       The node alias of the node sending the message

    .. py:attribute:: MTI

       The message type indicator, as an integer. This value should be
       set by subclasses of :py:class:`CANMessage`. See
       http://www.openlcb.org/trunk/specs/MtiAllocations.pdf for a list
       of MTI allocations.
    '''

    __metaclass__ = RegisteredMessage

    def __init__(self, **keywords):
        try:
            self.src_alias = NodeAlias(keywords['src_alias'])
        except KeyError:
            self.src_alias = None
        self.body = keywords.get('body', '')

    @property
    def header(self):
        # Shift the Message Type Indicator to the left 12 bits to make
        # room, then append the source alias
        return '{0:X}'.format((self.MTI << 12 | int(self.src_alias)))

    @classmethod
    def parse_frame(cls, frame):
        parts = super(OpenLCBMessage, cls).parse_frame(frame)
        parts['src_alias'] = int(parts['header'], 16) & 0xfff
        parts['mti'] = int(parts['header'], 16) >> 12
        if parts['mti'] > 0x1e000:
            parts['mti'] >>= 12
        return parts

    @classmethod
    def from_string(cls, frame):
        parts = cls.parse_frame(frame)
        if parts['mti'] != cls.MTI:
            raise IncorrectMTI(parts['mti'], cls)
        else:
            return cls(**parts)


class GlobalMessage(OpenLCBMessage):
    '''Represents a message sent to the entire bus'''


class AddressedMessage(OpenLCBMessage):
    '''Represents a message sent to a single node

    :param int src_alias: The alias of the node from which messages
       originate
    :param int dst_alias: The alias of the node to which the message
       is sent

    .. py:attribute:: src_alias

       The node alias of the node sending the message

    .. py:attribute:: dst_alias

       The alias of the node for which the message is intended
    '''

    def __init__(self, **keywords):
        super(AddressedMessage, self).__init__(**keywords)
        try:
            self.dst_alias = NodeAlias(keywords['dst_alias'])
        except KeyError:
            self.dst_alias = None

    @property
    def header(self):
        header = self.MTI << 12
        header |= int(self.dst_alias)
        header <<= 12
        header |= int(self.src_alias)
        return '{0:X}'.format(header)

    @classmethod
    def parse_frame(cls, frame):
        parts = super(AddressedMessage, cls).parse_frame(frame)
        parts['dst_alias'] = (int(parts['header'], 16) & 0xfff000) >> 12
        return parts


class MessageWithBody(OpenLCBMessage):
    '''Represents a message that contains a body

    .. py:attribute:: node_id

       The full of the ID of the node sending the message
    '''

    def __init__(self, **keywords):
        super(MessageWithBody, self).__init__(**keywords)
        self.node_id = keywords.get('node_id', None)

    @classmethod
    def parse_frame(cls, frame):
        parts = super(MessageWithBody, cls).parse_frame(frame)
        parts['node_id'] = [
            int(parts['body'][i:i+2], 16)
            for i in range(0, 12, 2)
        ]
        return parts


class EventMessage(MessageWithBody):
    '''Represents a message containing an event ID

    .. py:attribute:: event_id

       The ID of the event identified in the message
    '''

    def __init__(self, **keywords):
        super(EventMessage, self).__init__(**keywords)
        self.event_id = keywords.get('event_id', None)

    @classmethod
    def parse_frame(cls, frame):
        parts = super(EventMessage, cls).parse_frame(frame)
        parts['event_id'] = int(parts['body'], 16) & 0xffff
        return parts


class VerifyNodeIDNumberSimple(GlobalMessage):
    MTI = 0x180a7


class VerifiedNodeIDNumber(GlobalMessage, MessageWithBody):
    MTI = 0x180b7


class IdentifyEventsAddressed(AddressedMessage):
    MTI = 0x1e
    CAN_DATA = 0x2b


class IdentifyEventsGlobal(GlobalMessage):
    MTI = 0x182b7


class IdentifyConsumers(GlobalMessage):
    MTI = 0x1824f


class GeneralDatagram(AddressedMessage):
    MTI = 0x1d


class ConsumerIdentified(GlobalMessage, EventMessage):
    MTI = 0x1926b


class DatagramReceived(AddressedMessage):
    MTI = 0x1e

class StartDatagramFrame(AddressedMessage):
    MTI = 0x1c
   
class IdentifyProducers(GlobalMessage):
    MTI = 0x1828f
