import socket
from threading import Thread
import time
from sys import platform as _platform
from turtledemo.minimal_hanoi import Disc
from _socket import SHUT_RDWR


server_ip = "192.168.178.41"
broadcast_ip = "192.168.178.255"
discovery_port = 1236
udp_port = 1234
tcp_port = 1235
buffer = 1024
leader = true

def server_discovery():

    print("Ich habe erkannt, dass du das folgende Betriebssystem hast: ", _platform)

    #meine serverinformation an andere server schicken
    data = "%s:%s" % ("SA", server_ip)
    host_udp_socket.sendto(str.encode(data), (broadcast_ip, discovery_port))
    print("Following was broadcasted: ", data)
   
    Thread(target=listen_for_servers, args=()).start()
        
    Thread(target=client_discovery, args=()).start()
    host_udp_socket.close()

def listen_for_servers():    
   # wenn SA... Nachricht empfangen habe, schicke ich eine SB Nachricht an den Sender mit meiner IP POrt zurueck
    #listen_for_servers_socket.bind((server_ip, 1236))
    ##check mithilfe einer if-anweisung ob das Betriebssystem Win oder Unixbasiert ist
    
    listen_for_servers_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_for_servers_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    listen_for_servers_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin": 
        listen_for_servers_socket.bind((broadcast_ip, discovery_port))
        # linux 
    elif _platform == "win32" or _platform == "win64":
        listen_for_servers_socket.bind((server_ip, discovery_port))

    #checken ob ein server acknowledgement vorliegt
    sa_message = listen_for_servers_socket.recv(buffer).decode("UTF-8")
    #listen_for_servers_socket.close()
    
    
    if leader == true and sa_message[:2] == "SA":
        print("server request received from server on IP {}".format(sa_message))
        located_server_ip = sa_message[3:]
        server_list.append(located_server_ip)
        for member in server_list:
            listen_for_servers_socket.sendto(server_list)
        
    elif leader == false and sa_message[:2] == "SA":
        print("SA Nachricht erhalten aber kein Leader.")
    
#Hier weiter machen. Es kann maximal 4 Fälle geben welche mit if schleife abgedeckt werden können/müssen
        
        #als leader die serverliste an die anderen server senden
        
#5 sekunden darauf warten, dass der leader mir die client list sendet
    #infos von anderen servern empfangen
    #timeout = time.time() + 1
    #data = bytearray()
    #new_server = memoryview(data)


    #while time.time() < timeout:
        #try:
    #    print("listening for other servers responses...") 
    #    host_udp_socket.recv_into(new_server)
    #    server_list.append(new_server)
    #    print("receiving")
       # except:
       #     print("Listening for Servers")
       
    Thread(target=listen_for_servers(), args=()).start()


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
        
    udp_socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    udp_socket2.bind((server_ip, udp_port))
    
    udp_socket2.sendto(str.encode(server_ip), client_address)
    print("Establishing connection")
    Thread(target=client_discovery, args=()).start()
    Thread(target=connect, args=()).start()

def connect():
    
        #TCP connection  
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    #server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    #server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    
    #server_ip = socket.gethostbyname(socket.gethostname())
    server_address = (server_ip, tcp_port)
    print('Server gestartet auf IP %s und Port %s' % server_address)
    server.bind(server_address)
    server.listen()
    
    
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
    Thread(target=messaging(client), args=(client)).start()
    

if __name__ == "__main__":
    

    server_list = []
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
