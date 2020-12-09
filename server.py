import threading
import socket
from multiprocessing import Process, Pipe
from os import getpid
from datetime import datetime
    # Create a TCP/IP socket

# Listening port
BROADCAST_PORT = 5972
# Local host information
MY_HOST = socket.gethostname()
MY_IP = socket.gethostbyname(MY_HOST)
# Create a UDP socket
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Set the socket to broadcast and enable reusing addresses
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Bind socket to address and port
listen_socket.bind((MY_IP, BROADCAST_PORT))
print("Listening to broadcast messages")
while True:
    data, addr = listen_socket.recvfrom(1024)
    if data:
            print("Received broadcast message:", data.decode())

   
    #server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    
    # Enable broadcasting mode
    # server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


        # Bind the socket to the address given on the command line
#server_name = socket.gethostbyname(socket.gethostname())
#server_address = (server_name, 10000)
    
#print('Server gestartet auf %s mit Port %s' % server_address)
#server.bind(server_address)
#server.listen(1)



#Print local Lamport Timestamp
def local_time(counter):
    return ' (LAMPORT_TIME={}, LOCAL_TIME={})'.format(counter,
                                                     datetime.now())
    
#Lamport Event/Message Sending/Recieving Message Definition
def event(pid, counter):
    counter += 1
    print('Something happened in {} !'.\
          format(pid) + local_time(counter))
    return counter

def send_message(pipe, pid, counter):
    counter += 1
    pipe.send(('Empty shell', counter))
    print('Message sent from ' + str(pid) + local_time(counter))
    return counter

def recv_message(pipe, pid, counter):
    message, timestamp = pipe.recv()
    counter = calc_recv_timestamp(timestamp, counter)
    print('Message received at ' + str(pid)  + local_time(counter))
    return counter


clients = []
nicknames = []


def calc_recv_timestamp(recv_time_stamp, counter): #Lamport calculate new timestamp when process recieves a message
    return max(recv_time_stamp, counter) + 1

def broadcast(message): #um Nachrichten  zu den Clients zu senden
    for client in clients:
        client.send(message)
       

def handle(client, pipe21): #Fuer jeden Client auf dem Server wird ein eigener handle aufgerufen in jedem einzelnen Thread
    while True:
        try:
            message = client.recv(1024) #Nachricht empfangen
    
            broadcast(message) #Wenn eine Nachricht angekommen ist, wird die Nachricht an die anderen Clients gebroadcastet
            
            #For Lamport Process Two
            pid = getpid()
            counter = 0
            counter = recv_message(pipe21, pid, counter)
            counter = send_message(pipe21, pid, counter)
        
        except: #Sofern der Client keine Nachricht empfaengt
            index = clients.index(client)
            clients.remove(client) #Client wird von der Clientlist entfernt
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} hat das Blackboard verlassen'.encode('ascii'))
            nicknames.remove(nickname)
            break

def receive(pipe12):
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

        #Start Handling Thread For Client
        #thread = threading.Thread(target=handle, args=(client,))
        #thread.start()     
        
        #For Lamport Process One
        pid = getpid()
        counter = 0
        counter = event(pid, counter)
        counter = send_message(pipe12, pid, counter)
        counter  = event(pid, counter)
        counter = recv_message(pipe12, pid, counter)
        counter  = event(pid, counter)
   

if __name__ == '__main__':
    oneandtwo, twoandone = Pipe()

    receive = Process(target=receive, 
                       args=(oneandtwo,))
    handle = Process(target=handle, 
                       args=(twoandone,))


    receive.start()
    handle.start()

    receive.join()
    handle.join()


  
