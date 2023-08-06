__author__="Edward McKnight (EM-Creations.co.uk)"
__date__ ="$22-Jun-2012 15:51:16$"

import sampRcon

# Note: You're likely to get a socket.timeout exception if you have provided the incorrect rcon password
print "Starting program.."
query = sampRcon.new("127.0.0.1", 7777, "changeme1")

if query.connect(): # If the program has made a successful connection to the server
    commands = query.getCommandList() # Note commands[0] will contain: "Console Commands::", and not an actual server variable

    for command in commands:
        print command

    serverVars = query.getServerVariables() # Note serverVars[0]['var'] will contain: "Console Variables:", and not an actual server variable

    for var in serverVars:
        print var['var']+" - "+var['value']

    query.setWeather(8) # Set weather, if no weather id is given it sets weather id 1

    query.setGravity() # Set gravity, if no gravity float is given it sets the default gravity (0.008)

    query.kick(0) # Kick a player by player ID

    query.reloadLog() # Reload the log file

    query.reloadBans() # Reload the bans file

    query.say("Welcome to Eddy's server!") # Send an rcon say command to online players

    query.gmx() # Run next gamemode

    query.execConfig("server") # Executes a server configuration file

    query.call("say Hi guys!") # Directly executres an rcon command

    query.exit() # Shuts down the server
    
    print "Closing connection.."
    query.close() # Close the connection
else:
    print "Server didn't respond"



