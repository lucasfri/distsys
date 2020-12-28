import socket
import threading
import time

server_ip = "192.168.0.220"
broadcast_ip = "192.168.0.255"
udp_port = 1234
tcp_port = 1235
buffer = 1024

server_list = []

def server_discovery():
    host_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host_udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    host_udp_socket.bind((server_ip, udp_port))
    
    data = "%s:%s" % ("SA", server_ip)
    host_udp_socket.sendto(str.encode(data), (broadcast_ip, 1236))
    print("IP sent to servers.")
    
    timeout = time.time() + 1
 
    while time.time() < timeout:
        try:
            print("test0")
            new_server = host_udp_socket.recvfrom(buffer)
            server_list.append(new_server)
            print("receiving")
        except:
            print("Listening for Servers")

server_discovery()
    
#Create UDP socket, listen for broadcast, transmit own address
def client_discovery(): 
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((broadcast_ip, udp_port))
    
    #udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 2)
    #udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 2)
    
    print("server up and running...")
    print("Waiting for client request...") 
       
    request, client_address = udp_socket.recvfrom(buffer)
    print("client request received from client on IP {}".format(client_address))
    
    udp_socket.close()
    
    udp_socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket2.bind((server_ip, udp_port))
    
    udp_socket2.sendto(str.encode(server_ip), client_address)
    print("Establishing connection")


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
    thread = threading.Thread(target=messaging, args=(client,))
    thread.start()

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
    
    #udp_thread = threading.Thread(target=udp)
    #udp_thread.start()
    
    #tcp_thread = threading.Thread(target=connect)
    #tcp_thread.start()

    while True:
        
        try:
            client_discovery()
                
        except:
            continue
            
        connect()
            
        print(clients)
        print(nicknames)
        print(messages)
        
        
        
#Auf Unix Endgeräten muss erster UDP socket an broadcast IP_binden und bei Windowsgeräten muss erster UDP socket an server_IP biden 
