import socket
from threading import Thread
import pickle
import time
from sys import platform as _platform




# Dem Server zuhoeren und den Benutzernamen senden

def udp():
    
    global host_address
    
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    while len(host_address) == 0:
        try:    
            udp_socket.sendto(str.encode("Hello Server"), (broadcast_ip, udp_serverport))
            print("Requesting blackboard entrance.")
            
            try: 
                udp_socket.settimeout(10)
                host_address = udp_socket.recv(buffer)
                print("Hostaddress is {}".format(host_address))
                
            except socket.timeout as e:continue
         
        except: print("None")
          
    udp_socket.close()
    
    tcp()
    

def tcp():
    
    global tcp_sockets
    global nickname
    
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    tcp_socket.connect((host_address, tcp_serverport))
    print("TCP connection with server on IP {} established.".format(host_address))
    
    tcp_sockets.append(tcp_socket)
    
    Thread(target=heartbeat, args=()).start()
    time.sleep(2)
    Thread(target=receive, args=()).start()
    time.sleep(2)
    Thread(target=send, args=()).start()
    
    
       
    
def receive():

    global tcp_sockets
    global nickname
    
    while True:
        if stop_threads ==  True: break
        else:
            for element in tcp_sockets:
                #try:
                    # Receive Message From Server
                    # If 'NICK' Send Nickname
                message = element.recv(buffer).decode('ascii')
                if message == 'NICK':
                    element.send(nickname.encode('ascii'))
                else:
                    if len(message) != 0:
                        print(message)
                #except:
                    # Close Connection When Error
                 #   print("Ein Fehler ist aufgetreten!")
                  #  element.close()
                   # break
            
            

# Nachrichten zum Server senden
def send():
    global stop_threads
    global tcp_sockets
    while True:
        if stop_threads ==  True: break
        else:
            try:
                for element in tcp_sockets:
                    print("Enter message:")
                    message = '{}: {}'.format(nickname, input(''))
                    element.send(message.encode('ascii'))
            except:
                print("Connection to Leader lost. Please try again.")
                stop_threads = True
                time.sleep(3)
                udp()
                break

            
        
def heartbeat():   

    global host_address
    global client_ip
    global tcp_sockets
    
    heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    heartbeat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if _platform == "linux" or _platform == "linux2" or _platform == "darwin":
        heartbeat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        

    time.sleep(1)
    heartbeat_socket.connect((host_address, heartbeat_port))
    print("Heartbeat TCP connected.")
    ack2 = heartbeat_socket.recv(buffer).decode("UTF-8")
    print(ack2)
        
    while True:
        try:
            heartbeat_socket.send(client_ip.encode("UTF-8"))
            print("heartbeat sent to leader")

        except:
            print("Connection to Leader lost")
            host_address = ""
            tcp_sockets = []
            stop_threads = True
            time.sleep(3)
            udp()
            break
        time.sleep(10)
        
        
    heartbeat_socket.close()
    

if __name__ == "__main__":
    
    broadcast_ip = "192.168.56.255"
    client_ip = "192.168.56.102"
    udp_serverport = 1234
    tcp_serverport = 1235
    heartbeat_port = 1244
    buffer = 1024
    host_address = ""
    stop_threads = False
    tcp_sockets = []
    nickname = ""
#Start loop

    nickname = input("Wie lautet ihr Benutzername? ")
    
    udp()

    
    #source https://www.neuralnine.com/tcp-chat-in-python/
    #source https://pymotw.com/2/socket/tcp.html
    # Nutzernamen auswaehlen.


