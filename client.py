import socket
#import threading

#source https://www.neuralnine.com/tcp-chat-in-python/
#source https://pymotw.com/2/socket/tcp.html
# Nutzernamen auswaehlen
#nickname = input("Wie lautet ihr Benutzername? ")
#gjhgjh
# Verbindung zum Server
def broadcast(ip, port):
    # Create a UDP socket
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Send message on broadcast address
    while True:
        broadcast_socket.sendto(str.encode(MY_IP), (ip, port))
        print("Sending ", str.encode(MY_IP))
   # broadcast_socket.close()
    


#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_address = (sys.argv[1], 10000)
#print('Verbindung mit dem Blackboard auf %s mit Port %s herstellen' % server_address)

#sock.connect(server_address)

# Dem Server zuhoeren und den Benutzernamen senden
#def receive():
    
   # while True:
      #  try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
     #       message = broadcast_socket.recv(1024).decode('ascii')
    #        if message == 'NICK':
   #             broadcast_socket.send(nickname.encode('ascii'))
  #          else:
 #               print(message)
#        except:
#            # Close Connection When Error
#            print("Ein Fehler ist aufgetreten!")
#            broadcast_socket.close()
#            break
#
        
# Nachrichten zum Server senden
#def write():
 #   while True:
  #      message = '{}: {}'.format(nickname, input(''))
   #     broadcast_socket.send(message.encode('ascii'))
        
# 2 Threads fuer Zuhoeren und Nachrichten schreiben starten
#receive_thread = threading.Thread(target=receive)
#receive_thread.start()

#write_thread = threading.Thread(target=write)
#write_thread.start()


if __name__ == '__main__':
    # Broadcast address and port
    BROADCAST_IP = "192.168.2.255"
    BROADCAST_PORT = 5973

    # Local host information
    MY_HOST = socket.gethostname()
    MY_IP = socket.gethostbyname(MY_HOST)
    # Send broadcast message
    broadcast(BROADCAST_IP, BROADCAST_PORT)
    

