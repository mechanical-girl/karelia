import karelia

karelia.shortHelp = "A single line help message."
karelia.helpMessage = ["This allows a longer help message to be specified.",
                       "Each entry in this list will be sent as a separate message."]
karelia.botName = "templateBot"
room = "test"


connection = karelia.connectTo(room)

while True:
    
    packet = karelia.parse()

    # Your code here

    # This will force Karelia to treat the packet - specifically, to respond to
    # any bang-commands therein - as though the bots name was @otherNick
    spoofreturn = karelia.spoof(packet,"otherNick")
