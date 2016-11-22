#############################################################
#   Karelia library, by PouncySilverkitten                  #
#   github.com/PouncySilverkitten/karelia                   #
#                                                           #
#############################################################

from websocket import create_connection
import json
import time


startTime = time.time()
paused = False
helpMessage = ["This bot has not had a help message specified. This message was generated automatically."]

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

    uptime = str(updays) + " days " + str(uphours) + " hours " + str(upminutes) + " minutes"
    return uptime

def send(message,parent=''):
    global paused
    global ws
    if not paused:
        ws.send(json.dumps({'type': 'send', 'data': {'content': message, 'parent': parent}}))
    
def connectTo(room,name):
    global ws
    global botName
    botName = name
    ws = create_connection("wss://euphoria.io/room/"+room+"/ws")
    ws.send(json.dumps({"type": "nick","data": {"name":name}}))
    return(ws)


def parse(incoming):
    global ws
    global paused
    
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
        send('/me has been up for ' + uptime,packet['data']['id'])

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
            
    else:
        print(incoming)
        
    return(packet)
