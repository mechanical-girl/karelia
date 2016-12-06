import karelia

karelia.shortHelp = "A single line help message."
karelia.helpMessage = ["This allows a help message to be specified.",
                       "Each entry in this list will be sent as a separate message."]
karelia.botName = "templateBot"

room = "test"

connection = karelia.connectTo(room)

while True:
    
    packet = karelia.parse()

    # Your code here
