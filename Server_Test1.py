import socket
import threading
from threading import Thread
import time
from sys import platform as _platform
import pickle

#from smtplib import server

server_ip = "192.168.0.220"
broadcast_ip = "192.168.0.255"
discovery_port = 1236
send_list_port = 1237
server_msg_port = 1239
server_sl_port = 1240
server_cl_port = 1242
heartbeat_port = 1243
udp_port = 1234
tcp_port = 1235 
server_com_port = 1238
buffer = 1024

def service_announcement():
    
    global server_list
    global leader
    global leader_ip
    
    #broadcast socket
    sa_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sa_broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    #sa_broadcast_socket.setblocking(False)
    
    #meine serverinformation an andere server schicken
    data = "%s:%s" % ("SA", server_ip)
    sa_broadcast_socket.sendto(data.encode("UTF-8"), (broadcast_ip, discovery_port))
    print("Following was broadcasted: ", data)
    
    # 3 Sekunden warten ob Antwort auf Broadcast kommt.

    sa_broadcast_socket.settimeout(1)
    try:
        print("listening for other servers responses...")
        leader_ip = sa_broadcast_socket.recv(buffer).decode("UTF-8")
        print("Leader response received on {}".format(leader_ip))
    except socket.timeout as e:
            print(e)
            print("Nothing received")
            
    sa_broadcast_socket.close()  
    
    
    #Wenn keine Antwort dann ernennt sich der Server zum Leader und startet server discovery und client discovery
    if len(leader_ip) == 0:
        leader = True
        leader_ip = server_ip
        server_list.append(server_ip)
        print("I am the first server and leader.")
        print(server_list)
        #Thread(target=client_discovery, args=()).start()
        #Thread(target=server_discovery(server_list, server_msg_connections), args=(server_list, )).start()
        
    #Wenn Antwort kommt wird die Ringformation gestartet
    else:
            #TCP Socket fuer den Empfang der Serverliste
        recv_serverlist_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        recv_serverlist_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_serverlist_socket.connect((leader_ip, send_list_port))
        
        msg = recv_serverlist_socket.recv(buffer)
        server_list = pickle.loads(msg)
        recv_serverlist_socket.close()
        print("Received serverlist:")
        print(server_list)


    
def server_discovery(): 
    
    global server_list
    global server_msg_connections
    global leader

    
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
        #Adresse des neuen Servers zur Serverliste hinzufuegen
    print("server request received from server on IP {}".format(sa_message))
    located_server_ip = sa_message[3:]
    located_server_ip = located_server_ip.decode("UTF-8")
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
    send_list_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
        send_list_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        

    send_list_socket.bind((server_ip, send_list_port))
    send_list_socket.listen()
    new_server,new_server_address = send_list_socket.accept()
    print("Connected to new server.")



    #Serverliste an neuen Server übermitteln
    msg = pickle.dumps(server_list)
    new_server.send(msg)
    print("sent serverlist to new server")
    send_list_socket.close()
    #Serverliste von Leader an alle Noleader
    leader_noleader_send_serverlist()
    
    Thread(target=leader_noleader_msg_tcp, args=()).start()
    time.sleep(0.1)
    Thread(target=leader_noleader_sl_tcp, args=()).start()
    time.sleep(0.1)
    Thread(target=leader_noleader_cl_tcp, args=()).start()
    time.sleep(0.1)
    Thread(target=heartbeat, args=()).start()
    time.sleep(0.1)    
    Thread(target=server_discovery(), args=()).start()
    
    ring_formation(server_list)

def heartbeat():
    
    global leader
    global leader_ip
    global server_list


    heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    heartbeat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
        heartbeat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        
    
    if leader == True:

        heartbeat_socket.bind((leader_ip, heartbeat_port))
        heartbeat_socket.listen()
        print("heartbeat_msg_socket erstellt")
        
        noleader, noleader_address = heartbeat_socket.accept()
        print("Heartbeat socket connected")
        
        #heartbeat_connections.append(noleader)

        noleader.send("Heartbeat started for me.".encode("UTF-8"))
        
        check = noleader.recv(buffer)
        print(check)


        #try:
        while True:
            ack = noleader.recv(buffer)
            if ack != check:
                print("Old server_list: {}".format(server_list))
                index = server_list.index(noleader_address)
                #get first element of tuple
                noleader_ip = noleader_address()[0]
                server_list.remove(noleader_ip)
                leader_noleader_send_serverlist()
                print("New server_list: {}".format(server_list))
                continue
            else:
                print(ack)
        '''if len(ack) != 0:
               print("heartbeat received from {}".format(ack))
   
           else:
               print("Old server_list: {}".format(server_list))
               index = server_list.index(server_address)
               server_list.remove(noleader_address)
               leader_noleader_send_serverlist()
               print("New server_list: {}".format(server_list))'''
                   
       
        #except: #Sofern der Client keine Nachricht empfaeng
         #   print("Except.")

     
    else:
        time.sleep(1)
        heartbeat_socket.connect((leader_ip, heartbeat_port))
        print("Heartbeat TCP connected.")
        ack2 = heartbeat_socket.recv(buffer).decode("UTF-8")
        print(ack2)

            #muss noch was passieren
            
        while True:
            try:
                heartbeat_socket.send(server_ip.encode("UTF-8"))
                print("heartbeat sent to leader")

            except:
                print("Connection to noleader lost")
                server_list.remove(leader_ip)
                Thread(target=ring_formation(), args=()).start()
            time.sleep(10)
            


def leader_noleader_msg_tcp():
    
    global leader
    global leader_ip
    global server_msg_connections
    global messages
    
    server_msg_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_msg_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
        server_msg_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        
    print(server_msg_connections)
    
    if leader == True:

        server_msg_socket.bind((leader_ip, server_msg_port))
        server_msg_socket.listen()
        print("server_msg_socket erstellt")
        
        noleader, noleader_address = server_msg_socket.accept()
        
        #server_tcp_connections.append(noleader)
        server_msg_connections.append(noleader)
        print("MSG TCP server connections: {}".format(server_msg_connections))
        
        
        #print("Connected with noleader {}".format(noleader))
        print("Connected with noleader {}".format(noleader_address)) 
        
          
     
    else:
        time.sleep(1)
        server_msg_socket.connect((leader_ip, server_msg_port))
        print("Server msg tcp connected.")
                    
        while True:
            last_sent_msg = server_msg_socket.recv(buffer).decode("UTF-8")
            messages.append(last_sent_msg)
            print(last_sent_msg)


        server_msg_socket.close()

    
    #return server_tcp_connections   
    
def leader_noleader_sl_tcp():
    
    global leader
    global leader_ip
    global server_sl_connections
    
    server_sl_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
        server_sl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        

    if leader == True:

        server_sl_socket.bind((leader_ip, server_sl_port))
        server_sl_socket.listen()
        print("server_sl_socket erstellt")
        
        noleader, noleader_address = server_sl_socket.accept()
        
        #server_tcp_connections.append(noleader)
        server_sl_connections.append(noleader)
        print("SL TCP server connections: {}".format(server_sl_connections))
        
        
        #print("Connected with noleader {}".format(noleader))
        print("Connected with noleader {}".format(noleader_address)) 
    
      
 
    else:   
        time.sleep(1)    
        server_sl_socket.connect((leader_ip, server_sl_port))
        print("Server sl tcp connected.")
        
        while True:
            last_sent_sl = server_sl_socket.recv(buffer)
            server_list = pickle.loads(last_sent_sl)
            print("received serverlist", server_list)

        
def leader_noleader_cl_tcp():
    
    global leader
    global leader_ip
    global server_cl_connections
    global client_list
    
    
    server_cl_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_cl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
        server_cl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        
                

    if leader == True:

        server_cl_socket.bind((leader_ip, server_cl_port))
        server_cl_socket.listen()
        print("server_cl_socket erstellt")
        
        noleader, noleader_address = server_cl_socket.accept()
        
        #server_tcp_connections.append(noleader)
        server_cl_connections.append(noleader)
        print("CL TCP server connections: {}".format(server_cl_connections))
        
        
        #print("Connected with noleader {}".format(noleader))
        print("Connected with noleader {}".format(noleader_address)) 
    
      
 
    else:   
        time.sleep(1)    
        server_cl_socket.connect((leader_ip, server_cl_port))
        print("Server cl tcp connected.")
        
        while True:
            last_sent_cl = server_cl_socket.recv(buffer)
            client_list = pickle.loads(last_sent_cl)
            print("recieved clientlist", client_list)



def leader_noleader_send_msg(msg):

    global server_msg_connections
    
    for socket in server_msg_connections:
        socket.send(msg.encode("UTF-8"))
    print("last message transfered to noleaders.")

def leader_noleader_send_serverlist():
    
    global server_sl_connections
    global server_list
    
    print(server_list)
    msg = pickle.dumps(server_list)
    print(msg)

    for socket in server_sl_connections:
        socket.send(msg)
    print("serverlist transfered to noleaders.")
        
def leader_noleader_send_clientlist():
    
    global server_cl_connections
    global client_list
    
    msg = pickle.dumps(client_list)

    for socket in server_cl_connections:
        socket.send(msg)
    print("clientlist transfered to noleaders.")

        
        
def ring_formation():
    
    global server_list
    #threading.Timer(10.0, ring_formation).start()
    print("Ring formation started.") 
    sorted_binary_ring = sorted([socket.inet_aton(member) for member in server_list])
    sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
    print(sorted_ip_ring)
    print("Ring formation done")
    get_neighbour(sorted_ip_ring, server_ip, "left")

    

def get_neighbour(ring, own_ip, direction='left'):
    own_ip_index = ring.index(own_ip) if own_ip in ring else -1 
    if own_ip_index != -1:
        if direction == 'left':
            if own_ip_index + 1 == len(ring):
                return ring[0]
                print("I am the only server and therefore my neighbour")
            else:
                left_neighbour = ring[own_ip_index - 1]
                print("My left neighbour is {}".format(left_neighbour))
                right_neighbour = ring[own_ip_index + 1]
                print("My right neighbour is {}".format(right_neighbour))
                return left_neighbour, right_neighbour
        else:
            if own_ip_index == 0: 
                return ring[len(ring) - 1]
            else:
                return ring[own_ip_index - 1] 
    else:
        print("Getting neighbour failed.")
        return None
        


def send_to_neighbour(message):
    print("Send to neighbour")
    send_neighbour_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_list_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #send_neighbour_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
        send_neighbour_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    send_neighbour_socket.bind((server_ip, send_list_port))
    send_neighbour_socket.listen()
    send_neighbour_socket.accept()
    
    send_neighbour_socket.send(message)

    send_neighbour_socket.close()
    
'''def send_server_list_to_neighbour(server_list):
    print("Send server list to neighbour")
    send_server_list_neighbour_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_server_list_neighbour_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_server_list_neighbour_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    send_server_list_neighbour_socket.bind((server_ip, send_list_port))
    send_server_list_neighbour_socket.listen()
    send_server_list_neighbour_socket.accept()
    
    #Serverliste von Leader an alle Noleader
    msg = pickle.dumps(server_list)
    print("Serverliste, die an alle noleader gesendet wird: ", msg)
    send_server_list_neighbour_socket.send(msg)
    print("sent serverlist to new server")
    send_server_list_neighbour_socket.close()'''

#Create UDP socket, listen for broadcast, transmit own address
def client_discovery(): 
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin": 
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) 

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
    
    global client_list
        #TCP connection  
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin": 
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) 
    
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
    client_list.append(client_address)
    client_sockets.append(client)
    leader_noleader_send_clientlist()

    # Benutzername mitteilen und broadcasten
    print("Der Benutzername ist {}".format(nickname))
    broadcast("{} ist dem Blackboard beigetreten!".format(nickname).encode('ascii'))
    client.send('Mit dem Server verbunden!'.encode('ascii'))
    
#Start Handling Thread For Client
    Thread(target=messaging(client, client_address), args=(client, client_address)).start()



def broadcast(message): #um Nachrichten  zu den Clients zu senden
    for client in client_sockets:
        (client).send(message)



def messaging(client, client_address): #Fuer jeden Client auf dem Server wird ein eigener handle aufgerufen in jedem einzelnen Thread
    
    global client_sockets
    global client_list
    
    try:
        message = client.recv(1024).decode("UTF-8")
        if len(message) != 0:
            messages.append(message)
            print(message)
            leader_noleader_send_msg(message)
            broadcast(message.encode("UTF-8")) #Wenn eine Nachricht angekommen ist, wird die Nachricht an die anderen Clients gebroadcastet

            Thread(target=messaging(client, client_address), args=(client, client_address)).start()
        else:
            print("Old client_list: {}".format(client_list))
            index = client_sockets.index(client)
            client_sockets.remove(client) #Client wird von der Clientlist entfernt
            client.close()
            index = client_list.index(client_address)
            client_list.remove(client_address)
            nickname = nicknames[index]
            broadcast(f'{nickname} hat das Blackboard verlassen'.encode('ascii'))
            nicknames.remove(nickname)
            print("New client_list: {}".format(client_list))
            print("client removed")
            

    except: #Sofern der Client keine Nachricht empfaeng
        print("Except.")


if __name__ == "__main__":
    
    server_list = []
    client_list = []
    client_sockets = []
    nicknames = []
    messages = []
    heartbeat_connections = []
    server_msg_connections = []
    server_sl_connections = []
    server_cl_connections = []
    neighbour = 0
    leader = False
    leader_ip = ""
    variable = "Test"
    last_sent_msg = "Welcome!"
    

    service_announcement()
    
    if leader == True:
        print("Lead loop")
        Thread(target=client_discovery, args=()).start()
        Thread(target=server_discovery, args=()).start()

        
    else:
        print("Nolead loop")
        ring_formation()
        Thread(target=leader_noleader_msg_tcp, args=()).start()  
        time.sleep(0.1)
        Thread(target=leader_noleader_sl_tcp, args=()).start()
        time.sleep(0.1)
        Thread(target=leader_noleader_cl_tcp, args=()).start()
        time.sleep(0.1)
        Thread(target=heartbeat, args=()).start()


                
    print(client_list)
    print(nicknames)
    print(messages)

    time.sleep(60)
        
        
#Auf Unix Endgeräten muss erster UDP socket an broadcast IP_binden und bei Windowsgeräten muss erster UDP socket an server_IP biden 

