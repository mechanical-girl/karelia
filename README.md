#karelia.py

##About
karelia.py is a simple library for connecting Python bots to `euphoria.io`. It consists entirely of functions which handle all of the websocket- and json-related tasks required to stay connected. The rest, dear coder, is up to you.

##Dependencies
karelia.py requires **Python 3** and the *websocket-client* library. It also calls json, time, and sys.

##Use
At present, karelia.py is composed entirely of functions. For real-world reference, see template.py.

###Set Variables
There are several variables which should be set. These are
- karelia.botName (String. The name which the bot will give the Heim server.)
- karelia.shortHelp (String. The response to the `!help` command.)
- karelia.helpMessage (List of strings. Each string will be sent as a separate message in response to the `!help @botName` command.)

###karelia.connectTo(roomName)
This function will connect to the websocket of the room specified in string format. It will return a websocket connection object.

`connection = karelia.connectTo('xkcd')`


###karelia.parse()
Accepting no arguments, the parse() function instead waits until a new message arrives from the websocket connection. It then handles said message thus:

1. Convert to a dict.
2. If it is a ping, respond.
   If it is a bang command with a response specified in the Euphorian Bot Standards or '!antighost', respond.
4. Return the dict object.

If the parse() function encounters an error, it will return a dict with content dict['type'] == "error" and dict['error'] == the exception thrown.


###karelia.spoof(packet,spoofBot)
The spoof() function attempts to obey any bang commands (as specified in the Bot Standards) in the dict passed as the first argument, assuming it is named spoofBot.
This is equivalent to a circumstance where botName = spoofBot and the parse() command receives the packet.


###karelia.changeNick(nick)
This function simply changes the bot's nick. It does not check the validity of the Heim response. This should be done by the user (see api.euphoria.io).
