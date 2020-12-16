import socket
broadcast_address = "192.168.0.220"
udp_serverport = 1234
tcp_serverport = 1235
buffer = 1024

#UDP connection
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

nickname = input("Ihr Name?")


udp_socket.sendto(str.encode(nickname), (broadcast_address, udp_serverport))
print("Requesting blackboard entrance.")

host_address = udp_socket.recv(buffer)
print("Hostaddress is {}".format(host_address))

udp_socket.close()

#TCP connection

import socket
import threading
import sys
#source https://www.neuralnine.com/tcp-chat-in-python/
#source https://pymotw.com/2/socket/tcp.html
# Nutzernamen auswaehlen
nickname = input("Wie lautet ihr Benutzername? ")

# Verbindung zum Server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_address = ("172.29.180.18", 10000)
#print('Verbindung mit dem Blackboard auf %s mit Port %s herstellen' % host_address)

sock.connect((host_address, tcp_serverport))

# Dem Server zuhoeren und den Benutzernamen senden
def receive():
    while True:
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = sock.recv(1024).decode('ascii')
            if message == 'NICK':
                sock.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            # Close Connection When Error
            print("Ein Fehler ist aufgetreten!")
            sock.close()
            break
        
# Nachrichten zum Server senden
def write():
    while True:
        message = '{}: {}'.format(nickname, input(''))
        sock.send(message.encode('ascii'))
        
# 2 Threads fuer Zuhoeren und Nachrichten schreiben starten
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
    
