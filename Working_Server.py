import socket
from threading import Thread
import time
from sys import platform as _platform
from turtledemo.minimal_hanoi import Disc
from _socket import SHUT_RDWR

server_ip = "192.168.178.41"
broadcast_ip = "192.168.178.255"
discovery_port = 1999
udp_port = 1234
tcp_port = 1235
buffer = 1024

server_list = []

def server_discovery():

  #  host_udp_socket.bind((server_ip, udp_port))
    #check mithilfe einer if-anweisung ob das Betriebssystem Win oder Unixbasiert ist
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin": 
        host_udp_socket.bind((broadcast_ip, discovery_port))
        # linux 
    elif _platform == "win32" or _platform == "win64":
         host_udp_socket.bind((server_ip, discovery_port))
    
    print("Ich habe erkannt, dass du das folgende Betriebssystem hast: ", _platform)

    #meine serverinformation an andere server schicken
    data = "%s:%s" % ("SA", server_ip)
    host_udp_socket.sendto(str.encode(data), (broadcast_ip, 1236))
    print("Following was broadcasted: ", data)
    
   # wenn SA... Nachricht empfangen habe, schicke ich eine SB Nachricht an den Sender mit meiner IP POrt zurueck
   
    print("Waiting for server request...") 
       
    #sa_message = host_udp_socket.recv(buffer)
    #if sa_message str.startswith(SA)
    #print("client request received from client on IP {}".format(client_address))

    #infos von anderen servern empfangen
    timeout = time.time() + 1
    data = bytearray()
    new_server = memoryview(data)

    while time.time() < timeout:
        #try:
        print("test0")
        host_udp_socket.recv_into(new_server)
        server_list.append(new_server)
        print("receiving")
       # except:
       #     print("Listening for Servers")
       
    Thread(target=client_discovery, args=()).start()


#Create UDP socket, listen for broadcast, transmit own address
def client_discovery(): 
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if _platform == "linux" or _platform == "linux2" or _platform == "darwin": 
        udp_socket.bind((broadcast_ip, udp_port))
        # linux 
    elif _platform == "win32" or _platform == "win64":
         udp_socket.bind((server_ip, udp_port))
    
    #udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    print("server up and running...")
    print("Waiting for client request...") 
       
    request, client_address = udp_socket.recvfrom(buffer)
    print("client request received from client on IP {}".format(client_address))
    
    udp_socket.close()
    
    udp_socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    udp_socket2.bind((server_ip, udp_port))
    
    udp_socket2.sendto(str.encode(server_ip), client_address)
    print("Establishing connection")
    Thread(target=client_discovery, args=()).start()
    Thread(target=connect, args=()).start()

def connect():
    # Die Verbindung akzeptieren
    client,client_address = server.accept()
    print("Verbunden mit client {}".format(str(client_address)))

    # Anforderung des Benutzernamens und Speicherung dessen
    client.send('NICK'.encode('ascii'))
    nickname = client.recv(1024).decode('ascii')
    nicknames.append(nickname)
    clients.append(client)

    # Benutzername mitteilen und broadcasten
    print("Der Benutzername ist {}".format(nickname))
    broadcast("{} ist dem Blackboard beigetreten!".format(nickname).encode('ascii'))
    client.send(' Mit dem Server verbunden!'.encode('ascii'))
    
         # Start Handling Thread For Client
    Thread(target=messaging(client), args=(client, )).start()

def broadcast(message): #um Nachrichten  zu den Clients zu senden
    for client in clients:
        client.send(message)

def messaging(client): #Fuer jeden Client auf dem Server wird ein eigener handle aufgerufen in jedem einzelnen Thread
    try:
        message = client.recv(1024) #Nachricht empfangen
        messages.append(message)
        broadcast(message) #Wenn eine Nachricht angekommen ist, wird die Nachricht an die anderen Clients gebroadcastet


    except: #Sofern der Client keine Nachricht empfaengt
        index = clients.index(client)
        clients.remove(client) #Client wird von der Clientlist entfernt
        client.close()
        nickname = nicknames[index]
        broadcast(f'{nickname} hat das Blackboard verlassen'.encode('ascii'))
        nicknames.remove(nickname)
        

if __name__ == "__main__":
    
    #TCP connection  
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    #server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    #server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    
    #server_ip = socket.gethostbyname(socket.gethostname())
    server_address = (server_ip, tcp_port)
    print('Server gestartet auf IP %s und Port %s' % server_address)
    server.bind(server_address)
    server.listen()
    
    clients = []
    nicknames = []
    messages = []
    #udp_thread = threading.Thread(target=udp)
    #udp_thread.start()
    
    #tcp_thread = threading.Thread(target=connect)
    #tcp_thread.start()
    host_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host_udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    
    ACCEPT_THREAD = Thread(target=server_discovery)

    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    
    
    #server_discovery()
    #while True:
        
     #   try:
      #      client_discovery()
    
       # except:
        #    continue
            
        #connect()
                
    print(clients)
    print(nicknames)
    print(messages)

        
        
#Auf Unix Endgeräten muss erster UDP socket an broadcast IP_binden und bei Windowsgeräten muss erster UDP socket an server_IP biden 
