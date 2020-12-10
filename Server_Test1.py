
import socket
buffer = 1024
clientdict = {}
bind_address = "192.168.2.85"

#UDP connection

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((bind_address, 1023))


udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    
    # Enable broadcasting mode
#udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

print("Server up and running...")

#while True:
print("Waiting for client request... on {}".format(bind_address))

  
while True:
    print("empfangen laeuft")
    data, addr = udp_socket.recv(1024)
    print("Message: ", data)

#client_name, client_address = udp_socket.recvfrom(buffer)
#clientdict[client_address] = client_name

#print("client request received from client {} on IP {}".format(client_name, client_address))
#print("Establishing connection")
    
#udp_socket.sendto(str.encode(bind_address), client_address) #hier muss noch der port mitgeschickt werden!

#udp_socket.close()  #Ansonsten errno 48: address already in use
  

#TCP connection  
    
#tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
#tcp_socket.bind(("192.168.0.221", 1235))
#tcp_socket.listen()

#tcp_socket.accept()
#tcp_socket.send(str.encode("Connection established.")
print("Connection established.")

#sender, entry = tcp_socket.recv(buffer)
#tcp_socket.sendto("{} wrote: {}".format(clientdict[sender], entry), clientdict.keys()) #sollte das funktionieren dann nur für einen Client im dictionary

  
