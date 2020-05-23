import socket          
import threading

def on_new_client(clientSocket,address):
    clientMessages = bytes()
    username = ""
    isRunning = True
    hasHandshake = False

    while isRunning:
        recievedBytes = clientSocket.recv(2)
        #we used a buffer size of 2 bytes to prove that our protocol 
        #works even if the original packet is split into multiple messages
        if not (recievedBytes): # User Disconnected
            try:
                del clientDict[username]
            except KeyError:
                pass
            clientSocket.close()
            break

        clientMessages = clientMessages + recievedBytes
        if(clientMessages.decode("utf-8").endswith("\n")):
            clientMessages = clientMessages.decode("utf-8")
            messagesArray = clientMessages.strip().split("\n")
            
            for clientMessage in messagesArray:
                clientMessage = clientMessage.strip()

                if not hasHandshake:
                    if(clientMessage.startswith("HELLO-FROM") ):
                        username = clientMessage[11:].strip()
                        
                        if not username in clientDict:
                            clientDict[username] = clientSocket
                            response = ("HELLO " + username + "\n").encode("utf-8")
                            hasHandshake = True
                        else:
                            clientSocket.sendall(("IN-USE\n").encode("utf-8"))
                            clientSocket.close()
                            isRunning = False
                            break
                    else:
                        response = "BAD-RQST-HDR\n".encode("utf-8")
                        clientSocket.sendall(response)
                    
                if(clientMessage.startswith("WHO")):
                    userList = ""
                    for client in clientDict:
                        userList += (client + ", ")
                    userList = userList[:len(userList) - 2] + "\n"
                    response = ("WHO-OK " + userList).encode("utf-8")
                    
                elif(clientMessage.startswith("SEND")):
                    clientMessage = clientMessage[4:].strip()
                    try:
                        (receiver, clientMessage) = clientMessage.split(maxsplit=1)
                    except ValueError:
                        receiver = clientMessage
                        clientMessage = ""

                    if receiver in clientDict:
                        if not clientMessage:
                            response = "BAD-RQST-BODY\n".encode("utf-8")
                        else:
                            receiverSocket = clientDict[receiver]
                            message = ("DELIVERY " + username +" "+clientMessage + "\n").encode("utf-8")
                            try: 
                                receiverSocket.sendall(message)
                                response = "SEND-OK\n".encode("utf-8")
                            except OSError: 
                                response = "UNKNOWN\n".encode("utf-8")
                    else:
                        response = "UNKNOWN\n".encode("utf-8")
                else:
                    response = "BAD-RQST-HDR\n".encode("utf-8")
                
                clientSocket.sendall(response)
                clientMessages = bytes()


''' TCP server setup '''
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1) 
host = "127.0.0.1"
port = 5378 

sock.bind((host, port))
sock.listen(5)

clientDict = dict() # Dictionary to store all the clients usernames and addresses

''' Main loop: Accepts connection from clients. Each client has its own thread.
    Maximum amount of connections is 81. '''
while True:
    clientSocket, address = sock.accept()
    if (len(clientDict) < 81):
        threading.Thread(target=on_new_client, args=(clientSocket,address), daemon=True).start()
    else:
        clientSocket.sendall(("BUSY\n").encode("utf-8"))
        clientSocket.close()
