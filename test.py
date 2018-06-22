from karelia import newBot

bot = newBot('','xkcd')

bot.connect()
while True:
    bot.parse()

