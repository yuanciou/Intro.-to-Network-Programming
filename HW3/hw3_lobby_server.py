import socket
import threading
import time
import os
import csv

# for server
HOST_NAME = socket.gethostname()
HOST_IP = "140.113.235.15" + HOST_NAME[5]
TCP_SERVER_PORT = ""

# for register
USER_INFO = {}
DATA_FILE = "user_data.csv"

# for broadcasting
BROADCAST_SOCKETS = {}  # {"username": broadcast_socket}

# for invatation
INVATATION_SOCKETS = {}  # {"username": invatation_socket}

# for gaming
LOGIN_USER = {}     # {"username": ["status", "socket"]}
PUBLIC_ROOM = {}    # {"roomname": ["game_type", "public", "owner", "status", "socket", client]}
PRIVATE_ROOM = {}   # {"roomname": ["game_type", "private", "owner", "status", "socket", client]}

# PUBLIC_ROOM["roomname"] = ["game_type", "public", "owner", "status", "port"]

def load_user_data():
    """Load user account data from an external CSV file."""
    global USER_INFO
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            USER_INFO = {rows[0]: rows[1] for rows in reader}
    else:
        print("No existing user data found. Starting fresh.")

def save_user_data():
    """Save user account data to an external CSV file."""
    with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for username, password in USER_INFO.items():
            writer.writerow([username, password])

def broadcast_message(message):
    """Broadcast a message to all connected clients' broadcasting sockets."""
    for username, broadcast_socket in BROADCAST_SOCKETS.items():
        try:
            broadcast_socket.send(message.encode())
        except Exception as e:
            print(f"Error broadcasting to {username}: {e}")


def handle_client(client_socket, client_address, broadcast_socket, invatation_socket):
    """
    Function to handle communication with a connected client.
    """
    current_thread = threading.current_thread()
    #print("Current thread:", current_thread.name)   
    print(f"Connected successfully \n Client: {client_address}")
    while True:
        try:
            client_message = client_socket.recv(1024).decode()
            print(client_message)
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
                    save_user_data()
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
                            message = "login successfully" 
                            client_socket.send(message.encode())

                            #global tcp_lobby_socket
                            BROADCAST_SOCKETS[info] = broadcast_socket
                            INVATATION_SOCKETS[info] = invatation_socket

                            broadcast_message(f"User {info} has logged in.")

                            while(True):
                                player_message = client_socket.recv(1024).decode()
                                # print(current_thread.name, "1:", player_message)
                                choice, work = player_message.split()
                                if(choice == "logout"):
                                    # delete the broadcast socket
                                    broadcast_message(f"User {work} has logged out.")
                                    if work in BROADCAST_SOCKETS:
                                        BROADCAST_SOCKETS.pop(work)

                                    if work in INVATATION_SOCKETS:
                                        INVATATION_SOCKETS.pop(work)
                                    
                                    LOGIN_USER.pop(work)
                                    if(work in LOGIN_USER):
                                        message = "Deleting faild."
                                        client_socket.send(message.encode())
                                    else:
                                        message = "logout successfully."
                                        client_socket.send(message.encode())
                                        logout_flag = True
                                        break
                                elif(choice == "ListPlayers"):
                                    message = ""
                                    for (key, value) in LOGIN_USER.items():
                                        message = message + key + ">" + value[0] + " "
                                    client_socket.send(message.encode())
                                elif(choice == "ListRoom"):
                                    message = ""
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
                                            PUBLIC_ROOM[roominfo[0]] = [roominfo[1], roominfo[2], roominfo[3], "Waiting", client_socket, "empty"]
                                            broadcast_message(f"Public room '{roominfo[0]}' created by {roominfo[3]}.")
                                            LOGIN_USER[roominfo[3]][0] = "InRoom"
                                            message = "Creat Room Successfully."
                                            client_socket.send(message.encode())

                                    elif(room_type == "Private"):
                                        if(roominfo[0] in PRIVATE_ROOM):
                                            message = "Room name exit. Please try again."
                                            client_socket.send(message.encode())
                                        else:
                                            PRIVATE_ROOM[roominfo[0]] = [roominfo[1], roominfo[2], roominfo[3], "Waiting", client_socket, "empty"]
                                            LOGIN_USER[roominfo[3]][0] = "InRoom"
                                            message = "Creat Room Successfully."
                                            client_socket.send(message.encode())
                                            
                                elif(choice == "RequestIdlePlayer"):
                                    message = "IdlePlayer>"
                                    for (key, value) in LOGIN_USER.items():
                                        if(value[0] == "Idle"):
                                            message = message + key + " "
                                    client_socket.send(message.encode())
                                elif(choice == "InviteUser"):
                                    invited, roominviter = work.split(",")
                                    if invited in LOGIN_USER and LOGIN_USER[invited][0] == "Idle":
                                        invi_room, invi_user, roomtype = roominviter.split(";")
                                        message = invi_room + " " + invi_user + " " + roomtype
                                        INVATATION_SOCKETS[invited].send(message.encode())
                                        time.sleep(1)

                                        broad_m = "A invatation from " + invi_user + ", Please go invatation managment."
                                        BROADCAST_SOCKETS[invited].send(broad_m.encode())
                                    else:
                                        message = "InvalidInvite"
                                        client_socket.send(message.encode())
                                elif(choice == "InvitationAccept"):
                                    invi_room_name, inviter, invited_user = work.split(",")
                                    print(work)
                                    
                                    if(invi_room_name not in PRIVATE_ROOM):
                                        message = "RoomClosed"
                                        client_socket.send(message.encode())
                                    elif(PRIVATE_ROOM[invi_room_name][5] != "empty"):
                                        message = "RoomFull"
                                        # print(message)
                                        client_socket.send(message.encode())
                                    else:
                                        LOGIN_USER[invited_user][0] = "InRoom"
                                        PRIVATE_ROOM[invi_room_name][5] = invited_user
                                        message = "Invitation Success"
                                        client_socket.send(message.encode())
                                        message = invited_user + " Join Private Room"
                                        BROADCAST_SOCKETS[inviter].send(message.encode())
                                        BROADCAST_SOCKETS[invited_user].send(message.encode())
                                        

                                        
                                elif(choice == "StartPivateGame"):
                                    if(PRIVATE_ROOM[work][5] == "empty"):
                                        message = "Not enough players join the room"
                                        client_socket.send(message.encode())
                                    else:
                                        message = PRIVATE_ROOM[work][2] + " start the game"
                                        BROADCAST_SOCKETS[PRIVATE_ROOM[work][2]].send(message.encode())
                                        message = PRIVATE_ROOM[work][2] + " start the game, please click [1/2/3] to reset the status"
                                        BROADCAST_SOCKETS[PRIVATE_ROOM[work][5]].send(message.encode())
                                        client_socket.send(message.encode())

                                        time.sleep(1)
                                        private_room_server = client_socket.recv(1024).decode()
                                        # print(private_room_server)
                                        private_room_server = private_room_server + ";" + PRIVATE_ROOM[work][0]
                                        LOGIN_USER[PRIVATE_ROOM[work][5]][1].send(private_room_server.encode())
                                        LOGIN_USER[PRIVATE_ROOM[work][2]][0] = "InGame"
                                        LOGIN_USER[PRIVATE_ROOM[work][5]][0] = "InGame"
                                        PRIVATE_ROOM[work][3] = "InGame"

                                        # after game
                                        private_room_delete = client_socket.recv(1024).decode()
                                        check, roomname, player1, player2 = private_room_delete.split()
                                        if(check == "DelPrivateRoom"):
                                            # player->idle
                                            LOGIN_USER[player1][0] = "Idle"
                                            LOGIN_USER[player2][0] = "Idle"
                                            
                                            message = "Exit Room"
                                            BROADCAST_SOCKETS[PRIVATE_ROOM[roomname][2]].send(message.encode())
                                            BROADCAST_SOCKETS[PRIVATE_ROOM[roomname][5]].send(message.encode())
                                            # room delete
                                            PRIVATE_ROOM.pop(roomname)
                                            
                                elif(choice == "StartPublicGame"):
                                    if(PUBLIC_ROOM[work][5] == "empty"):
                                        message = "Not enough players join the room"
                                        client_socket.send(message.encode())
                                    else:
                                        message = PUBLIC_ROOM[work][2] + " start the game"
                                        BROADCAST_SOCKETS[PUBLIC_ROOM[work][2]].send(message.encode())
                                        message = PUBLIC_ROOM[work][2] + " start the game, please click [1/2/3] to reset the status"
                                        BROADCAST_SOCKETS[PUBLIC_ROOM[work][5]].send(message.encode())
                                        client_socket.send(message.encode())

                                        time.sleep(1)
                                        public_room_server = client_socket.recv(1024).decode()
                                        # print(private_room_server)
                                        public_room_server = public_room_server + ";" + PUBLIC_ROOM[work][0]
                                        LOGIN_USER[PUBLIC_ROOM[work][5]][1].send(public_room_server.encode())
                                        LOGIN_USER[PUBLIC_ROOM[work][2]][0] = "InGame"
                                        LOGIN_USER[PUBLIC_ROOM[work][5]][0] = "InGame"
                                        PUBLIC_ROOM[work][3] = "InGame"

                                        # after game
                                        public_room_delete = client_socket.recv(1024).decode()
                                        check, roomname, player1 = public_room_delete.split()
                                        if(check == "DelPublicRoom"):
                                            # player->idle
                                            LOGIN_USER[player1][0] = "Idle"
                                            LOGIN_USER[PUBLIC_ROOM[roomname][5]][0] = "Idle"
                                            
                                            message = "Exit Room"
                                            BROADCAST_SOCKETS[PUBLIC_ROOM[roomname][2]].send(message.encode())
                                            BROADCAST_SOCKETS[PUBLIC_ROOM[roomname][5]].send(message.encode())
                                            # room delete
                                            PUBLIC_ROOM.pop(roomname)
                                            
                                elif(choice == "LeaveRoomPrivate"):
                                    cur_room, cur_user = work.split(",")
                                    if (cur_user == PRIVATE_ROOM[cur_room][2]): # is owner
                                        if(PRIVATE_ROOM[cur_room][5] == "empty"):
                                            PRIVATE_ROOM.pop(cur_room)
                                            
                                        else:
                                            new_owner = PRIVATE_ROOM[cur_room][5]
                                            LOGIN_USER[PRIVATE_ROOM[cur_room][2]][0] = "Idle"
                                            PRIVATE_ROOM[cur_room][2] = new_owner
                                            PRIVATE_ROOM[cur_room][5] = "empty"
                                            PRIVATE_ROOM[cur_room][4] = LOGIN_USER[new_owner][1]
                                            change_owner = "Become Private Room Owner"
                                            BROADCAST_SOCKETS[new_owner].send(change_owner.encode())
                                    else:
                                        LOGIN_USER[PRIVATE_ROOM[cur_room][5]][0] = "Idle"
                                        PRIVATE_ROOM[cur_room][5] = "empty"
                                        re_invite = "Player Leave, Please Re-invite"
                                        BROADCAST_SOCKETS[PRIVATE_ROOM[cur_room][2]].send(re_invite.encode())
                                elif(choice == "LeaveRoomPublic"):
                                    cur_room, cur_user = work.split(",")
                                    if (cur_user == PUBLIC_ROOM[cur_room][2]): # is owner
                                        if(PUBLIC_ROOM[cur_room][5] == "empty"):
                                            PUBLIC_ROOM.pop(cur_room)
                                            
                                        else:
                                            new_owner = PUBLIC_ROOM[cur_room][5]
                                            LOGIN_USER[PUBLIC_ROOM[cur_room][2]][0] = "Idle"
                                            PUBLIC_ROOM[cur_room][2] = new_owner
                                            PUBLIC_ROOM[cur_room][5] = "empty"
                                            PUBLIC_ROOM[cur_room][4] = LOGIN_USER[new_owner][1]
                                            change_owner = "Become Public Room Owner"
                                            BROADCAST_SOCKETS[new_owner].send(change_owner.encode())
                                    else:
                                        LOGIN_USER[PUBLIC_ROOM[cur_room][5]][0] = "Idle"
                                        PUBLIC_ROOM[cur_room][5] = "empty"
                                        re_pub = "The player leave the public room."
                                        BROADCAST_SOCKETS[PUBLIC_ROOM[cur_room][2]].send(re_pub.encode())

                                                    
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
                                        LOGIN_USER[join_user][0] = "InRoom"
                                        PUBLIC_ROOM[join_room_name][5] = join_user
                                        message = "Join room success"
                                        client_socket.send(message.encode())
                                        message = join_user + " Join Public Room"
                                        BROADCAST_SOCKETS[PUBLIC_ROOM[join_room_name][2]].send(message.encode())
                                        BROADCAST_SOCKETS[join_user].send(message.encode())
                                
                                elif choice == "UploadGame":
                                    game_name, uploader, description, file_size = work.split(",")
                                    file_size = int(file_size)
                                    
                                    game_file_path = os.path.join("game_file", game_name)

                                    # 接收檔案並保存
                                    received_size = 0
                                    with open(game_file_path, "wb") as f:
                                        while received_size < file_size:
                                            time.sleep(0.5)
                                            data = client_socket.recv(1024)
                                            if not data:
                                                break
                                            f.write(data)
                                            received_size += len(data)
                                    if received_size == file_size:
                                        print(f"Game '{game_name}' uploaded successfully and saved to '{game_file_path}'.")
                                    else:
                                        print(f"Error: Expected {file_size} bytes but received {received_size} bytes.")
                                    
                                    # 更新或創建 game_list.csv
                                    
                                    csv_path = os.path.join("game_file", "game_list.csv")
                                    file_exists = os.path.exists(csv_path)

                                    # 讀取現有的遊戲列表
                                    games = []
                                    if file_exists:
                                        with open(csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
                                            reader = csv.reader(csvfile)
                                            header = next(reader, None)  # 跳過標題行
                                            games = [row for row in reader]

                                    # 更新或新增遊戲資訊
                                    game_updated = False
                                    for game in games:
                                        if game[0] == game_name[:-3]:  # 如果遊戲名稱已存在
                                            game[1] = uploader  # 更新開發者
                                            game[2] = description  # 更新描述
                                            game_updated = True
                                            break

                                    if not game_updated:
                                        # 如果遊戲名稱不存在，新增一行
                                        games.append([game_name[:-3], uploader, description])

                                    # 覆寫更新後的遊戲列表
                                    with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
                                        writer = csv.writer(csvfile)
                                        writer.writerow(["Game Name", "Developer", "Description"])  # 寫入標題行
                                        writer.writerows(games)  # 寫入更新後的遊戲內容

                                    print(f"Game list updated. {'Game updated' if game_updated else 'Game added'}: {game_name}")

                                    print(f"Game '{game_name}' uploaded by {uploader} saved successfully.")
                                elif choice == "DownloadGame":
                                    game_name = work
                                    game_file_path = os.path.join("game_file", game_name)

                                    if not os.path.exists(game_file_path):
                                        client_socket.send(f"Error: File '{game_name}' does not exist.".encode())
                                    else:
                                        # 傳送檔案
                                        file_size = os.path.getsize(game_file_path)
                                        client_socket.send(f"{file_size}".encode())
                                        
                                        with open(game_file_path, "rb") as f:
                                            while chunk := f.read(1024):
                                                client_socket.send(chunk)
                                        
                                        print(f"Game file '{game_name}' sent to client.")
                                elif choice == "ListLobbyGame":
                                    csv_path = os.path.join("game_file", "game_list.csv")
                                    if not os.path.exists(csv_path):
                                        client_socket.send("NoGames".encode())
                                    else:
                                        # 讀取 CSV 並回傳所有遊戲資訊
                                        with open(csv_path, mode="r", encoding="utf-8") as csvfile:
                                            reader = csv.reader(csvfile)
                                            next(reader)  # 跳過標題行
                                            games = ["{}, {}, {}".format(row[0], row[1], row[2]) for row in reader]
                                            if not games:
                                                client_socket.send("NoGames".encode())
                                            else:
                                                client_socket.send(";".join(games).encode())
                                elif choice == "ListMyGame":
                                    developer = work
                                    csv_path = os.path.join("game_file", "game_list.csv")
                                    if not os.path.exists(csv_path):
                                        client_socket.send("NoGames".encode())
                                    else:
                                        # 讀取 CSV 並過濾出當前用戶的遊戲
                                        with open(csv_path, mode="r", encoding="utf-8") as csvfile:
                                            reader = csv.reader(csvfile)
                                            next(reader)  # 跳過標題行
                                            games = ["{}, {}, {}".format(row[0], row[1], row[2]) for row in reader if row[1] == developer]
                                            if not games:
                                                client_socket.send("NoGames".encode())
                                            else:
                                                client_socket.send(";".join(games).encode())



                                        
                                            
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
    load_user_data()
    print(f"Loaded {len(USER_INFO)} user accounts.")
    global tcp_lobby_socket
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
    tcp_lobby_socket.listen(15)  # accept up to 10 socket connections
    print("Waiting for client connection...")

    while True:
        tcp_client, tcp_client_addr = tcp_lobby_socket.accept()
        time.sleep(1)
        broadcast_socket, _ = tcp_lobby_socket.accept()
        time.sleep(1)
        invatation_socket, _ = tcp_lobby_socket.accept()
        # Start a new thread for each client
        client_thread = threading.Thread(target=handle_client, args=(tcp_client, tcp_client_addr, broadcast_socket, invatation_socket))
        client_thread.start()

if __name__ == "__main__":
    main()
