import socket
from threading import Thread
import pickle
import time
from sys import platform as _platform



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
            
            

#send udp broadcast and wait for answer from leader
def udp():
    
    global host_address
    
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    while len(host_address) == 0:
        try:    
            udp_socket.sendto(str.encode("Hello server."), (broadcast_ip, udp_serverport))
            print("Requesting blackboard entrance.")
            
            try: 
                udp_socket.settimeout(10)
                host_address = udp_socket.recv(buffer)
                print("Hostaddress is {}".format(host_address))
                
            except socket.timeout as e:continue
         
        except: print("")
          
    udp_socket.close()
    
    tcp()
    


#Connect with lead server which was identified via udp()
def tcp():
    
    global tcp_socket
    global nickname
    
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
    time.sleep(1)
    tcp_socket.connect((host_address, tcp_serverport))
    print("TCP connection with server on IP {} established.".format(host_address))
    
    #tcp_sockets.append(tcp_socket)
    
    Thread(target=heartbeat, args=()).start()
    time.sleep(2)
    Thread(target=receive, args=()).start()
    time.sleep(2)
    Thread(target=send, args=()).start()
    
    
       
#receive messages from lead server
def receive():

    global tcp_socket
    global nickname
    
    while True:
        if stop_threads ==  True: break
        else:
            #for element in tcp_sockets:
            message = tcp_socket.recv(buffer).decode('ascii')
            if message == 'NICK':
                tcp_socket.send(nickname.encode('ascii'))
            else:
                if len(message) != 0:
                    print(message)
            
            

# Send user input to lead server
def send():
    global stop_threads
    global tcp_socket
    
    while True:
        if stop_threads ==  True: break
        else:
            try:
                #for element in tcp_sockets:
                print("Enter message:")
                message = '{}: {}'.format(nickname, input(''))
                tcp_socket.send(message.encode('ascii'))
            except:
                print("Connection to Leader lost. Please try again.")
                stop_threads = True
                time.sleep(3)
                #tcp_socket = ""
                udp()
                break

            
 
#send heartbeat pings to say i'm up and running       
def heartbeat():   

    global host_address
    global client_ip
    global tcp_socket
    
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
            tcp_socket.close()
            #tcp_sockets = ""
            stop_threads = True
            time.sleep(3)
            udp()
            break
        time.sleep(10)
        
        
    heartbeat_socket.close()
    



if __name__ == "__main__":
    
    broadcast_ip = "192.168.0.255"
    client_ip = get_local_address()
    udp_serverport = 1234
    tcp_serverport = 1235
    heartbeat_port = 1244
    buffer = 1024
    host_address = ""
    stop_threads = False
    nickname = ""

    nickname = input("Enter username:")
    
    udp()


#heartbeat time.sleep
#multicast -->
# tcp_sockets zu Variable
