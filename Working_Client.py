import socket
import socket
import threading
import pickle

broadcast_ip = "192.168.0.255"
udp_serverport = 1234
tcp_serverport = 1235
buffer = 1024

#UDP connection

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

nickname = input("Bitte beliebige Eingabe um Verbindungsaufbau zu starten.")

udp_socket.sendto(str.encode(nickname), (broadcast_ip, udp_serverport))
print("Requesting blackboard entrance.")

host_address = udp_socket.recv(buffer)
print("Hostaddress is {}".format(host_address))

udp_socket.close()

#TCP connection

#source https://www.neuralnine.com/tcp-chat-in-python/
#source https://pymotw.com/2/socket/tcp.html
# Nutzernamen auswaehlen
nickname = input("Wie lautet ihr Benutzername? ")

# Verbindung zum Server
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tcp_socket.connect((host_address, tcp_serverport))
print("TCP connection with server on IP {} established.".format(host_address))


# Dem Server zuhoeren und den Benutzernamen senden
def receive():
    while True:
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = tcp_socket.recv(buffer).decode('ascii')
            if message == 'NICK':
                tcp_socket.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            # Close Connection When Error
            print("Ein Fehler ist aufgetreten!")
            tcp_socket.close()
            break

# Nachrichten zum Server senden
def send():
    while True:
        message = '{}: {}'.format(nickname, input(''))
        tcp_socket.send(message.encode('ascii'))

# 2 Threads fuer Zuhoeren und Nachrichten schreiben starten
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=send)
write_thread.start()

