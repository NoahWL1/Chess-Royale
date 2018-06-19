from RoseRoyale.Server import Server
from RoseRoyale.ClientConnection import ClientConnection
from threading import Thread
import RoseRoyale.Graphics
import time
import random
import os

myServer = None
cc = None

def Main():
    #setupServer()
    time.sleep(1) # Temp
    #setupServerConnection()
    RoseRoyale.Graphics.init() # Start main game loop in this thread
    shutdown()

def setupServerConnection():
    global cc
    cc = ClientConnection(str(random.randint(1, 100))) # Create client connection manager instance
    connectionThread = Thread(target = cc.connect, args=())
    connectionThread.start() # Start connection manager in its own thread
    
def setupServer():
    global myServer
    myServer = Server("miserver") # Create server instance
    serverThread = Thread(target = myServer.initialize, args=())
    serverThread.start() # Staaaaart server in its own thread
    
def shutdown():
    print('Shutting down')
    #cc.close()
    #myServer.close()
    time.sleep(0.5) # Allow for all threads to close cleanly
    os._exit(0) # Unclean temporary exit

if __name__ == "__main__":
    Main()