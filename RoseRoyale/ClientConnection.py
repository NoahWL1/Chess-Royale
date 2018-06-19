from threading import Thread
import RoseRoyale.Graphics as rg
import time
import socket

global theClientConnection
theClientConnection = None

class ClientConnection:
    def __init__(self, username):
        global theClientConnection
        theClientConnection = self # Singleton
        self.username = username
        self.shouldRun = True
        print("Client connection starting...")
        
    def connect(self):
        IP = '127.0.0.1'
        connection = socket.socket()
        connection.connect((IP, 2396))
        self.connectionManager = ConnectionManager(connection, self.username)
        self.connectionManager.start()
        
        while self.shouldRun: # Main server connection loop
            messages = self.connectionManager.read()
            if messages != None:
                for message in messages:
                    #print("Message from server:" + message)
                    self.handleMessage(message)
            time.sleep(0.001)
    
    def sendPlayerPos(self, x, y):
        message = '!typePLAYERPOSITION!/type !name' + self.username + '!/name !posX' + str(x) + '!/posX !posY' + str(y) + '!/posY !end'
        #print(message)
        self._sendMessage(message)
    
    def _sendMessage(self, message):
        self.connectionManager.sendMessage(message)
        
    def handleMessage(self, message):
        #print('handling:', message)
        type = message[message.find('!type') + 5 : message.find('!/type')] # Get message type
        
        if type == 'PLAYERPOSITION':
            playerName = message[message.find('!name') + 5 : message.find('!/name')] # Get player name
            x = message[message.find('!posX') + 5 : message.find('!/posX')]
            y = message[message.find('!posY') + 5 : message.find('!/posY')]
            x = int(x)
            y = int(y)
            rg.updateMPPlayer(playerName, x, y)
            
    def close(self):
        print('Disconnecting from server')
        self.shouldRun = False
        self.connectionManager.close()

class ConnectionManager:
    def __init__(self, connection, name):
        Thread.__init__(self)
        self.connection = connection
        self.shouldRun = True
        self.name = name
        
    def start(self):
        self.listener = ServerListener(self, self.connection)
        self.writer = ServerWriter(self, self.connection)
        self.listener.start()
        self.writer.start()
        
    def read(self):
        return self.listener.getMessages()
    
    def sendMessage(self, message):
        self.writer.sendMessage(message)
        
    def close(self):
        self.shouldRun = False
        self.connection.close()
    
class ServerListener(Thread):
    def __init__(self, manager, connection):
        Thread.__init__(self)
        self.manager = manager
        self.connection = connection
        self.receivedMessages = []
        
    def run(self):
        while self.manager.shouldRun:
            buffer = ''
            #print('serverlistener')
            received = self.connection.recv(2048)
            buffer += received.decode('utf-8')
            if buffer != '':
                self.receivedMessages.append(buffer[0 : buffer.find("!end")])
            time.sleep(0.001)
    
    def getMessages(self):
        messages = self.receivedMessages.copy()
        self.receivedMessages.clear()
        return messages
        
class ServerWriter(Thread):
    def __init__(self, manager, connection):
        Thread.__init__(self)
        self.manager = manager
        self.connection = connection
        self.messages = []
        self.hasMessages = False
        print("Client writer created")
        
    def run(self):
        nameInfo = '!typeCLIENTNAME!/type! !name' + self.manager.name + '!/name !end'
        self.connection.sendall(nameInfo.encode("utf-8"))
        print('Sent client name')
        while self.manager.shouldRun:
            #print('serverwriter')
            if len(self.messages) > 0:
                #print("Writing message: " + self.messages[0])
                self.connection.sendall(self.messages[0].encode("utf-8"))
                del self.messages[0]
            time.sleep(0.001)
                
    def sendMessage(self, message):
        self.messages.append(message)