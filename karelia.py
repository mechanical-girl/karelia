#!/usr/local/bin/python

#############################################################
#   Karelia library, by PouncySilverkitten                  #
#   github.com/PouncySilverkitten/karelia                   #
#                                                           #
#   Functions                                               #
#   - connectTo(room)                                       #
#   - disconnect(websocketObject)                           #
#   - parse(message)                                        #
#   - changeNick(newNick)                                   #
#   - spoof(message)                                        #
#############################################################

from websocket import create_connection
import json
import time
import sys

botName = ""
startTime = time.time()
startDate = time.strftime("%Y-%m-%d %H:%M:%S")
paused = False
helpMessage = ["This bot has not had a help message specified. This message was generated automatically."]

def changeNick(nick):
    global ws
    ws.send(json.dumps({"type": "nick","data": {"name":nick}}))

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

def send(message,parent=''):
    global paused
    global ws
    if not paused:
        ws.send(json.dumps({'type': 'send', 'data': {'content': message, 'parent': parent}}))
    
def connectTo(room):
    global ws
    global botName
    ws = create_connection("wss://euphoria.io/room/"+room+"/ws")
    ws.send(json.dumps({"type": "nick","data": {"name":botName}}))
    return(ws)

def disconnect(room):
    room.close()


def parse(incoming):
    global ws
    global paused
    global botName

    try:

        packet = json.loads(incoming)

        if packet["type"] == "ping-event":
            ws.send(json.dumps({'type': 'ping-reply', 'data': {'time': packet['data']['time']}}))

        elif packet['type'] == "send-event" and packet['data']['content'] == '!ping':
            send('Pong!',packet['data']['id'])
        elif packet['type'] == "send-event" and packet['data']['content'] == '!ping @' + botName:
            send('Pong!',packet['data']['id']) 
            
        elif packet['type'] == "send-event" and packet['data']['content'] == '!uptime':
            uptime = getUptime()
            send('/me has been up since ' + uptime,packet['data']['id'])      
        elif packet['type'] == "send-event" and packet['data']['content'] == '!uptime @' + botName:
            uptime = getUptime()
            send('/me has been up since ' + uptime,packet['data']['id'])

        elif packet['type'] == "send-event" and packet['data']['content'] == '!pause @' + botName:
            send('/me has been paused',packet['data']['id'])
            paused = True
        elif packet['type'] == "send-event" and packet['data']['content'] == '!unpause @' + botName:
            paused = False
            send('/me has been unpaused',packet['data']['id'])
            
        elif packet['type'] == "send-event" and packet['data']['content'] == '!help @' + botName:
            for message in helpMessage:
                sending = message.replace('**sender**','@' + packet['data']['sender']['name'].replace(' ',''))
                send(sending,packet['data']['id'])

        elif packet['type'] == "send-event" and packet['data']['content'] == "!kill @" + botName:
            send("Bot killed; will now exit.")
                
        else:
             return(packet)

        if packet["type"] == "ping-event":
            handleType = "ping"
        else:
            handleType = str(packet['data']['content'].split()[0][1:])
            
        return(json.loads(json.dumps({"type": "handled", 'class':handleType})))
        
    except Exception as error:
        print("Parsing error from karelia.py: " + str(error))
        return(json.dumps({"type": "error"}))

def spoof(packet):
    global ws
    global paused
    global botName

    try:

        if packet['type'] == "send-event" and '!ping' in packet['data']['content']:
            send('Pong!',packet['data']['id']) 
            
        elif packet['type'] == "send-event" and '!uptime' in packet['data']['content']:
            uptime = getUptime()
            send('/me has been up since ' + uptime,packet['data']['id'])      

        elif packet['type'] == "send-event" and '!pause' in packet['data']['content']:
            send('/me has been paused',packet['data']['id'])
            paused = True
        elif packet['type'] == "send-event" and '!unpause' in packet['data']['content']:
            paused = False
            send('/me has been unpaused',packet['data']['id'])
            
        elif packet['type'] == "send-event" and  '!help' in packet['data']['content']:
            for message in helpMessage:
                sending = message.replace('**sender**','@' + packet['data']['sender']['name'].replace(' ',''))
                send(sending,packet['data']['id'])

        elif packet['type'] == "send-event" and  "!kill" in packet['data']['content']:
            send("Bot killed; will now exit.")
                
        else:
             return(json.dumps({'type':'failure','cause':'packet contents not spoofable'}))
            
    except Exception as error:
        print("Spoofing error from karelia.py: " + str(error))
        return(json.loads(json.dumps({"type": "error"})))
