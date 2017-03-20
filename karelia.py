#!/usr/local/bin/python

"""
Karelia is a library of functions for connecting a bot to the Heim chat
platform at euphoria.io                                              
"""

from websocket import create_connection
import json, time, sys, os

botName = ""
startTime = time.time()
startDate = time.strftime("%Y-%m-%d %H:%M:%S")
paused = False
room = ""
lastMessage = ""
conn = None
room = ""

class KareliaException(Exception):
    pass

def changeNick(nick = botName):
    """
    changeNick sends the `nick` command to Heim servers.

    If a nick is passed in as an argument, it will change to that and change
    the `botName` variable to the value passed as an argument (for resilience
    against `!antighost`, amongst other reasons). If no nick is specified, it
    will assume that the `botName` variable is the desired nick.
    """
    conn.send(json.dumps({"type": "nick","data": {"name":nick}}))
    botName = nick

def getUptime():
    """Called by the `!uptime` command. Returns time since connect as string."""
    global startTime
    timeNow = time.time()

    updays = 0
    uphours = 0
    upminutes = 0
    upseconds = 0

    upticks = timeNow - startTime
    while upticks > 86400:
        updays += 1
        upticks -= 86400
    while upticks > 3600:
        uphours += 1
        upticks -= 3600
    while upticks > 60:
        upminutes += 1
        upticks -= 60

    uptime = "{} ({} days {} hours {} minutes)".format(startDate, updays, uphours, upminutes)
    return uptime

def send(message, parent = '', packet = False):
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
    if not paused:
        if packet:
            conn.send(packet)
        elif len(message) > 0:
            conn.send(json.dumps({'type': 'send', 'data': {'content': message,
                                                           'parent': parent}}))
    
def connectTo(roomName):
    """Connects to specified room and sets nick. Returns a connection object."""
    global conn, room
    room = roomName
    conn = create_connection("wss://euphoria.io/room/{}/ws".format(roomName))
    conn.send(json.dumps({"type": "nick","data": {"name":botName}}))
    return(conn)

def disconnect(conn):
    """Attempts to close the connection passed to it."""
    try:
        conn.close()
    finally:
        return()

def parse(packet = False, name = False):
    """
    parse() handles the commands specified in the Botrulez
    (github.com/jedevc/botrulez) and those required to stay alive.

    parse() is a blocking function - that is, it will always wait until it
    receives a packet from heim before returning.

    On receiving a packet, it will reply to pings (both global and specific,
    offer uptime, pause and unpause the bot, respond to help requests (again,
    both global and local) and antighost commands, and kills the bot.

    Regardless of actions taken, it will return the unaltered packet. If an
    error occurs, it will return an exception.

    Note: as of 2017-03-16 if killed, it will return sys.exit().
    """
    global paused
    global lastMessage
    spoof = False
    if name == False: name = botName
    else: spoof = True

    try:
        incoming = conn.recv()
        
        if lastMessage != incoming:
            lastMessage = incoming

            if not packet: packet = json.loads(incoming)

            if packet["type"] == "ping-event" and not spoof:
                conn.send(json.dumps({'type': 'ping-reply', 'data': {
                        'time': packet['data']['time']}}))

            elif packet['type'] == "send-event":
                
                if packet['data']['content'] == '!ping' and not spoof:
                    send('Pong!', packet['data']['id'])
                if packet['data']['content'] == '!ping @{0}'.format(name):
                    send('Pong!',packet['data']['id']) 
         
                if packet['data']['content'] == '!uptime @{0}'.format(name):
                    uptime = getUptime()
                    send('/me has been up since {}'.format(uptime),packet[
                            'data']['id'])

                if packet['data']['content'] == '!pause @{0}'.format(name):
                    send('/me has been paused',packet['data']['id'])
                    paused = True
                if packet['data']['content'] == '!unpause @{0}'.format(name):
                    paused = False
                    send('/me has been unpaused',packet['data']['id'])
                    
                if packet['data']['content'] == '!help @{0}'.format(name):
                    for message in helpMessage:
                        sending = message.replace('**sender**','@{}'.format(
                                packet['data']['sender']['name'].replace(' ',''))
                        send(sending,packet['data']['id'])
                if packet['data']['content'] == '!help' and not spoof:
                    send(shortHelp,packet['data']['id'])

                if packet['data']['content'] == '!kill @{0}'.format(name):
                    send("Bot killed; will now exit.",packet['data']['id'])
                    log("Killed by user.",packet['data'])
                    return(sys.exit())

                if packet['data']['content'] == "!antighost" and not spoof:
                    changeNick()

            return(packet)
        
    except Exception as e:
        raise KareliaException(
            {'message':'There was an error parsing the message','error':e})

def spoof(packet, spoofBot):
    """
    spoof() takes two arguments (packet and spoofBot)

    Calling spoof(packet, spoofBot) causes karelia to respond to the packet
    offered as though it were named spoofBot.
    """
    try: parse(packet, spoofBot)      
    except Exception as e:
        print("Spoofing error from karelia.py: " + str(e))
        return({"type": "error",'error':str(e)})

def log(error = '', message = ''):
    """
    logs as much information as possible to an external file.

    log should be passed an exception object and if possible the message being
    processed at the time of the exception. It will then write out as much as
    it can about the exception to a logfile.
    """
    try:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        exception = """Exception on message: {}
{}: {}
    {}
{}
}} at line {}

""".format(message['data'], type(error), error, exc_type, exc_obj, fname,
           exc_tb.tb_lineno)
                                                  
    except Exception as e:
        print(e)
        exception = """Intelligent logging failed, falling back.
{}
{}

""".format(error, message)
                                                  
    with open("{} &{}.log".format(botName, room), 'a') as f:
        f.write(exception)
    print(exception)
