import socket
import sys
import select

def displayServerMessage(message):
    message = message.decode("utf-8").strip()

    if (message.startswith("SEND-OK")):
        print("(Message send)")
    
    elif (message.startswith("DELIVERY")):
        message = message[9:]
        gapIndex = message.index(" ")
        message = message[:gapIndex]+":"+message[gapIndex:]
        print(message)
    
    elif (message.startswith("WHO-OK")):
        message = "Online users:"+message[6:]
        print(message)
    
    elif (message.startswith("UNKNOWN")):
        print("Message delivery failed! The user is offline.")
    
    else:
        print(message)

helpMessage = """Available commands: 
    !quit: Exits the program.
    !help: Displays this help message.
    !who: Displays all currently logged-in users
    @<username> <message>: Sends a message to the specified user. """

host = ("18.195.107.195",5378)
print("\n*** Welcome to the chat client ***\n")

''' Login Loop
Asks the user to pick the username and checks if the username is already in user or not.
If the username is already in use we ask the user for another one, until he enters a valid one.
'''
while True:
    clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    try:
        clientSocket.connect(host)
    except OSError:
        print("Unreachable network. Please check your internet connection and try again.\n")
        sys.exit()

    print("Choose a username, or enter !quit to exit the program.")
    username = input("Username: ")
    if (username == "!quit"):
        clientSocket.close()
        sys.exit()

    message = ("HELLO-FROM {0}\n".format(username)).encode("utf-8")
    clientSocket.sendall(message)

    serverMessage = (clientSocket.recv(4096)).decode("utf-8")
    if (serverMessage.startswith("IN-USE")):
        clientSocket.close()
        print("\nUsername already in use, please choose another one.")

    elif (serverMessage.startswith("BUSY")):
        print("The server is busy. Please try again in few minutes.\n")
        clientSocket.close()
        sys.exit()
        
    else:
        print('\nSuccesful login.\nHello {0}! If you do not know what to do, type "!help"'.format(username))
        break

inputStreams = [sys.stdin,clientSocket]
serverMessage = bytes()

''' Main Loop
All the functionality of the client is here. The user recieved messages from the server and can interact
with the server though the appropriate commands.
'''
while True:
    
    readStreams,writeStreams,errorStreams = select.select(inputStreams,[],[])

    for inputStream in readStreams:
        if inputStream == clientSocket: # Message from server
            try:
                recievedBytes = clientSocket.recv(2)
                serverMessage = serverMessage + recievedBytes
                if(serverMessage.decode().endswith("\n")):
                    displayServerMessage(serverMessage)
                    serverMessage = bytes() #Reset serverMessage contents for the next message from the server     
            except TimeoutError:
                print("Unreachable network. Please check your internet connection and try again.\n")
                sys.exit()

        else: # User Input
            command = sys.stdin.readline().strip()
            if (command == "!quit"):
                clientSocket.close()
                sys.exit()
            
            elif (command == "!who"):
                message = "WHO\n".encode("utf-8")
                clientSocket.sendall(message)
            
            elif (command.startswith("@")):
                command = command[1:]
                try: 
                    (user, chatMessage) = command.split(maxsplit=1)
                except ValueError:
                    print("Invalid command syntax. To send a message you have to use the following syntax: \n @<username> <message>")
                    continue
                
                message = ("SEND {0} {1}\n".format(user,chatMessage)).encode("utf-8")
                clientSocket.sendall(message)

                # Recieve the "SENT-OK" (or the "UNKNOWN") response"
                while True:
                    try:
                        recievedBytes = clientSocket.recv(2)
                        serverMessage = serverMessage + recievedBytes
                        if(serverMessage.decode().endswith("\n")):
                            displayServerMessage(serverMessage)
                            serverMessage = bytes() #Reset serverMessage contents for the next message from the server
                            break
                    except TimeoutError:
                        print("Unreachable network. Please check your internet connection and try again.\n")
                        sys.exit()

            elif (command == "!help"):
                print(helpMessage)
            
            else:
                print("Invalid command")
