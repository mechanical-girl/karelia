# karelia
Karelia is a library written in Python for connecting bots to euphoria.io.

The Karelia library is a super-barebones library for connecting Python bots to euphoria. It is designed to handle opening and maintaining a connection and keeping compliance with the Euphorian bot standards, while allowing a user as much freedom as possible.

It requires websocket-client.

The connectTo() function takes the name of the room and the name of the bot, and returns the websocket connection.
The parse() function handles maintaining the connection and upholding the standards. It must be called on every new message. It will return a json object containing the message, or False if an error was encountered.
The send() function sends a message with the optional parameter of the parent comment.
