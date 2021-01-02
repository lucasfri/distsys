import socket
from threading import Thread
import time
from sys import platform as _platform
from turtledemo.minimal_hanoi import Disc
import pickle



server_ip = "192.168.0.220"
broadcast_ip = "192.168.0.255"
discovery_port = 1236
send_list_port = 1237
udp_port = 1234
tcp_port = 1235
buffer = 1024



def service_announcement():

    leader = True
    server_list = []
    response = 0
    
    print("OS: ", _platform)
  
    if leader == False:
        print("Leader")
    else: print("Not Leader")
    
    
    #broadcast socket
    sa_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sa_broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    #meine serverinformation an andere server schicken
    data = "%s:%s" % ("SA", server_ip)
    sa_broadcast_socket.sendto(data.encode("UTF-8"), (broadcast_ip, discovery_port))
    print("Following was broadcasted: ", data)
    
    # 3 Sekunden warten ob Antwort auf Broadcast kommt.
    timeout = time.time() + 3
    #leader_address = 0
    #data = bytearray()
    #leader_address = memoryview(data)
    
            
#    while time.time() < timeout:
 #       try:
  #          print("listening for other servers responses...")
   #         sa_broadcast_socket.recv_into(leader_address)
    #        response = leader_address
     #       if not data: break
      #      print("Leaderaddress is {}".format(leader_address))
            
    
       #     #TCP Socket für den Empfang der Serverliste

    leader_address = sa_broadcast_socket.recv(buffer)
    recv_serverlist_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recv_serverlist_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    recv_serverlist_socket.connect((leader_address, send_list_port))
    msg = recv_serverlist_socket.recv(buffer)
    server_list = pickle.loads(msg)
       # except:
        #    print("Done listening")
            
    sa_broadcast_socket.close()  
    response = 1
    print(response)
    
    #Wenn keine Antwort dann ernennt sich der Server zum Leader und startet server discovery und client discovery
    if response == 0:
        leader = True
        server_list.append(server_ip)
        print("I am the first server and leader.")
        Thread(target=client_discovery, args=()).start()
        Thread(target=server_discovery(), args=()).start()

    #Wenn Antwort kommt wird die Ringformation gestartet
    else:
        print("Received serverlist:")
        print(server_list)
        print("Starting Ring formation")
        ring_formation()

    
    return leader
    return server_list

    
def server_discovery():    
    
    recv_sa_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sa_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    recv_sa_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    #Bei Unix Systemen muss ein Broadcast empfangender UDP Socket an die Broadcastadresse gebunden werden, bei Windows an die lokale Adresse.
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin": 
        recv_sa_socket.bind((broadcast_ip, discovery_port))

    elif _platform == "win32" or _platform == "win64":
        recv_sa_socket.bind((server_ip, discovery_port))

    #empfange broadcast
    print("listening for new servers")
    sa_message, sa_address = recv_sa_socket.recvfrom(buffer)
    print(sa_message, sa_address)
    
    recv_sa_socket.close()

    #if sa_message[:2] == "SA":
        #Adresse des neuen Servers zur Serverliste hinzufügen
    print("server request received from server on IP {}".format(sa_message))
    located_server_ip = sa_message[3:]
    server_list.append(located_server_ip)
    print("server list:")
    print(server_list)
    
    #eigene Adresse an neuen Leader senden
    send_leader_address_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_leader_address_socket.sendto(server_ip.encode("UTF-8"), sa_address)
    print("Own address sent to new server.")
    send_leader_address_socket.close()
    
    #TCP connection aufbauen
    send_list_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_list_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    send_list_socket.bind((server_ip, send_list_port))
    send_list_socket.listen()
    new_server,new_server_address = send_list_socket.accept()
    print("Connected to new server.")


    #Serverliste an neuen Server übermitteln
    new_server.send('Hi'.encode('UTF-8'))
    #Serverliste an Nachbar übermitteln
    send_to_neighbour()
    print("sent serverlist")
    
    #starte Ringformation
    ring_formation()   
    
    send_list_socket.close()
        
        
    
    #else:
        #print("Error: Received unknown message.")
    
    server_discovery()



def ring_formation():
    print("Ring formation started.")
    
    
def send_to_neighbour():
    print("Send to neighbour.")

def recv_from_neighbour():
    print("recv_from_neighbour")
    


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
    neighbour = 0
    
    service_announcement()
    
    
    #udp_thread = threading.Thread(target=udp)
    #udp_thread.start()
    
    #tcp_thread = threading.Thread(target=connect)
    #tcp_thread.start()


    
    #ACCEPT_THREAD = Thread(target=server_discovery())

   # ACCEPT_THREAD.start()
    #ACCEPT_THREAD.join()
    
    
   
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
