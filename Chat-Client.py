import socket
import threading
import sys

def clientReceive():
    while True:
        response = sock.recv(4096).decode("utf-8")
        print(response)
        if(response):
            if(response.startswith("DELIVERY")):
                response = response[9:].strip()
                gapIndex = response.index(" ")
                print(response[:gapIndex] + ": " + response[gapIndex:])

            elif(response.startswith("WHO-OK")):
                response = response[7:].strip()
                print("Online users: " + response)
            elif(response.startswith("SEND-OK")):
                print("(message has been sent)")
            elif (response.startswith("UNKNOWN")):
                print("Message delivery failed! The user is offline.")
            else:
                print(response.strip())



host_port = ("18.195.107.195", 5378)


while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect(host_port)
    except OSError:
        print("Unreachable network. Please check your internet connection and try again")
        sock.close()
        sys.exit()

    username = input("Please enter a username: ")
    message = ("HELLO-FROM " + username + "\n").encode("utf-8")
    sock.sendall(message)

    response = sock.recv(4096).decode("utf-8")
    if(response.startswith("IN-USE")):
        print("\nUsername already in use, please choose another one.")
        sock.close()

    elif(response.startswith("BUSY")):
        print("The server is busy. Please try again in few minutes.")
        sock.close()
        sys.exit()

    else:
        print("\nSuccesful login.\nHello " + username + "! If you do not know what to do, type '!help'")
        break

t = threading.Thread(target=clientReceive, daemon=True)
t.start()

while True:
    command = input()
    if(command == "!quit"):
        sock.close()
        sys.exit()
    elif(command == "!who"):
        message = ("WHO\n").encode("utf-8")
        sock.sendall(message)
    elif(command.startswith("@")):
        message = ("SEND " + command[1:] + "\n" + "WHO\n").encode("utf-8")
        sock.sendall(message)
    else:
        print("Wrong command. !help will provide more command info")
