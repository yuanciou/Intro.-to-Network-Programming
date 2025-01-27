import socket
import threading
import time

# for server
HOST_NAME = socket.gethostname()
HOST_IP = "140.113.235.15" + HOST_NAME[5]
TCP_SERVER_PORT = ""

# for register
USER_INFO = {}

# for gaming
LOGIN_USER = {}     # {"username": ["status", "socket"]}
PUBLIC_ROOM = {}    # {"roomname": ["game_type", "public", "owner", "status", "socket"]}
PRIVATE_ROOM = {}

# PUBLIC_ROOM["roomname"] = ["game_type", "public", "owner", "status", "port"]

def handle_client(client_socket, client_address):
    """
    Function to handle communication with a connected client.
    """
    current_thread = threading.current_thread()
    #print("Current thread:", current_thread.name)   
    print(f"Connected successfully \n Client: {client_address}")
    while True:
        try:
            client_message = client_socket.recv(1024).decode()
            if not client_message:
                break  # Connection closed by the client

            option, info = client_message.split()

            if option == "register":
                if info in USER_INFO:
                    message = "Username already exists."
                    client_socket.send(message.encode())
                else:
                    message = "Enter the password: "
                    client_socket.send(message.encode())

                    password = client_socket.recv(1024).decode()
                    USER_INFO[info] = password
                    message = f"{info} {password}"
                    client_socket.send(message.encode())
            elif option == "login":
                if info in USER_INFO:
                    message = "Enter the password: "
                    client_socket.send(message.encode())

                    logout_flag = False
                    while(True):
                        password = client_socket.recv(1024).decode()
                        if (USER_INFO[info] == password and info not in LOGIN_USER):
                            LOGIN_USER[info] = ["Idle", client_socket]

                            """
                            --------------------------------------------------
                                        E. Display the online status
                            ---------------------------------------------------
                            """
                            message = ""
                            for (key, value) in LOGIN_USER.items():
                                message = message + key + ">" + value[0] + " "
                            message = message + ";"
                            for (key, value) in PUBLIC_ROOM.items():
                                message = message + key + ">"
                                for status in range(4):
                                    message = message + value[status] + ","
                                message = message + " "
                            
                            client_socket.send(message.encode())

                            while(True):
                                player_message = client_socket.recv(1024).decode()
                                # print(current_thread.name, "1:", player_message)
                                choice, work = player_message.split()
                                if(choice == "logout"):
                                    LOGIN_USER.pop(work)
                                    if(work in LOGIN_USER):
                                        message = "Deleting faild."
                                        client_socket.send(message.encode())
                                    else:
                                        message = "logout successfully."
                                        client_socket.send(message.encode())
                                        logout_flag = True
                                        break
                                elif(choice == "ListRoom"):
                                    message = "ListRoom "
                                    for (key, value) in PUBLIC_ROOM.items():
                                        message = message + key + ">"
                                        for status in range(4):
                                            message = message + value[status] + ","
                                        message = message + ";"
                                    message = message + ";"
                                    client_socket.send(message.encode())
                                elif(choice == "createroom"):
                                    room_type, room_i = work.split(">")
                                    roominfo = room_i.split(",")
                                    if(room_type == "Public"):
                                        if(roominfo[0] in PUBLIC_ROOM):
                                            message = "Room name exit. Please try again."
                                            client_socket.send(message.encode())
                                        else:
                                            PUBLIC_ROOM[roominfo[0]] = [roominfo[1], roominfo[2], roominfo[3], "Waiting"]
                                            LOGIN_USER[roominfo[3]][0] = "InRoom"
                                            message = "Creat Room Successfully."
                                            client_socket.send(message.encode())

                                            PUBLIC_ROOM[roominfo[0]].append(client_socket)
                                            while(roominfo[0] in PUBLIC_ROOM):
                                                time.sleep(2)
                                    elif(room_type == "Private"):
                                        if(roominfo[0] in PRIVATE_ROOM):
                                            message = "Room name exit. Please try again."
                                            client_socket.send(message.encode())
                                        else:
                                            PRIVATE_ROOM[roominfo[0]] = [roominfo[1], roominfo[2], roominfo[3], "Waiting"]
                                            LOGIN_USER[roominfo[3]][0] = "InRoom"
                                            message = "Creat Room Successfully."
                                            client_socket.send(message.encode())
                                            #time.sleep(1)

                                            while(True):
                                                time.sleep(1)
                                                client_port_message_i = client_socket.recv(1024).decode()
                                                # print(client_port_message_i)
                                                client_port_message_work, client_port_message_job = client_port_message_i.split()
                                                if(client_port_message_work == "RequestIdlePlayer"):
                                                    message = "IdlePlayer>"
                                                    for (key, value) in LOGIN_USER.items():
                                                        if(value[0] == "Idle"):
                                                            message = message + key + " "
                                                    client_socket.send(message.encode())
                                                elif(client_port_message_work == "InviteUser"):
                                                    invited, inviter = client_port_message_job.split(",")
                                                    if invited in LOGIN_USER and LOGIN_USER[invited][0] == "Idle":
                                                        message = "RoomInviting " + inviter
                                                        LOGIN_USER[invited][1].send(message.encode())
                                                        while True:
                                                            time.sleep(1)
                                                            invited_return = LOGIN_USER[invited][1].recv(1024).decode()
                                                            #print("Received data: ", invited_return)  # 調試輸出以查看實際接收到的訊息

                                                            if invited_return == "InvitationAccept" or invited_return == "InvitationReject":
                                                                client_socket.send(invited_return.encode())
                                                                break
                                                            

                                                        if(invited_return == "InvitationAccept"):
                                                            time.sleep(1)
                                                            private_room_server = client_socket.recv(1024).decode()
                                                            # print(private_room_server)
                                                            private_room_server = private_room_server + ";" + roominfo[1]
                                                            LOGIN_USER[invited][1].send(private_room_server.encode())
                                                            LOGIN_USER[inviter][0] = "InGame"
                                                            LOGIN_USER[invited][0] = "InGame"
                                                            PRIVATE_ROOM[roominfo[0]][3] = "InGame"

                                                            # after game
                                                            private_room_delete = client_socket.recv(1024).decode()
                                                            check, roomname, player1, player2 = private_room_delete.split()
                                                            if(check == "DelPrivateRoom"):
                                                                # player->idle
                                                                LOGIN_USER[player1][0] = "Idle"
                                                                LOGIN_USER[player2][0] = "Idle"

                                                                # room delete
                                                                PRIVATE_ROOM.pop(roomname)
                                                                break
                                                    else:
                                                        message = "InvalidInvite"
                                                        client_socket.send(message.encode())
                                elif(choice == "Joinroom"):
                                    join_room_name, join_user = work.split(";")
                                    # print(PUBLIC_ROOM[join_room_name][0])
                                    if(join_room_name not in PUBLIC_ROOM):
                                        message = "The room does not exit"
                                        client_socket.send(message.encode())
                                    elif(PUBLIC_ROOM[join_room_name][3] == "InGame"):
                                        message = "The room is full."
                                        # print(message)
                                        client_socket.send(message.encode())
                                    else:
                                        message = "PublicRequestIpPort"
                                        # print(current_thread.name, "2.")
                                        PUBLIC_ROOM[join_room_name][4].send(message.encode())
                                        # print(current_thread.name, "3.")
                                        
                                        time.sleep(2)
                                        public_room_server = PUBLIC_ROOM[join_room_name][4].recv(1024).decode()
                                        # print(current_thread.name, "4:", PUBLIC_ROOM[join_room_name])
                                        public_room_server = public_room_server + " " + PUBLIC_ROOM[join_room_name][0]
                                        # print(current_thread.name, "5.", public_room_server)
                                        client_socket.send(public_room_server.encode())
                                        PUBLIC_ROOM[join_room_name][3] = "InGame"
                                        LOGIN_USER[PUBLIC_ROOM[join_room_name][2]][0] = "InGame"
                                        LOGIN_USER[join_user][0] = "InGame"
                                        time.sleep(5)

                                        delete_pub_message = PUBLIC_ROOM[join_room_name][4].recv(1024).decode()
                                        # print("5:", delete_pub_message)
                                        delete_pub, delete_pub_room, delete_pub_host = delete_pub_message.split()
                                        if(delete_pub == "DelPublicRoom"):
                                            # player->idle
                                            LOGIN_USER[delete_pub_host][0] = "Idle"
                                            LOGIN_USER[join_user][0] = "Idle"

                                            # room delete
                                            PUBLIC_ROOM.pop(delete_pub_room)
                                        
                                            
                            if(logout_flag == True):
                                break
                        elif(info in LOGIN_USER):
                            message = "AlreadyLoginUser"
                            client_socket.send(message.encode())
                            break
                        else:
                            message = "Incorrect password."
                            client_socket.send(message.encode())
                            continue
                else:
                    message = "User does not exist."
                    client_socket.send(message.encode())
                    

        except ConnectionResetError:
            print(f"Client {client_address} disconnected abruptly.")
            break

    client_socket.close()
    print(f"Connection with client {client_address} closed.")

def main():
    """
    ---------------------------------------------------
                 A. Run the lobby server
    ---------------------------------------------------
    """
    # choose the port number
    global TCP_SERVER_PORT
    while True:
        TCP_SERVER_PORT = input("Choose the port number of the lobby server (10000~15999): ")
        if int(TCP_SERVER_PORT) < 10000 or int(TCP_SERVER_PORT) > 15999:
            print("The port number is invalid, please choose the valid port number")
            continue
        else:
            try:
                tcp_lobby_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_lobby_socket.bind((HOST_IP, int(TCP_SERVER_PORT)))
                break
            except OSError:  # the port is not available
                print("The port number is not available, try another one.")
                continue

    # build the TCP server
    tcp_lobby_socket.listen(10)  # accept up to 10 socket connections
    print("Waiting for client connection...")

    while True:
        tcp_client, tcp_client_addr = tcp_lobby_socket.accept()

        # Start a new thread for each client
        client_thread = threading.Thread(target=handle_client, args=(tcp_client, tcp_client_addr))
        client_thread.start()

if __name__ == "__main__":
    main()
