import karelia
import time

def on_kill():
    """Define actions to be performed when the bot receives a !kill command"""
    print("Got killed :-(")

# Initialise a bot with nick (or [nick1, nick2]) and room the bot will connect to
bot = karelia.bot("ExampleBot", "test")

# Define response messages to the botrulez.
bot.stock_responses['short_help'] = "Short help message"
bot.stock_responses['long_help'] = ["Long help message can be sent over multiple messages","This message was generated by Example Bot"]

# Assign on_kill function to bot's on_kill.
bot.on_kill = on_kill

# Connect to the room
bot.connect()

while True:
    try:
        while True:
            message = bot.parse()

            if message.type == "send-event":
                print(f"{message.data.sender.name}: {message.data.content}")
                if message.data.content.split()[0] == "!changenick":
                    bot.change_nick("NewNick")

    except:
        bot.log()
        bot.disconnect()
    finally:
        time.sleep(1)
        bot.connect()
