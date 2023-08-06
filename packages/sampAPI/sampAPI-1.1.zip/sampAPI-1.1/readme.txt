############################################################################################
# Python SA-MP (GTA San Andreas Multiplayer) API
# Version 1.1
# This API allows you to make remote connections to a SA-MP server from within Python.
# You must have the RCON password of the server to use the sampRcon class.
# Copyright 2012 Edward McKnight (EM-Creations.co.uk)
# Creative Commons Attribution-NoDerivs 3.0 Unported License
############################################################################################

##########################################################################################
# Change log (1.0 -> 1.1):
# Servers with over 255 online or max players will now display correctly
# Some fixes were made for RCON commands that were not working properly
# Changed the copyright licensing
##########################################################################################

Examples are provided in the sampQueryExample.py and sampRconExample.py files.

Steps:

1. Import the classes you want to use. (import sampQuery, sampRcon)
2. Instantiate the class using: (query = sampQuery.new("127.0.0.1", 7777))
3. Determine if a successful connection has been made: (if query.connect():)
4. Use the documented methods and retrieve data.