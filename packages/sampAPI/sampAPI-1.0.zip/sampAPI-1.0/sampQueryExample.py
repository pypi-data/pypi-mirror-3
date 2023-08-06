__author__="Edward McKnight (EM-Creations.co.uk)"
__date__ ="$22-Jun-2012 15:51:16$"

import sampQuery

print "Starting program.."
query = sampQuery.new("127.0.0.1", 7777)

print "Trying to connect.."
if query.connect(): # If the program has made a successful connection to the server
    print "Info:"
    serverInfo = query.getInfo()

    if serverInfo['password']:
        passworded = "True"
    else:
        passworded = "False"
    print serverInfo['hostname']+" - Password: "+passworded+" Players: "+str(serverInfo['players'])+"/"+str(serverInfo['maxplayers'])+" Map: "+serverInfo['map']+" Gamemode: "+serverInfo['gamemode']


    basicPlayers = query.getBasicPlayers()

    if basicPlayers: # If the server has players online
        print "Basic Players:"
        for player in basicPlayers:
            print str(player['name'])+" "+str(player['score'])
    else:
        print "No players"

    
    detailedPlayers = query.getDetailedPlayers()

    if detailedPlayers: # If the server has players online
        print "Detailed Players:"
        for player in detailedPlayers:
            print "("+str(player['id'])+")"+str(player['name'])+" Score: "+str(player['score'])+" Ping: "+str(player['ping'])
    else:
        print "No players"
    
    rules = query.getRules()

    print "Rules:"
    for rule in rules:
        print str(rule['rule'])+" - "+str(rule['value'])

    print "Closing connection.."
    query.close() # Close the connection
else:
    print "Server didn't respond"