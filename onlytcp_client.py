import socket
import threading
import sys
#source https://www.neuralnine.com/tcp-chat-in-python/
#source https://pymotw.com/2/socket/tcp.html
# Nutzernamen auswaehlen
nickname = input("Wie lautet ihr Benutzername? ")

# Verbindung zum Server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("192.168.0.220", 10000)
print('Verbindung mit dem Blackboard auf %s mit Port %s herstellen' % server_address)

sock.connect(server_address)

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