import socket          
import threading

def on_new_client(clientSocket,address):
    clientMessage = bytes()
    username = ""

    while True:
        recievedBytes = clientSocket.recv(4096)
        if not (recievedBytes):
            try:
                del clientDict[username]
            except KeyError:
                pass
            
            clientSocket.close()
            break
    
        if(len(recievedBytes) < 4096):
            if not recievedBytes.decode("utf-8").endswith("\n"):
                clientMessage = bytes()
                response = ("BAD-RQST-BODY\n").encode("utf-8")
                clientSocket.sendall(response)

        clientMessage = clientMessage + recievedBytes

        if(clientMessage.decode("utf-8").endswith("\n")):
            clientMessage = clientMessage.decode("utf-8")
            print (address, ' >> ', clientMessage)

            if(clientMessage):
                if(clientMessage.startswith("HELLO-FROM")):
                    username = clientMessage[11:].strip()
                    if not username in clientDict:
                        clientDict[username] = clientSocket
                        response = ("HELLO " + username + "\n").encode("utf-8")
                        clientSocket.sendall(response)
                    else:
                        response = ("IN-USE\n").encode("utf-8")
                        clientSocket.sendall(response)
                        clientSocket.close()
                        break
                
                elif(clientMessage.startswith("WHO")):
                    userList = ""
                    for client in clientDict:
                        userList += (client + ", ")
                    userList = userList[:len(userList) - 2] + "\n"
                    response = ("WHO-OK " + userList).encode("utf-8")
                    clientSocket.sendall(response)
                
                elif(clientMessage.startswith("SEND")):
                    clientMessage = clientMessage[4:].strip()
                    gapIndex = clientMessage.index(" ")
                    receiver = clientMessage[:gapIndex]
                    print("DELIVERY " + username + clientMessage[gapIndex:]) #send this clientMessage to the intended user

                    if receiver in clientDict:
                        receiverSocket = clientDict[receiver]
                        if(receiverSocket.sendall(("DELIVERY " + username + clientMessage[gapIndex:] + "\n").encode("utf-8")) == None):
                            #this checks if the clientMessage was sent succesfully
                            clientSocket.sendall(("SEND-OK \n").encode("utf-8")) 
                    else:
                        print("user not found")
                        response = ("UNKNOWN\n").encode("utf-8")
                        clientSocket.sendall(response)
                else:
                    response = ("BAD-RQST-HDR\n").encode("utf-8")
                    clientSocket.sendall(response)
                clientMessage = bytes()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1) 
host = "127.0.0.1" # Get local machine name
port = 5378        # Reserve a port for service.

print('Server started!')
print('Waiting for clients...')

clientDict = dict()

sock.bind((host, port))        # Bind to the port
sock.listen(5)                 # Now wait for client connection.

while True:
        clientSocket, address = sock.accept()     # Establish connection with client.
        print ('Got connection from', address)
        if (len(clientDict) < 81):
            threading.Thread(target=on_new_client, args=(clientSocket,address), daemon=True).start()
        else:
            clientSocket.sendall(("BUSY\n").encode("utf-8"))
            clientSocket.close()
        
sock.close()


