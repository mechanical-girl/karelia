#!/usr/local/bin/python

"""
Karelia is a library of functions for connecting a bot to the Heim chat
platform at euphoria.io
"""

from websocket import create_connection
import websocket
import traceback
import random
import json
import time
import sys
import os
import re

class KareliaException(Exception):
    """Generic exception"""
    pass

class Sender:
    def __init__(self, name, sid, serv_id, serv_era, sess_id):
        self.name = name
        self.id = sid
        self.server_id = serv_id
        self.server_era = serv_era
        self.session_id = sess_id

class DataStruct:
    def __init__(self, mid, time, content, sid, name, serv_id, serv_era, sess_id):
        self.id = mid
        self.time = time
        self.content = content
        self.sender = Sender(name, sid, serv_id, serv_era, sess_id)

class Message:
    def __init__(self, packet):
        self.type = packet['type']
        data = packet['data']
        self.data = DataStruct(data['id'], data['time'], data['content'], data['sender']['id'], data['sender']['id'], data['sender']['server_id'], data['sender']['server_id'], data['sender']['session_id'])

class newBot:
    """newBot represents a single bot for euphoria.io

    A single bot is the simplest object which Karelia supports. Simply speaking,
    a bot object is a collection of functions which, when used correctly, are
    capable of maintaining and utilising a two-way connection between itself and
    the Heim servers at euphoria.io.

    To create a bot which only responds to a single nick, call `karelia.newBot(nick, room)`
    which will return a bot object.
    Alternatively, to have a bot respond to multiple names, call
    `karelia.newBot([list, of, nicks], room)` which will present as
    the first nick in the list, but respond to stock commands send to all nicks.
    """

    def __init__(self, name, room):
        """Inits the bot object"""
        if type(name) == "<class 'list'>":
            self.names = name
        else:
            self.names = [name]
        self.stockResponses = {'ping': 'Pong!',
                               'shortHelp': '',
                               'longHelp': [''],
                               'paused': '/me has been paused',
                               'unpaused': '/me has been unpaused',
                               'killed': '/me has been killed'}
        self.room = room
        self.paused = False
        self.lastMessage = ''
        self.connectTime = time.gmtime()
        websocket.enableTrace(False)
        self.non_bmp_map = dict.fromkeys(
            range(0x10000, sys.maxunicode + 1), 0xfffd)

    def connect(self, stealth=False):
        """Connects to specified room and sets nick."""
        self.conn = create_connection(
            "wss://euphoria.io/room/{}/ws".format(self.room))
        if not stealth:
            self.changeNick()
        self.stealth = stealth
        self.parse()
        self.parse()

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
        else:
            self.names[0] = nick
        self.send({"type": "nick", "data": {"name": nick}})

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
            time.strftime("%a, %d %b %Y %H:%M:%S", self.connectTime),
            self.updays,
            self.uphours,
            self.upminutes,
            self.upseconds
        )
        return(self.uptime)

    def send(self, message, parent=''):
        """
        Sends the supplied message. The parent message can be specified.

        Arguments are: the message to be sent, the id of the parent message, the
        packet being replied to, and whether or not message is a complete packet.

        - message:  either a complete packet, or the `['data']['content']` field
        of one.
        - parent:   the id of the message being replied to. If not specified,
        karelia will send the message as a new parent i.e. bottom-level message.

        `karelia.send('Top-level message')` will send that as a top-level message.

        `karelia.send('It's a reply!','02aa8y85m7hts')` will send that message as
        a reply to the message with id `02aa8y85m7hts`.

        `karelia.send({'type': 'log', 'data': {'n':1000}})` will send a log
        request for the thousand most recent messages posted to the room.
        """
        if not self.paused:
            if type(message) is dict:
                self.conn.send(json.dumps(message))
            elif len(message) > 0:
                self.conn.send(json.dumps({'type': 'send',
                                           'data': {'content': message,
                                                    'parent': parent}}))

    def disconnect(self):
        """Attempts to close the connection at self.conn."""
        try:
            self.conn.close()
        except Exception as e:
            self.log()

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
        |---------------|---------------------------|
        | 'ping'        | 'Pong!'                   |
        | 'shortHelp'   | (no response)             |
        | 'longHelp'    | (no response)             |
        | 'paused'      | '/me has been paused'     |
        | 'unpaused'    | '/me has been unpaused'   |
        | 'killed'      | '/me has been killed'     |

        Regardless of actions taken, it will return the unaltered packet. If an
        error occurs, it will return an exception.

        Note: as of 2017-03-16 if killed, it will disconnect automatically
        and return the string 'Killed'.
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

                elif packet['type'] == "send-event" and len(packet['data']['content'] > 0 and packet['data']['content'][0] == '!':

                    if packet['data']['content'] == '!ping':
                        self.send(self.stockResponses['ping'], packet['data']['id'])
                    elif packet['data']['content'] == '!help':
                        self.send(self.stockResponses['shortHelp'], packet['data']['id'])
                    elif packet['data']['content'] == "!antighost" and not self.stealth:
                        self.changeNick(self.names[0])

                    command = packet['data']['content'].split()[0]
                    try:
                        commandName = self.normaliseNick(packet['data']['content'].split()[1][1:])
                    except IndexError:
                        commandName = ''
                    if commandName in [self.normaliseNick(name) for name in self.names]:
                        if command == '!ping':
                            self.send(self.stockResponses['ping'], packet['data']['id'])
                        if command == '!uptime':
                            self.send(self.getUptime(), packet['data']['id'])
                        if command == '!pause':
                            self.send(self.stockResponses['paused'], packet['data']['id'])
                            self.paused = True
                            self.log('{} PauseEvent from {}'.format(time.strftime(
                                "%a, %d %b %Y %H:%M:%S (%Z)", time.time()),
                                packet['data']['sender']['name']))
                        if command == '!unpause':
                            self.log('{} UnpauseEvent from {}'.format(time.strftime(
                                "%Y-%M-%D %H:%M:%S (%Z)", time.time()),
                                packet['data']['sender']['name']))
                            self.paused = False
                            self.send(self.stockResponses['unpaused'],
                                      packet['data']['id'])
                        if command == '!help':
                            if type(self.stockResponses['longHelp']) != "<class 'list'>":
                                self.stockResponses['longHelp'] = [
                                    self.stockResponses['longHelp']]
                            for message in self.stockResponses['longHelp']:
                                sending = message.format(self.normaliseNick(
                                    packet['data']['sender']['name']))
                                self.send(sending, packet['data']['id'])
                        if command == '!kill':
                            self.send(self.stockResponses['killed'],
                                      packet['data']['id'])
                            self.disconnect()
                            return('Killed')

                self.packet = packet
                return(packet)

        except Exception as e:
            raise KareliaException(
                {'message': 'There was an error parsing the message', 'error': e})

    def normaliseNick(self, nick):
        """Return the known-standard form i(i.e., lowercase with no whitespace) of the supplied nick."""
        return(re.sub(r'\s+', '', nick.translate(self.non_bmp_map)).lower())

    def log(self, **kwargs):
        """
        logs as much information as possible to an external file.
        """
        currTime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        delimit = "-" * 20
        if not hasattr(self, 'packet'):
            self.packet = {}
        
        tbText = traceback.format_exc()
        logText = "{}\n{} - {}: {}:\n{}\n\n".format(delimit, currTime,
                                                    "Exception on message",
                                                    self.packet,
                                                    tbText)

        with open("{} &{}.log".format(self.names[0], self.room), 'a') as f:
            f.write(logText)


class Botling:
    def __init__(self):
        pass

    def parse_botbot_command(self, command):
        escape = '\\'
        delim = ';'
    
        ret = []
        current = []
    
        itr = iter(command)
        for ch in itr:
            if ch == escape:
                try:
                    # skip the next character; it has been escaped!
                    current.append(next(itr))
                except:
                    pass
            elif ch == delim:
                # split! (add current to the list and reset it)
                ret.append(''.join(current))
                current = []
            else:
                current.append(ch)
        ret.append(''.join(current))
        return ret
    
    def construct(self):
        self.bot = self.newBot(self.nick, self.room)
        self.raw_commands = self.parse_botbot_command(self.regex)
        self.commands = {}
        for command in self.raw_commands:
            trigger, response = command.split('->', 1)
            self.commands[trigger] = response

    def connect(self):
        self.bot.connect()

    def disconnect(self):
        self.bot.disconnect()

    def choose_random_options(self, options):
        # Recursively check for random options and pick one
        if type(options) == 'list':
            return options[random.randint(0, len(options)-1)]
        if '[' in options and ']' in options:
            left, options = options.split('[',1)
            options, right = options.split(']',-1)
            return "{}{}{}".format(left, self.choose_random_options(options), right)

    def compile_reply(self, reply_text):
      return(self.choose_random_options(reply_text)) 

    def check(self, message)
        for trigger in list(self.commands.keys()):
            if re.match(trigger, message['data']['content']):
                self.bot.send(self.compile_reply(self.commands[trigger]), message['data']['id'])
    
    def parse(self):
        message = self.bot.parse()
        if not message['type'] == 'send-event': return
        self.check(message)
