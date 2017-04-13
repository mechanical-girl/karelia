karelia
======
Karelia is a library of functions for connecting a bot to the Heim chat
platform at euphoria.io

Syntax
======
KareliaException
------

Generic exception from the library.

newBot
------

This class represents a single bot connected to the Heim servers.

For simple usecases, a single call to newBot will suffice. This will be in
circumstances where only one bot is required, and will only be required to
connect to one room at a time.

For more complex implementations, the botCommand class may be required,
which will negate the need to call newBot manually. For more information,
see the botCommand docs.

### __init__
`__init__(self, name, room, botCommand = False)`: 
Automatically called on creation. Do not set botCommand True.

### connect
`connect(self, stealth=False)`: 
Connects to specified room and sets nick from names[0].

### changeNick
`changeNick(self, nick='')`: 
changeNick sends the `nick` command to Heim servers.

If a nick is passed in as an argument, it will change to that and change
the `botName` variable to the value passed as an argument (for resilience
against `!antighost`, amongst other reasons). If no nick is specified, it
=======
will assume that the string at `name[0]` variable is the desired nick.


### getUptime
`getUptime(self)`: 
Called by the `!uptime` command. Returns time since connect as string.

### send
`send(self, message, parent='')`: 
Sends the supplied message. The parent message can be specified.

Arguments are: the message to be sent, the id of the parent message, the
packet being replied to, and whether or not message is a complete packet.

- message:  either a complete packet, or the `['data']['content']` field

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
`log(self, message, **kwargs)`: 
logs as much information as possible to an external file.

log should be passed an exception object and if possible the message being
processed at the time of the exception. It will then write out as much as
it can about the exception to a logfile.

botCommand
------

The botCommand object takes a list of rooms and a list (or a list of lists)
and creates a bot for each room, then returns itself. The list of bots can
be accessed at botCommand.bots.

If the names parameter is a list, then each bot will be passed that list as
the names it should respond to. If it is a list of lists, then the bot
connecting to `rooms[0]` will receive `names[0]`, the bot connecting to
`rooms[1]` will receive `names[1]` and so on.

The botCommand object can be used for interbot communication. For instance,
if a bot is in several rooms, and is required to communicate between them,
this can be achieved by using the bot's `broadcast()` feature. It is up to
the user to design the structure of data whick will be sent. However, the
following template is provided:

```
broadcastMessage = {  'from': 'testing',
                       'to': 'test;,
                       'type': 'notify',
                       'data': {   'from': 'senderName',
                                   'message': 'message'
                                }
                        }
```

The user can then write code which only reads messages directed to the room
to which it is connected, and can handle them accordingly, based on the
`type` and `data` fields.

A botCommander (the name for a single botCommand object) can also send a
signal to bots using the `broadcast()` function.
=======
Regardless of actions taken, it will return the unaltered packet. If an
error occurs, it will return an exception.

Note: as of 2017-03-16 if killed, it will return sys.exit().

### normaliseNick
`normaliseNick(self, nick)`: 
Return the known-standard form of the supplied nick.

### log
`log()`: 
logs as much information as possible to an external file.

log should be passed an exception object and if possible the message being
processed at the time of the exception. It will then write out as much as
it can about the exception to a logfile.