# Distributed Blackboard

This is a distributed blackboard project of the course "Distributed Systems" at Herman Hollerith Zentrum Reutlingen for the winter semester 2020/2021.
# Files
The Blackboard consists of one client and one server file. Inside the python files, one has to change the broadcast address to the one of their own network (broadcast_ip in client.py and server.py).
# Functionality
After starting a server, several other servers can be started which will be connecting to the lead server and act as no leader. Those servers act as a backup in case of crash of the lead server.
When starting client.py, it is connecting to the lead server and can interact with other Blackboard participants exchanging messages

# Common errors

### ConnectionRefusedError: [Errno 111] Connection refused #21
Please start the program code again.
### Writing of messages is not possible anymore
Please restart your client.py. Don't worry, old messages already transferred to the server are saved.
