karelia
======
Karelia is a library of functions for connecting a bot to the Heim chat
platform at euphoria.io

Syntax
======
bot:
    
------

bot represents a single bot for euphoria.io

To create a bot which only responds to a single nick, call `karelia.bot(nick, room)`
which will return a bot object.
Alternatively, to have a bot respond to multiple names, call
`karelia.bot([list, of, nicks], room)` which will present as
the first nick in the list, but respond to stock commands send to all nicks.

If specific action is required when the bot receives the `!kill` command, a function can be written by the user and assigned to `bot.on_kill`.

### \_\_init\_\_
`__init__(self, name, room)`: 
Inits the bot object

### connect
`connect(self, stealth=False)`: 
Connects to specified room and sets nick.

`bot.connect()` will connect to the room and then cause the bot to appear on the nicklist.
`bot.connect(stealth=True)` will connect to the room, but not set the nick for the bot.

### change\_nick
`change_nick(self, nick='')`: 
`change_nick` sends the `nick` command to Heim servers.

If the bot only has a single nick:
- `bot.change_nick()` will cause the bot to set its nick to the previously specified value
- `bot.change_nick("nick")` will cause the bot to set its nick to `nick` *and* store `nick` for future reference.

If the bot has multiple nicks specified:
- `bot.changenick()` will cause the bot to set its nick to the first nick in its list
- `bot.changenick("nick")` will cause the bot to set its nick to `nick` *and* store `nick` as the first value in its list

### get\_uptime
`get_uptime(self)`: 
Called by the `!uptime` command. Returns time since connect as string.

### send
`send(self, message, parent='')`: 
Unless the bot is paused, sends the supplied message. The parent message can be specified: `send(message, parent = parent_id)`.

If the `message` argument has type `dict`, it will be sent as a packet. Otherwise, it will be treated as the body of a message.

With format `send(message, parent):`
- `message`: either a complete packet, or the a message in string form.
- `parent`: the id of the message being replied to. If not specified,
karelia will send the message as a new parent i.e. bottom-level message.

`bot.send('Top-level message')` will send that as a top-level message.

`bot.send('It's a reply!','02aa8y85m7hts')` will send that message as
a reply to the message with id `02aa8y85m7hts`.

`bot.send({'type': 'log', 'data': {'n':1000}})` will send a log
request for the thousand most recent messages posted to the room.

### reply
`reply(self, message)`: 
Wrapper around `bot.send()`

Sends the only argument as a reply to the most recently `parse()`d message.

### disconnect
`disconnect(self)`: 
Attempts to close the connection at `self.conn`. If unsuccessful, it will log and raise an Exception.

### parse
`parse(self)`: 
`parse()` handles the commands specified in the Botrulez
(github.com/jedevc/botrulez) and those required to stay alive.

`parse()` is a blocking function - that is, it will always wait until it
receives a packet from heim before returning.

On receiving a packet, it will reply to pings (both global and specific),
offer uptime, pause and unpause the bot, respond to help requests (again,
both global and specific) and antighost commands, and kills the bot.

For all commands with a name attached, it will reply if any of the names
stored in `self.names` match.

The responses to all botrulez-mandated commands (with the exception of
uptime, as The Powers That Be disapprove of dissident response formats
to it) can be altered with the `bot.stock_responses` dict. The following
values are available:

| key           | default value             |
|---------------|---------------------------|
| 'ping'        | 'Pong!'                   |
| 'short_help'  | (no response)             |
| 'long_help'   | (no response)             |
| 'paused'      | '/me has been paused'     |
| 'unpaused'    | '/me has been unpaused'   |
| 'killed'      | '/me has been killed'     |

Regardless of actions taken, it will return the unaltered packet. If an
error occurs, it will return an exception.

Note: as of 2017-03-16 if killed, it will disconnect automatically
and return the string 'Killed'.
Note: as of 2018-06-22 if killed, it will log the killer, run `bot.on_kill()`, and then exit.

### normalise\_nick
`normalise_nick(self, nick)`: 
Return the known-standard form (i.e., lowercase with no whitespace) of the supplied nick.

### log
`log(self, **kwargs)`: 
logs as much information as possible to an external file.

Optionally, specify `log(event = "Event to Log", logfile = "bot_logs.log")`.
Otherwise,  logs will be written to a file with the following format: `botname_room.log`

