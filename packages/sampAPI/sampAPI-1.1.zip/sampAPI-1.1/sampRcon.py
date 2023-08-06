__author__="Edward McKnight (EM-Creations.co.uk)"
__date__ ="$22-Jun-2012 15:51:16$"

###############################################################
# sampRcon.py
# Version 1.1
# This class connects to a specific SA-MP server via sockets.
# You must have the RCON password of the server to use this.
# Copyright 2012 Edward McKnight (EM-Creations.co.uk)
# Creative Commons Attribution-NoDerivs 3.0 Unported License
###############################################################

import socket
import time
import math

class SampRcon:

    def __init__(self, sock=None, server="127.0.0.1", port=7777, password="changeme"):
        if sock is None:
            self.serverVars = [server, port, password]
        else:
            self.sock = sock


    def connect(self):
        try:
            self.serverVars[0] = socket.gethostbyname(self.serverVars[0])
            socket.setdefaulttimeout(2)
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM) # Internet and UDP
        except socket.gaierror:
            return False
        
        ipSplit = str.split(self.serverVars[0], '.')

        packet = 'SAMP'
        packet += chr(int(ipSplit[0]))
        packet += chr(int(ipSplit[1]))
        packet += chr(int(ipSplit[2]))
        packet += chr(int(ipSplit[3]))
        packet += chr(self.serverVars[1] & 0xFF)
        packet += chr(self.serverVars[1] >> 8 & 0xFF)
        packet += 'p0101'

        try:
            self.send(packet)

            reply = self.receive()[10:]

            if reply == 'p0101':
                return True
            else:
                return False
        except socket.timeout:
            return False


    def send(self, msg):
            self.sock.sendto(msg, (self.serverVars[0], self.serverVars[1]))


    def receive(self, buffer=1024):
        msg = self.sock.recv(buffer)
        return msg


    def close(self):
        self.sock.close()


    def getCommandList(self): # Finished
        """Returns a list of commands:
        [
            "command0",
            "command1",
        ]"""
        packet = self.assemblePacket("cmdlist")
        commands = self.rconSend(packet)

        for i in range(len(commands)):
            commands[i] = commands[i].strip()

        return commands


    def getServerVariables(self): # Outputs server variables with hardly any formatting
        """Returns a list of server variables:
        [
            {
            'var' : string,
            'value' : string,
            },
            {
            'var' : string,
            'value' : string,
            },
        ]"""
        packet = self.assemblePacket("varlist")
        vars = self.rconSend(packet)

        finalVars = []

        for i in range(len(vars)):
            finalVars.append({'var' : "", 'value' : ""})

        for i in range(len(vars)):
            if i == 0:
                finalVars[i]['var'] = "Console Variables:"
                finalVars[i]['value'] = ""
            else:
                temp = vars[i].split("=")
                finalVars[i]['var'] = temp[0].strip()
                finalVars[i]['value'] = temp[1].strip()

        return finalVars


    def setWeather(self, weatherID=1): # Finished
        """Sets the weather to the id specified. If no weather id is passed 1 will be used."""
        command = "weather "+str(weatherID)
        packet = self.assemblePacket(command)
        self.rconSend(packet, False)


    def setGravity(self, gravity=0.008): # Finished
        """Sets the gravity to the value specified. If no gravity value is passed 0.008 will be used."""
        command = "gravity "+str(gravity)
        packet = self.assemblePacket(command)
        self.rconSend(packet, False)


    def ban(self, playerID): # Finished
        """Bans a player by player id from the server."""
        command = "ban "+str(playerID)
        packet = self.assemblePacket(command)
        self.rconSend(packet, False)


    def kick(self, playerID): # Finished
        """Kicks a player by player id from the server."""
        command = "kick "+str(playerID)
        packet = self.assemblePacket(command)
        self.rconSend(packet, False)


    def banAddress(self, address): # Finished
        """IP bans a player from the server."""
        command = "banip "+str(address)
        packet = self.assemblePacket(command)
        self.rconSend(packet, False)


    def unbanAddress(self, address): # Finished
        """Unbans an IP from the server."""
        command = "unbanip "+str(address)
        packet = self.assemblePacket(command)
        self.rconSend(packet, False)

        
    def reloadLog(self): # Finished
        """Reloads the server's log file."""
        packet = self.assemblePacket("reloadlog")
        self.rconSend(packet)


    def reloadBans(self): # Finished
        """Reloads the server's bans file."""
        packet = self.assemblePacket("reloadbans")
        self.rconSend(packet)


    def say(self, message): # Finished
        """Sends an admin message to players on the server."""
        command = "say "+str(message)
        packet = self.assemblePacket(command)
        self.rconSend(packet, False)


    def changeGameMode(self, gamemode): # Finished
        """Changes the server's current gamemode."""
        command = "changemode "+str(gamemode)
        packet = self.assemblePacket(command)
        self.rconSend(packet, False)


    def nextGameMode(self): # Finished
        """Runs next gamemode (gmx)."""
        packet = self.assemblePacket("gmx")
        self.rconSend(packet, False)


    def gmx(self): # Finished
        """Runs next gamemode (gmx)."""
        self.nextGameMode()


    def execConfig(self, config): # Finished
        """Executes a server configuration file."""
        command = "exec "+str(config)
        packet = self.assemblePacket(command)
        self.rconSend(packet, False)


    def loadFilterscript(self, fs): # Finished
        """Loads a filterscript."""
        command = "loadfs "+str(fs)
        packet = self.assemblePacket(command)
        self.rconSend(packet, False)


    def loadFS(self, fs): # Finished
        """Loads a filterscript."""
        self.loadFilterscript(fs)


    def unloadFilterscript(self, fs): # Finished
        """Unloads a filterscript."""
        command = "unloadfs "+str(fs)
        packet = self.assemblePacket(command)
        self.rconSend(packet, False)


    def unloadFS(self, fs): # Finished
        """Unloads a filterscript."""
        self.unloadFilterscript(fs)


    def reloadFilterscript(self, fs): # Finished
        """Reloads a filterscript."""
        command = "reloadfs "+str(fs)
        packet = self.assemblePacket(command)
        self.rconSend(packet, False)


    def reloadFS(self, fs): # Finished
        """Reloads a filterscript."""
        self.reloadFilterscript(fs)


    def exit(self): # Finished
        """Shuts down the server."""
        packet = self.assemblePacket("exit")
        self.rconSend(packet, False)


    def call(self, command, delay=False): # Finished
        """Sends an RCON command."""
        packet = self.assemblePacket(str(command))
        return self.rconSend(packet, delay)

    def rconSend(self, msg, delay = 1.0):
        self.send(msg)

        if delay == False:
            return

        data = []
        myTime = self.microtime(True) + delay

        while self.microtime(True) < myTime:
            temp = self.receive()[13:]

            if len(temp):
                data.append(temp)
            else:
                break

        return data
        

    def assemblePacket(self, command):
        ipSplit = str.split(self.serverVars[0], '.')

        packet = 'SAMP'
        packet += chr(int(ipSplit[0]))
        packet += chr(int(ipSplit[1]))
        packet += chr(int(ipSplit[2]))
        packet += chr(int(ipSplit[3]))
        packet += chr(self.serverVars[1] & 0xFF)
        packet += chr(self.serverVars[1] >> 8 & 0xFF)
        packet += 'x'

        packet += chr(len(self.serverVars[2]) & 0xFF)
        packet += chr(len(self.serverVars[2]) >> 8 & 0xFF)
        packet += self.serverVars[2]
        packet += chr(len(command) & 0xFF)
        packet += chr(len(command) >> 8 & 0xFF)
        packet += command

        return packet


    def microtime(self, get_as_float=False) :
        if get_as_float:
            return time.time()
        else:
            return '%f %d' % math.modf(time.time())


def new(server="127.0.0.1", port=7777, password="changeme"):
    """Creates a new sampRcon object, if an address isn't passed 127.0.0.1 is used. If a port isn't passed 7777 is used. If a password isn't passed changeme is used."""
    return SampRcon(None, server, port, password)