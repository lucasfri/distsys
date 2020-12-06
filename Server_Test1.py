
import socket
buffer = 1024
clientdict = {}


#UDP connection

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(("192.168.0.220", 1234))

print("server up and running...")

#while True:
print("Waiting for client request...")
client_name, client_address = udp_socket.recvfrom(buffer)
clientdict[client_address] = client_name
print("client request received from client {} on IP {}".format(client_name, client_address))
print("Establishing connection")
    
udp_socket.sendto(str.encode("192.168.0.220"), client_address)
    
  
#TCP connection  
    
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    
    # Enable broadcasting mode
tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
tcp_socket.bind(("192.168.0.220", 1235))
tcp_socket.listen()
print("Check")

tcp_socket.accept()
#tcp_socket.send(str.encode("Connection established.")
print("Connection established.")


#while :
sender, entry = tcp_socket.recvfrom(buffer)
tcp_socket.sendto("{} wrote: {}".format(clientdict[sender], entry), clientdict.keys()) #sollte das funktionieren dann nur für einen Client im dictionary

    
