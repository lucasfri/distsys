import socket
import threading
from threading import Thread
import time
from sys import platform as _platform
import pickle


broadcast_ip = "192.168.0.255"
discovery_port = 1236
send_list_port = 1237
server_msg_port = 1239
server_sl_port = 1240
server_cl_port = 1242
heartbeat_port = 1243
client_heartbeat_port = 1244
udp_port = 1234
tcp_port = 1235 
server_com_port = 1238
buffer = 1024



def get_local_address():
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_address = s.getsockname()[0]
        return local_address
    finally:
        if s:
            s.close()
            
            
            
def service_announcement():
    
    global server_list
    global leader
    global leader_ip
    
    #broadcast socket
    sa_broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sa_broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    #send my information to leader
    data = "%s:%s" % ("SA", server_ip)
    time.sleep(5)
    sa_broadcast_socket.sendto(data.encode("UTF-8"), (broadcast_ip, discovery_port))
    print("Following was broadcasted: ", data)

    #wait for 10 seconds if leader responds
    sa_broadcast_socket.settimeout(10)
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
        print("Server list: ", server_list)

    else: #receive the server list from leader via tcp
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

    #set socket option depending on OS
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin": 
        recv_sa_socket.bind((broadcast_ip, discovery_port))

    elif _platform == "win32" or _platform == "win64":
        recv_sa_socket.bind((server_ip, discovery_port))

    #receive broadcast from new server
    print("listening for new servers")
    sa_message, sa_address = recv_sa_socket.recvfrom(buffer)
    print(sa_message, sa_address)
    
    recv_sa_socket.close()

    #append address of new server to server list
    print("server request received from server on IP {}".format(sa_message))
    located_server_ip = sa_message[3:]
    located_server_ip = located_server_ip.decode("UTF-8")
    server_list.append(located_server_ip)
    print("server list:")
    print(server_list)
    
    #send own address to new server
    send_leader_address_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_leader_address_socket.sendto(server_ip.encode("UTF-8"), sa_address)
    print("Own address sent to new server.")
    send_leader_address_socket.close()
    
    #send server list to new server
    send_list_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_list_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
        send_list_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        
    send_list_socket.bind((server_ip, send_list_port))
    send_list_socket.listen()
    new_server,new_server_address = send_list_socket.accept()
    print("Connected to new server.")

    msg = pickle.dumps(server_list)
    new_server.send(msg)
    print("sent serverlist to new server")
    send_list_socket.close()
    #Serverliste von Leader an alle Noleader
    leader_noleader_send_serverlist()
    
    
    #initiate tcp Threads
    Thread(target=leader_noleader_msg_tcp, args=()).start()
    time.sleep(0.1)
    Thread(target=leader_noleader_sl_tcp, args=()).start()
    time.sleep(0.1)
    Thread(target=leader_noleader_cl_tcp, args=()).start()
    time.sleep(0.1)
    Thread(target=server_heartbeat, args=()).start()
    time.sleep(0.1)    
    Thread(target=server_discovery(), args=()).start()
    
    

def server_heartbeat():
    
    global leader
    global leader_ip
    global server_list
    global stop_threads


    heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    heartbeat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
        heartbeat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
           
    if leader == True:

        heartbeat_socket.bind((leader_ip, heartbeat_port))
        heartbeat_socket.listen()
        noleader, noleader_address = heartbeat_socket.accept()
        print("Heartbeat socket connected")
        
        time.sleep(1)
        noleader.send("Heartbeat started".encode("UTF-8"))
        
        check = noleader.recv(buffer)
        print(check)

        while True:
            ack = noleader.recv(buffer)
            if ack != check:
                print("Old server_list: {}".format(server_list))
                noleader_ip = noleader_address[0]
                server_list.remove(noleader_ip)
                leader_noleader_send_serverlist()
                print("New server_list: {}".format(server_list))
                break
            else:
                print(ack)
                
     
    else:
        time.sleep(1)
        heartbeat_socket.connect((leader_ip, heartbeat_port))
        print("Heartbeat socket connected.")
        ack2 = heartbeat_socket.recv(buffer).decode("UTF-8")
        print(ack2)
            
        while True:
            try:
                heartbeat_socket.send(server_ip.encode("UTF-8"))
                print("heartbeat sent to leader")

            except:
                print("Connection to leader lost")
                server_list.remove(leader_ip)
                stop_threads = True
                ring_formation()
                break
            
            time.sleep(10)
            
        heartbeat_socket.close()
        
        
def client_heartbeat():
    
    global leader
    global leader_ip
    global client_list
    global stop_threads


    client_heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_heartbeat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
        client_heartbeat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    client_heartbeat_socket.bind((leader_ip, client_heartbeat_port))
    client_heartbeat_socket.listen()
    client, client_address = client_heartbeat_socket.accept()
    print("client heartbeat socket connected")

    client.send("Client heartbeat started".encode("UTF-8"))
    
    check = client.recv(buffer)
    print(check)


    while True:
        ack = client.recv(buffer)
        if ack != check:
            print("Old client_list: {}".format(client_list))
            client_ip = client_address[0]
            client_list.remove(client_ip)
            leader_noleader_send_clientlist()
            client.close()
            print("New client_list: {}".format(client_list))
            break
        else:
            print(ack)
            
    client_heartbeat_socket.close()       



def leader_noleader_msg_tcp():
    
    global leader
    global leader_ip
    global server_msg_connections
    global messages
    global stop_threads
    
    
    server_msg_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_msg_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
        server_msg_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        
    
    if leader == True:

        server_msg_socket.bind((leader_ip, server_msg_port))
        server_msg_socket.listen()
        noleader, noleader_address = server_msg_socket.accept()
        
        noleader_ip = noleader_address[0]
        server_msg_connections.append(noleader)
        print("Messsage TCP server connections: {}".format(server_msg_connections))
        print("Message transfer established with noleader {}".format(noleader_address)) 
        
          
     
    else:
        time.sleep(1)
        server_msg_socket.connect((leader_ip, server_msg_port))
        print("Message transfer establsihed with leader")
                    
        while True:
            if stop_threads == True: break
            else:
                last_sent_msg = server_msg_socket.recv(buffer).decode("UTF-8")
                if len(last_sent_msg) != 0:
                    messages.append(last_sent_msg)
                    print(last_sent_msg)
            

        server_msg_socket.close()


    
def leader_noleader_sl_tcp():
    
    global leader
    global leader_ip
    global server_sl_connections
    global stop_threads
    global server_list
    
    server_sl_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
        server_sl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        

    if leader == True:

        server_sl_socket.bind((leader_ip, server_sl_port))
        server_sl_socket.listen()
        noleader, noleader_address = server_sl_socket.accept()

        server_sl_connections.append(noleader)
        print("Server list TCP connections: {}".format(server_sl_connections))
        print("Serverlist transfer established with noleader {}".format(noleader_address)) 
    
      
 
    else:   
        time.sleep(1)    
        server_sl_socket.connect((leader_ip, server_sl_port))
        print("server list transfer establsihed with leader.")
        
        while True:
            if stop_threads ==  True: break
            else:    
                try:
                    last_sent_sl = server_sl_socket.recv(buffer)
                    try:
                        server_list = pickle.loads(last_sent_sl)
                        print("received serverlist: ", server_list)
                    except: continue
                except: continue
            
        server_sl_socket.close()    
        
        
        
def leader_noleader_cl_tcp():
    
    global leader
    global leader_ip
    global server_cl_connections
    global client_list
    global stop_threads
    
    
    server_cl_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_cl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
        server_cl_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        
                

    if leader == True:

        server_cl_socket.bind((leader_ip, server_cl_port))
        server_cl_socket.listen()    
        noleader, noleader_address = server_cl_socket.accept()
        
        server_cl_connections.append(noleader)
        print("Client list TCP connections: {}".format(server_cl_connections))
        print("Client list transfer established with noleader {}".format(noleader_address)) 
    
      
 
    else:   
        time.sleep(1)    
        server_cl_socket.connect((leader_ip, server_cl_port))
        print("Client list transfer established with leader")
        
        while True:
            if stop_threads == True: 
                break
            else:
                try:
                    last_sent_cl = server_cl_socket.recv(buffer)
                    try:
                        client_list = pickle.loads(last_sent_cl)
                        print("Recieved clientlist: ", client_list)
                    except:continue
                except: continue

        server_cl_socket.close()
        
        
    
def leader_noleader_send_msg(msg):

    global server_msg_connections
    
    for socket in server_msg_connections:
        try:
            socket.send(msg.encode("UTF-8"))
        except: continue
    print("last message transfered to noleaders.")


def leader_noleader_send_serverlist():
    
    global server_sl_connections
    global server_list
    
    print(server_list)
    msg = pickle.dumps(server_list)
    print(msg)

    for socket in server_sl_connections:
        try:
            socket.send(msg)
        except:
            continue
    print("server list transfered to noleaders.")
        
        
def leader_noleader_send_clientlist():
    
    global server_cl_connections
    global client_list
    
    msg = pickle.dumps(client_list)

    for socket in server_cl_connections:
        try:
            socket.send(msg)
        except: continue
    print("client list transfered to noleaders.")

        
        
def ring_formation():
    
    global server_list

    print("Ring formation started.") 
    sorted_binary_ring = sorted([socket.inet_aton(member) for member in server_list])
    sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
    
    print(sorted_ip_ring)
    print("Ring formation done")
    
    get_neighbour(sorted_ip_ring, "left")
    leader_election(sorted_ip_ring)
    
    

def leader_election(sorted_ip_ring):
    global server_ip
    global leader
    global leader_ip
    
    if sorted_ip_ring[0] == server_ip:
        leader = True
        leader_ip = server_ip
        server_list = []
        server_list.append(server_ip)
        print("I am the new leader")
        
        Thread(target=client_discovery, args=()).start()
        Thread(target=server_discovery, args=()).start()
   
    else: 
        leader_ip = ""
        service_announcement()
        print("Waiting for new leader to boot")
        time.sleep(10)
        print("Nolead loop")
        #ring_formation()
        Thread(target=leader_noleader_msg_tcp, args=()).start()  
        time.sleep(0.1)
        Thread(target=leader_noleader_sl_tcp, args=()).start()
        time.sleep(0.1)
        Thread(target=leader_noleader_cl_tcp, args=()).start()
        time.sleep(0.1)
        Thread(target=server_heartbeat, args=()).start()

        

def get_neighbour(ring, direction='left'):
    
    global server_ip
    own_ip_index = ring.index(server_ip) if server_ip in ring else -1 
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
    
    

def recv_from_neighbour():
    print("recv_from_neighbour")



def client_discovery(): 
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin": 
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) 

    if _platform == "linux" or _platform == "linux2" or _platform == "darwin": 
        udp_socket.bind((broadcast_ip, udp_port))
        
    elif _platform == "win32" or _platform == "win64":
        udp_socket.bind((server_ip, udp_port))

    
    print("server up and running...")
    print("Waiting for client request...") 
       
    request, client_address = udp_socket.recvfrom(buffer)
    print("client request received from client on IP {}".format(client_address))
        
    udp_socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    udp_socket2.bind((server_ip, udp_port))
    
    udp_socket2.sendto(str.encode(server_ip), client_address)
    
    #Initialising the TCP connections
    Thread(target=client_heartbeat, args=()).start()
    Thread(target=client_discovery, args=()).start()
    Thread(target=connect, args=()).start()



def connect():

    global client_list

    print("Establishing TCP connection.")
    client_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin": 
        client_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) 
    
    
    server_address = (server_ip, tcp_port)
    print('Server started on IP %s and port %s' % server_address)
    client_tcp.bind(server_address)
    client_tcp.listen()
    client,client_address = client_tcp.accept()
    print("Connected to client {}".format(str(client_address)))

    # Request Username
    client.send('NICK'.encode('ascii'))
    nickname = client.recv(1024).decode('ascii')
    client_ip = client_address[0]
    client_list.append(client_ip)
    client_sockets.append(client)
    leader_noleader_send_clientlist()

    # Benutzername mitteilen und broadcasten
    print("Username: {}".format(nickname))
    multicast("{} entered the blackboard!".format(nickname).encode('ascii'))
    client.send('Connected to server!'.encode('ascii'))
    
    
    blackboard_history_transfer(client)
    Thread(target=messaging(client, client_address), args=(client, client_address)).start()
    
    

def blackboard_history_transfer(client):
    
    for message in messages:
            client.send(("\n" + message).encode("UTF-8"))
    print("blackboard history transfered.")
            
            
            
def multicast(message):
    for client in client_sockets:
        try:
            (client).send(message)
        except:
            continue
    print("message sent to all clients.")



def messaging(client, client_address):
    
    global client_list
    
    try:
        message = client.recv(1024).decode("UTF-8")
        if len(message) != 0:
            messages.append(message)
            print(message)
            leader_noleader_send_msg(message)
            multicast(message.encode("UTF-8"))

            Thread(target=messaging(client, client_address), args=(client, client_address)).start()
        
        else:
            print("message transfer with client interrupted")
            

    except:
        print("")



if __name__ == "__main__":
    
    server_ip = get_local_address()
    server_list = []
    client_list = []
    client_sockets = []
    messages = []
    server_msg_connections = []
    server_sl_connections = []
    server_cl_connections = []
    neighbour = 0
    leader = False
    leader_ip = ""
    last_sent_msg = "Message TCP"
    stop_threads = False
    

    service_announcement()
    
    if leader == True:
        print("Lead loop")
        Thread(target=client_discovery, args=()).start()
        Thread(target=server_discovery, args=()).start()

    else:
        print("Nolead loop")
        Thread(target=leader_noleader_msg_tcp, args=()).start()  
        time.sleep(0.1)
        Thread(target=leader_noleader_sl_tcp, args=()).start()
        time.sleep(0.1)
        Thread(target=leader_noleader_cl_tcp, args=()).start()
        time.sleep(0.1)
        Thread(target=server_heartbeat, args=()).start()

