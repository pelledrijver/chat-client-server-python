# chat-client-server-python
I created a text-based chat client and server using Python and its socket module. The chat client and chat server are built on top of TCP and use their own application-layer protocol.

| Message | Sent by | Description |
| :---         |    :---   |       :---  |
| HELLO-FROM <name>\n   | Client     | First hand-shake message.    |
| HELLO <name>\n     | Server       | Second hand-shake message.      |
| WHO\n     | Client     | Request for all currently logged-in users.      |
| WHO-OK \<name_1\>,..., \<name_n\>\n     | Server       | A list containing all currently logged-in users.      |
| SEND <user> <msg>\n     | Client       | A chat message for a user. Note that the message cannot contain the newline character, because it is used as the message delimiter.      |
| SEND-OK\n     | Server       | Response to a client if their ‘SEND’ message is processed successfully.      |
| UNKNOWN\n      | Server | Sent in response to a SEND message to indicate that the destination user is not currently logged in.      |
| DELIVERY <user> <msg>\n      | Server       |  A chat message from a user      |
| IN-USE\n  | Server       |  Sent during handshake if the user cannot log in because the chosen username is already in use.      |
| BUSY\n      | Server       | Sent during handshake if the user cannot log in because the maximum number of clients has been reached.      |
| BAD-RQST-HDR\n      | Server       |  Sent if the last message received from the client contains an error in the header.      |
| BAD-RQST-BODY\n      | Server | Sent if the last message received from the client contains an error in the body.      |

