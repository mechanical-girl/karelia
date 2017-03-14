#!/usr/local/bin/python

#############################################################
#   Karelia library, by PouncySilverkitten                  #
#   github.com/PouncySilverkitten/karelia                   #
#                                                           #
#############################################################

import websocket
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

def changeNick(nick=botName):
    conn.send(json.dumps({"type": "nick","data": {"name":nick}}))
    botName = nick

def getUptime():
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

    uptime = startDate + " (" + str(updays) + " days " + str(uphours) + " hours " + str(upminutes) + " minutes)"
    return uptime

def send(message,parent='',packet=False):
    if not paused:
        if packet != False and len(message) > 0:
            message = message.replace('***sender**','@' + packet['data']['sender']['name'].replace(' ',''))
        conn.send(json.dumps({'type': 'send', 'data': {'content': message, 'parent': parent}}))
    
def connectTo(roomName):
    global conn, room
    room = roomName
    conn = create_connection("wss://euphoria.io/room/"+roomName+"/ws")
    conn.send(json.dumps({"type": "nick","data": {"name":botName}}))
    return(conn)

def disconnect(conn):
    try:
        conn.close()
    finally:
        return()

def parse(packet = False, name=False):
    global paused
    global lastMessage
    if name == False:
        name = botName

    try:
        incoming = conn.recv()
        
        if lastMessage != incoming:
            lastMessage = incoming

            packet = json.loads(incoming)

            if packet["type"] == "ping-event":
                conn.send(json.dumps({'type': 'ping-reply', 'data': {'time': packet['data']['time']}}))

            elif packet['type'] == "send-event":
                
                if packet['data']['content'] == '!ping':
                    send('Pong!', packet['data']['id'])
                if packet['data']['content'] == '!ping @{0}'.format(name):
                    send('Pong!',packet['data']['id']) 
         
                if packet['data']['content'] == '!uptime @{0}'.format(name):
                    uptime = getUptime()
                    send('/me has been up since ' + uptime,packet['data']['id'])

                if packet['data']['content'] == '!pause @{0}'.format(name):
                    send('/me has been paused',packet['data']['id'])
                    paused = True
                if packet['data']['content'] == '!unpause @{0}'.format(name):
                    paused = False
                    send('/me has been unpaused',packet['data']['id'])
                    
                if packet['data']['content'] == '!help @{0}'.format(name):
                    for message in helpMessage:
                        sending = message.replace('**sender**','@' + packet['data']['sender']['name'].replace(' ',''))
                        send(sending,packet['data']['id'])
                if packet['data']['content'] == '!help':
                    send(shortHelp,packet['data']['id'])

                if packet['data']['content'] == '!kill @{0}'.format(name):
                    send("Bot killed; will now exit.",packet['data']['id'])
                    return(sys.exit())

                if packet['data']['content'] == "!antighost":
                    changeNick(botName)

            return(packet)
        
    except Exception as e:
        raise KareliaException({'message':'There was an error parsing the message','error':e})

def spoof(packet,spoofBot):
    try: parse(packet,spoofBot)      
    except Exception as e:
        print("Spoofing error from karelia.py: " + str(e))
        return({"type": "error",'error':str(e)})

def log(e, message = ''):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    exception = "Exception on message: {}\n{}: {}\n  {}\n  {}\n  {} at line {}\n\n".format(message['data'], type(e), e, exc_type, exc_obj, fname, exc_tb.tb_lineno)
    with open("{} &{}.log".format(botName, room), 'a') as f:
        f.write(exception)
    print(exception)
