karelia
======
Karelia is a library of functions for connecting a bot to the Heim chat
platform at euphoria.io

Syntax
======
KareliaException
------

Generic exception

newBot
------

newBot represents a single bot for euphoria.io

A single bot is the simplest object which Karelia supports. Simply speaking,
a bot object is a collection of functions which, when used correctly, are
capable of maintaining and utilising a two-way connection between itself and
the Heim servers at euphoria.io.

To create a bot, call `karelia.newBot(['list', 'of', 'nicks'], ['rooms'])`
which will return a bot object.

### \_\_init\_\_
`\_\_init\_\_(self, name, room)`: 
Inits the bot object

### connect
`connect(self, stealth=False)`: 
Connects to specified room and sets nick.

### changeNick
`changeNick(self, nick='')`: 
changeNick sends the `nick` command to Heim servers.

If a nick is passed in as an argument, it will change to that and change
the `botName` variable to the value passed as an argument (for resilience
against `!antighost`, amongst other reasons). If no nick is specified, it
will assume that the `botName` variable is the desired nick.

### getUptime
`getUptime(self)`: 
Called by the `!uptime` command. Returns time since connect as string.

### send
`send(self, message, parent='')`: 
Sends the supplied message. The parent message can be specified.

Arguments are: the message to be sent, the id of the parent message, the
packet being replied to, and whether or not message is a complete packet.

- message:  either a complete packet, or the `['data']['content']` field
of one. If the former, the packet argument must be set to true.
- parent:   the id of the message being replied to. If not specified,
karelia will send the message as a new parent i.e. bottom-level message.

`karelia.send('Top-level message')` will send that as a top-level message.

`karelia.send('It's a reply!','02aa8y85m7hts')` will send that message as
a reply to the message with id `02aa8y85m7hts`.

`karelia.send({'type': 'log', 'data': {'n':1000}})` will send a log
request for the thousand most recent messages posted to the room.

### disconnect
`disconnect(self)`: 
Attempts to close the connection at self.conn.

### parse
`parse(self)`: 
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
| 'pause'       | '/me has been paused'     |
| 'unpause'     | '/me has been unpaused'   |
| 'kill'        | '/me has been killed'     |

Regardless of actions taken, it will return the unaltered packet. If an
error occurs, it will return an exception.

Note: as of 2017-03-16 if killed, it will return sys.exit().

### normaliseNick
`normaliseNick(self, nick)`: 
Return the known-standard form of the supplied nick.

### log
`log(self, **kwargs)`: 
logs as much information as possible to an external file.

log should be passed an exception object and if possible the message being
processed at the time of the exception. It will then write out as much as
it can about the exception to a logfile.

