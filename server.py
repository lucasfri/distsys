'''
Created on 16.11.2020

@author: lucas.fritzsche
'''

import select
import socket

LENGTH_HEADER_SIZE = 8
USER_HEADER_SIZE = 16


def format_message(username, message):
    if not message:
        return None
    length_header = f'{len(message):<{LENGTH_HEADER_SIZE}}'
    user_header = f'{username:<{USER_HEADER_SIZE}}'
    return f'{length_header}{user_header}{message}'


IP = '127.0.0.1'
PORT = 5555

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, PORT))
server_socket.listen(10)
print (f'Listening on {IP}:{PORT}')
all_sockets = [server_socket]


def receive(client_socket):
    size_header = client_socket.recv(LENGTH_HEADER_SIZE)
    if not size_header:
        return None
    size_header = size_header.decode('utf-8')
    message_size = int(size_header.strip())

    user_header = client_socket.recv(USER_HEADER_SIZE).decode('utf-8')
    user = user_header.strip()        
    message = client_socket.recv(message_size).decode('utf-8')
    print (f'{user} > {message}')    
    return f'{size_header}{user_header}{message}'


def broadcast(sender, message):
    for socket in all_sockets: 
        if socket != sender and socket != server_socket: 
            socket.send(message.encode('utf-8'))

            
while True:
    read_sockets, _, error_sockets = select.select(all_sockets, [], all_sockets)        
    for socket in read_sockets:
        if socket == server_socket: 
            client_socket, client_address = server_socket.accept()            
            all_sockets.append(client_socket)
            print(f'Established connection to {client_address[0]}:{client_address[1]}')
        else:
            try:
                message = receive(socket)
                if not message:
                    print(f'{client_socket.getpeername()[0]}:{client_socket.getpeername()[1]} closed the connection')
                    all_sockets.remove(socket)
                    continue
                broadcast(socket, message)
            except ConnectionResetError as e:
                all_sockets.remove(socket)
                print('Client forcefully closed the connection')

    for error_socket in error_sockets:
        all_sockets.remove(error_socket)
