karelia
======
 Karelia is a library of functions for connecting a bot to the Heim chat platform at euphoria.io 

Syntax
------
### changeNick()

 changeNick sents the nick command to Heim servers.

 If a nick is passed in as an argument, it will change to that and change the botName variable to the value passed as an argument (for resilience amongst !antighost, amongst other reasons. If no nick is specified, it will assume that the botName variable is the desired nick.
 

### getUptime()
Called by the !uptime command. Returns time since bot start as string.

### send()

 Sends the supplied message to the Heim servers. The parent message can be specified.

 Arguments are: the message to be sent, the id of the parent message, the packet being replied to, and whether or not message is a complete packet.

 - message: either a complete packet, or the ['data']['content'] field of one. If the former, the packet argument must be set to true.
 - parent: the id of the message being replied to. If not specified, karelia will send the message as a new parent i.e. bottom-level message
 - packet: if set to True, the first argument will be treated as a completepacket.

 `karelia.send('Top-level message')` will send that as a top-level message.
 
 `karelia.send('It's a reply!','02aa8y85m7hts')` will send that message as a reply to the message with id `02aa8y85m7hts`.

 `karelia.send({'type': 'log', 'data': {'n':1000}})` will send a log request for the thousand most recent messages posted to the room.
 

### connectTo()
Connects to specified room and sets nick. Returns a connection object.

### disconnect()
Attempts to close the connection passed to it.

### parse()

 parse() handles the commands specified in the Botrulez (github.com/jedevc/botrulez) and those required to stay alive.

 parse() is a blocking function - that is, it will always wait until it receives a packet from heim before returning.

 On receiving a packet, it will reply to pings (both global and specific, offer uptime, pause and unpause the bot, respond to help requests (again, both global and local) and antighost commands, and kills the bot.

 Regardless of actions taken, it will return the unaltered packet. If an error occurs, it will return an exception.

 Note: as of 2017-03-16 if killed, it will return sys.exit().
 

### spoof()

 spoof() takes two arguments (packet and spoofBot)

 Calling spoof(packet, spoofBot) causes karelia to respond to the packet offered as though it were named spoofBot.
 

### log()

 logs as much information as possible to an external file.

 log should be passed an exception object and if possible the message being processed at the time of the exception. It will then write out as much as it can about the exception to a logfile.
 

