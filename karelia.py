#!/usr/local/bin/python

"""
Karelia is a library of functions for connecting a bot to the Heim chat
platform at euphoria.io
"""

from websocket import create_connection
import traceback
import json
import time
import sys
import os
import re


class KareliaException(Exception):
    """Generic exception"""
    pass


class newBot():
    """newBot represents a single bot for euphoria.io

    A single bot is the simplest object which Karelia supports. Simply speaking,
    a bot object is a collection of functions which, when used correctly, are
    capable of maintaining and utilising a two-way connection between itself and
    the Heim servers at euphoria.io.

    To create a bot, call `karelia.newBot(['list', 'of', 'nicks'], ['rooms'])`
    which will return a bot object.

    A bot object has the following functions:
    - `connect` connects to the room specified on creation
    """

    def __init__(self, name, room):
        """Inits the bot object"""
        if type(name) == "<class 'list'>": self.names = name
        else: self.names = [name]
        self.stockResponses = {'ping': 'Pong!',
                      'shortHelp': '',
                      'longHelp': [],
                      'paused': '/me has been paused',
                      'unpaused': '/me has been unpaused',
                      'killed': '/me has been killed'}
        self.room = room
        self.paused = False
        self.lastMessage = ''
        self.connectTime = time.gmtime()
        self.non_bmp_map = dict.fromkeys(
            range(0x10000, sys.maxunicode + 1), 0xfffd)

    def connect(self, stealth=False):
        """Connects to specified room and sets nick."""
        self.conn = create_connection(
            "wss://euphoria.io/room/{}/ws".format(self.room))
        if not stealth:
            self.changeNick()

    def changeNick(self, nick=''):
        """
        changeNick sends the `nick` command to Heim servers.

        If a nick is passed in as an argument, it will change to that and change
        the `botName` variable to the value passed as an argument (for resilience
        against `!antighost`, amongst other reasons). If no nick is specified, it
        will assume that the `botName` variable is the desired nick.
        """
        if nick == '':
            nick = self.names[0]
        self.conn.send(json.dumps(
            {"type": "nick", "data": {"name": nick}}))

    def getUptime(self):
        """Called by the `!uptime` command. Returns time since connect as string."""
        self.updays = 0
        self.uphours = 0
        self.upminutes = 0
        self.upseconds = 0

        self.upticks = time.time() - time.mktime(self.connectTime)
        while self.upticks > 86400:
            self.updays += 1
            self.upticks -= 86400
        while self.upticks > 3600:
            self.uphours += 1
            self.upticks -= 3600
        while self.upticks > 60:
            self.upminutes += 1
            self.upticks -= 60

        self.uptime = "/me has been up since {} UTC ({} days, {} hours, {} minutes)".format(
            time.strftime("%a, %d %b %Y %H:%M:%S (%Z)", self.connectTime),
            self.updays,
            self.uphours,
            self.upminutes,
            self.upseconds
        )
        return(self.uptime)

    def send(self, message, parent='', packet=False):
        """
        Sends the supplied message. The parent message can be specified.

        Arguments are: the message to be sent, the id of the parent message, the
        packet being replied to, and whether or not message is a complete packet.

        - message:  either a complete packet, or the `['data']['content']` field
        of one. If the former, the packet argument must be set to true.
        - parent:   the id of the message being replied to. If not specified,
        karelia will send the message as a new parent i.e. bottom-level message.
        - packet:   if set to `True`, the first argument will be treated as a
        complete packet.

        `karelia.send('Top-level message')` will send that as a top-level message.

        `karelia.send('It's a reply!','02aa8y85m7hts')` will send that message as
        a reply to the message with id `02aa8y85m7hts`.

        `karelia.send({'type': 'log', 'data': {'n':1000}}, True)` will send a log
        request for the thousand most recent messages posted to the room.
        """
        if not self.paused:
            if packet == True and len(message) > 0:
                self.conn.send(message)
            else:
                self.conn.send(json.dumps({'type': 'send',
                                           'data': {'content': message,
                                                    'parent': parent}}))

    def disconnect(self):
        """Attempts to close the connection at self.conn."""
        try:
            self.conn.close()
        except Exception as e:
            self.log(e)

    def parse(self):
        """
        parse() handles the commands specified in the Botrulez
        (github.com/jedevc/botrulez) and those required to stay alive.

        parse() is a blocking function - that is, it will always wait until it
        receives a packet from heim before returning.

        On receiving a packet, it will reply to pings (both global and specific),
        offer uptime, pause and unpause the bot, respond to help requests (again,
        both global and specific) and antighost commands, and kills the bot.

        For all commands with a name attached, it will reply if any of the names
        stored in self.names match.
        
        The responses to all botrulez-mandated commands (with the exception of
        uptime, as The Powers That Be disapprove of dissident response formats
        to it) can be altered with the bot.stockResponses dict. The following
        values are available:
        
        | key           | default value             |
        | 'ping'        | 'Pong!'                   |
        | 'shortHelp'   | <empty>                   |
        | 'longHelp'    | <empty> (must be a list)  |
        | 'pause'       | '/me has been paused'     |
        | 'unpause'     | '/me has been unpaused'   |
        | 'kill'        | '/me has been killed'     |

        Regardless of actions taken, it will return the unaltered packet. If an
        error occurs, it will return an exception.

        Note: as of 2017-03-16 if killed, it will return sys.exit().
        """

        try:
            incoming = self.conn.recv()

            if self.lastMessage != incoming:
                packet = json.loads(incoming)
                self.packet = packet

                if packet["type"] == "ping-event":
                    self.conn.send(json.dumps({'type': 'ping-reply',
                                               'data': {
                                                   'time': packet['data']['time']}}))

                elif packet['type'] == "send-event":

                    if packet['data']['content'] == '!ping':
                        self.send(self.stockResponses['ping'], packet['data']['id'])
                    elif packet['data']['content'] == '!help':
                        self.send(self.stockResponses['shortHelp'], packet['data']['id'])
                    elif packet['data']['content'] == "!antighost":
                        self.changeNick(self.names[0])

                    for name in self.names:
                        if packet['data']['content'] == '!ping @{0}'.format(name):
                            self.send(self.stockResponses['ping'], packet['data']['id'])
                        if packet['data']['content'] == '!uptime @{0}'.format(name):
                            self.send(self.getUptime(), packet['data']['id'])
                        if packet['data']['content'] == '!pause @{0}'.format(name):
                            self.send(self.stockResponses['pause'],
                                      packet['data']['id'])
                            self.paused = True
                            self.log('{} PauseEvent from {}'.format(time.strftime(
                                "%a, %d %b %Y %H:%M:%S (%Z)", time.time()),
                                packet['data']['sender']['name']))
                        if packet['data']['content'] == '!unpause @{0}'.format(name):
                            self.log('{} UnpauseEvent from {}'.format(time.strftime(
                                "%Y-%M-%D %H:%M:%S (%Z)", time.time()),
                                packet['data']['sender']['name']))
                            self.paused = False
                            self.send(self.stockResponses['unpause'],
                                      packet['data']['id'])
                        if packet['data']['content'] == '!help @{0}'.format(name):
                            for message in self.stockResponses['longHelp']:
                                sending = message.format(self.normaliseNick(
                                    packet['data']['sender']['name']))
                                self.send(sending, packet['data']['id'])
                        if packet['data']['content'] == '!kill @{0}'.format(name):
                            self.send(self.stockResponses['kill'],
                                      packet['data']['id'])
                            return(sys.exit())

                self.packet = packet
                return(packet)

        except Exception as e:
            raise KareliaException(
                {'message': 'There was an error parsing the message', 'error': e})

    def normaliseNick(self, nick):
        """Return the known-standard form of the supplied nick."""
        return(re.sub(r'\s+', '', nick.translate(self.non_bmp_map)).lower())

    def log(self, e=False):
        """
        logs as much information as possible to an external file.

        log should be passed an exception object and if possible the message being
        processed at the time of the exception. It will then write out as much as
        it can about the exception to a logfile.
        """
        if e == False:
            tbText = traceback.format_exc()
            message = "{}\n{} - Exception on message: {}:\n{} \n\n".format("-" * 20, time.strftime(
                "%Y-%m-%d %H:%M:%S", time.gmtime()), self.packet['data'], tbText)
        else:
            message = "{}\n{}: {}\n\n".format("-" * 20, time.strftime(
                "%Y-%m-%d %H:%M:%S", time.gmtime()), e)
        with open("{} &{}.log".format(self.names[0], self.room), 'a') as f:
            f.write(message)
        print(message)
