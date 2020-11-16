import socket
import select
import errno
import sys
from tkinter import *
from tkinter import messagebox

from threading import Thread

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


def send():
    username = name_input.get()
    message = message_input.get()
    if message == '[exit]':
        message = format_message(username, 'Signing out')
        client_socket.send(message.encode('utf-8'))
        print_message('\nSigned out')
        client_socket.close()
        sys.exit()
    elif message:
        print_message(f'\n{username} > {message}')
        formatted_message = format_message(username, message).encode('utf-8')
        client_socket.send(formatted_message)
        message_input.delete(0, END)


def receive():
    try:
        message_size = client_socket.recv(LENGTH_HEADER_SIZE)
        if message_size: 
            message_size = int(message_size.decode('utf-8').strip())
            sender = client_socket.recv(USER_HEADER_SIZE).decode('utf-8').strip()
            message = client_socket.recv(message_size).decode('utf-8')
            print_message(f'\n{sender} > {message}')
        
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Encountered error while reading', e)
            client_socket.close()
            sys.exit()
    except Exception as e:
        client_socket.close()
        sys.exit()


def print_message(message):
    chat_log.configure(state=NORMAL)
    chat_log.insert(END, message)
    chat_log.configure(state=DISABLED)

    
def loop_receive():
    while True:
        receive()


def lock_username():
    if name_input.get():
        message_input.configure(state=NORMAL)
        send_button.configure(state=NORMAL)
        name_input.configure(state=DISABLED)
    else:
        messagebox.showinfo('Error', 'Please enter a user name!')


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT)) 
client_socket.setblocking(False)

window = Tk(className='Chat program')
name_label = Label(window, text='Name')
name_label.grid(row=0, column=0)

name_input = Entry(window, width=100)
name_input.grid(row=0, column=1)

name_confirm_button = Button(window, width=20, text='Confirm', bg='white', command=lock_username)
name_confirm_button.grid(row=0, column=2)

chat_log = Text(window, width=100, height=20, state=DISABLED)
chat_log.grid(row=1, column=0, columnspan=3)

message_label = Label(window, text='Message')
message_label.grid(row=2, column=0)

message_input = Entry(window, width=100, state=DISABLED)
message_input.grid(row=2, column=1)

send_button = Button(window, width=20, text='Send', bg='white', command=send, state=DISABLED)
send_button.grid(row=2, column=2)

receive_thread = Thread(target=loop_receive)
receive_thread.start()

window.mainloop()
