import socket
broadcast_address = "192.168.0.220"
udp_serverport = 1234
tcp_serverport = 1235
buffer = 1024


#UDP connection
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_name = input("Ihr Name?")


udp_socket.sendto(str.encode(client_name), (broadcast_address, udp_serverport))
print("Requesting blackboard entrance.")

host_address = udp_socket.recv(buffer)
print("Hostaddress is {}".format(host_address))

udp_socket.close()


#TCP connection

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.connect((host_address, tcp_serverport))

#est = tcp_socket.recv(buffer)
#print(est)

#if est == "Connection established." :
    #receive last 10 messages
new_entry = input("Eintrag hinzufügen:")
tcp_socket.send(str.encode(new_entry))