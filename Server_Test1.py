import socket
buffer = 1024
clientdict = {}


#UDP connection

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(("192.168.0.220", 1234))

#tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    
    # Enable broadcasting mode
#tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

print("server up and running...")

#while True:
print("Waiting for client request...")
client_name, client_address = udp_socket.recvfrom(buffer)
clientdict[client_address] = client_name
print("client request received from client {} on IP {}".format(client_name, client_address))
print("Establishing connection")
    
udp_socket.sendto(str.encode("192.168.0.220"), client_address)

udp_socket.close()  #Ansonsten errno 48: address already in use
  

#TCP connection  

import threading
import socket
import sys
from test.test_decimal import file

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address given on the command line
server_name = "192.168.0.220"
#server_name = socket.gethostbyname(socket.gethostname())
server_address = (server_name, 10000)
print('Server gestartet auf %s mit Port %s' % server_address)
server.bind(server_address)
server.listen(1)

clients = []
nicknames = []

def broadcast(message): #um Nachrichten  zu den Clients zu senden
    for client in clients:
        client.send(message)

def handle(client): #Fuer jeden Client auf dem Server wird ein eigener handle aufgerufen in jedem einzelnen Thread
    while True:
        try:
            message = client.recv(1024) #Nachricht empfangen
            broadcast(message) #Wenn eine Nachricht angekommen ist, wird die Nachricht an die anderen Clients gebroadcastet

        
        except: #Sofern der Client keine Nachricht empfaengt
            index = clients.index(client)
            clients.remove(client) #Client wird von der Clientlist entfernt
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} hat das Blackboard verlassen'.encode('ascii'))
            nicknames.remove(nickname)
            break

def receive():
    while True:
        # Die Verbindung akzeptieren
        client,server_address = server.accept()
        print("Verbunden mit {}".format(str(server_address)))

        # Anforderung des Benutzernamens und Speicherung dessen
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)

        # Benutzername mitteilen und broadcasten
        print("Der Benutzername ist {}".format(nickname))
        broadcast("{} ist dem Blackboard beigetreten!".format(nickname).encode('ascii'))
        client.send('Mit dem Server verbunden!'.encode('ascii'))


        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()
                
receive()