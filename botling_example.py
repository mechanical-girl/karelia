import karelia

botling = karelia.Botling()

botling.nick = "WaitWait"
botling.room = "test"

botling.regex = """^wait\s+wait$ -> [
i.imgur.com/dJIqoXM.png,
i.imgur.com/hdLiqM8.png,
i.imgur.com/COqb3Zf.png,
i.imgur.com/JXtUBNJ.png,
i.imgur.com/wjKFuZG.png,
i.imgur.com/F5a4o1U.png,
i.imgur.com/uVQlDJS.png,
i.imgur.com/cuK1wIN.png,
i.imgur.com/8kjuUvN.png,
i.imgur.com/qAJjMe7.png,
i.imgur.com/2mjOtxH.png,
i.imgur.com/OkKvrNl.png,
i.imgur.com/W8334oH.png,
i.imgur.com/I7Pmsp1.png,
i.imgur.com/tLRjU9N.png,
i.imgur.com/IaPD3qz.png,
i.imgur.com/XrxQYl2.png,
i.imgur.com/G6qpG5L.png,
i.imgur.com/N7wJfgF.png,

]"""

botling.regex = "Nested [replies,text] work[s,,,] like [this, this [or do they?, except [it,they] don't]"

botling.construct()

print(botling.compile_reply("Nested [replies,text] work[s,,,] like [this, this [or do they?, except [it,they] don't]")


botling.connect()

while True:
    try:
        botling.parse()
    except:
        botling.disconnect()
    finally:
        time.sleep(10)
       botling.connect()
