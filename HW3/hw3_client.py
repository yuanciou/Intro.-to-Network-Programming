import socket
import time
import os
import threading
import importlib.util

HOST_NAME = socket.gethostname()
HOST_IP =  "140.113.235.15" + HOST_NAME[5]

INVATATION_LIST = [] # ["roomname", inviter, invitype]

broadcast_message = ""

def list_game(lobby_socket, username):
    while True:
        choice = input("\nList Game Options:\n1. List Lobby Games\n2. List My Games\n3. Back\n")
        if choice == "1":
            try:
                # 發送請求獲取所有遊戲清單
                lobby_socket.send("ListLobbyGame tmp".encode())
                response = lobby_socket.recv(1024).decode()

                # 如果回傳空清單
                if response == "NoGames":
                    print("No games are currently available in the lobby.")
                else:
                    print("\n[Available Lobby Games]\n")
                    games = response.split(";")
                    for game in games:
                        if game.strip():  # 確保不顯示空行
                            game_name, developer, description = game.split(",")
                            print(f"Game Name: {game_name}\tDeveloper: {developer}\tDescription: {description}")
            except Exception as e:
                print(f"Error listing lobby games: {e}")

        elif choice == "2":
            try:
                # 發送請求獲取當前用戶的遊戲清單
                lobby_socket.send(f"ListMyGame {username}".encode())
                response = lobby_socket.recv(1024).decode()

                # 如果回傳空清單
                if response == "NoGames":
                    print("You have not uploaded any games.")
                else:
                    print("\n[Your Uploaded Games]")
                    games = response.split(";")
                    for game in games:
                        if game.strip():  # 確保不顯示空行
                            game_name, developer, description = game.split(",")
                            print(f"Game Name: {game_name}\tDeveloper: {developer}\tDescription: {description}")
            except Exception as e:
                print(f"Error listing your games: {e}")

        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")


def game_development_management(lobby_socket, username):
    while True:
        choice = input("\nGame Development Management:\n1. Upload Game File\n2. Back\n")
        if choice == "1":
            try:
                game_name = ""
                while True:
                    game_name = input("Enter the game file name (e.g., game.py): ")
                    if (".py" not in game_name):
                        print("The file name must end with .py")
                        continue
                    else:
                        break
                description = input("Enter a description for the game: ")
                file_path = os.path.join("game_file", game_name)

                # 檢查檔案是否存在
                if not os.path.exists(file_path):
                    print("File does not exist in 'game_file' directory. Please try again.")
                    continue
                
                file_size = os.path.getsize(file_path)
                # 發送上傳請求
                message = f"UploadGame {game_name},{username},{description},{file_size}"
                lobby_socket.send(message.encode())

                # 傳送檔案
                with open(file_path, "rb") as f:
                    while chunk := f.read(1024):
                        lobby_socket.send(chunk)
                
                print("Game file uploaded successfully.")
            except Exception as e:
                print(f"Error uploading file: {e}")
        elif choice == "2":
            break
        else:
            print("Invalid choice. Please try again.")

def download_game_file(lobby_socket, game_name):
    try:
        game_name_py = game_name + ".py"
        message = f"DownloadGame {game_name_py}"
        lobby_socket.send(message.encode())

        file_size = lobby_socket.recv(1024).decode()
        file_size = int(file_size)
        # 接收檔案內容
        file_path = os.path.join("game_file_download", game_name_py)
        received_size = 0
        with open(file_path, "wb") as f:
            while received_size < file_size:
                data = lobby_socket.recv(1024)
                if not data:
                    break
                f.write(data)
                received_size += len(data)
        if received_size == file_size:
            print(f"Game '{game_name}' download successfully and saved to '{file_path}'.")
        else:
            print(f"Error: Expected {file_size} bytes but received {received_size} bytes.")
    except Exception as e:
        print(f"Error downloading file: {e}")


def invatation_append(invatation_socket):
    while True:
        try:
            invatation_message = invatation_socket.recv(1024).decode()
            room, user, gametype = invatation_message.split()
            INVATATION_LIST.append([room, user, gametype])
            
        except Exception as e:
            print(f"Invatation socket disconnected: {e}")
            break

def in_room_handler(roomname, username, host_or_not, private_public, lobby_socket, game_type):
    print("=============================\n         In Room\n=============================")
    download_game_file(lobby_socket, game_type)
    
    if(private_public == "private"):
        idleplayers = []
        invite_user = ""
        while True:
            # print("test ", broadcast_message)
            if("start the game" in broadcast_message):
                break
            if("Become Private Room Owner" in broadcast_message):
                host_or_not = "host"
            choice = input("\nPlease choose the option:\n1. List Player\n2. Invite User\n3. Start Game\n4. Exit rooms\n")
            if(choice != "1" and choice != "2" and choice != "3" and choice != "4"):
                print("Invalid choice, please try again!")
                continue
            else:
                if(choice == "4"):
                        message = "LeaveRoomPrivate " + roomname + "," + username
                        lobby_socket.send(message.encode())
                        return
                elif(choice == "1"):
                    if(host_or_not == "host"):
                        message = "RequestIdlePlayer tmp"
                        lobby_socket.send(message.encode())

                        time.sleep(1)
                        private_lobby_message = lobby_socket.recv(1024).decode()
                        work_type, job = private_lobby_message.split(">")
                        if(work_type == "IdlePlayer"):
                            idleplayers = job.split()
                            print("\nIdle Player List:")
                            for idleplayer in idleplayers:
                                print(idleplayer)
                    else:
                        if("start the game" in broadcast_message):
                            break
                        else:
                            print("Invalid choice")
                elif(choice == "2"):
                    if(host_or_not == "host"):
                        while(True):
                            option = input("Enter the option (1. Invite 2. Exit): ")
                            if(option == "1"):
                                invite_user = input("Enter the inviting username: ")
                                message = "RequestIdlePlayer tmp"
                                lobby_socket.send(message.encode())

                                time.sleep(1)
                                private_lobby_message = lobby_socket.recv(1024).decode()
                                work_type, job = private_lobby_message.split(">")
                                if(work_type == "IdlePlayer"):
                                    idleplayers = job.split()
                                if(invite_user not in idleplayers):
                                    print("The invited user is invalid, try again.")
                                    break
                                message = "InviteUser " + invite_user + "," + roomname + ";" + username + ";" + game_type
                                lobby_socket.send(message.encode())
                            else:
                                break
                    else:
                        if("start the game" in broadcast_message):
                            break
                        else:
                            print("Invalid choice")
                elif(choice == "3"):
                    if(host_or_not == "host"):
                        message = "StartPivateGame " + roomname
                        lobby_socket.send(message.encode())

                        time.sleep(1)
                        startgame_message = lobby_socket.recv(1024).decode()
                        if(startgame_message == "Not enough players join the room"):
                            print(startgame_message)
                        else:
                            break
                    else:
                        if("start the game" in broadcast_message):
                            break
                        else:
                            print("Invalid choice")

        if(host_or_not == "host"):
            p2p_port = ""
            while(True):
                p2p_port = input("Please enter the port number to bind (10000~15999): ")
                if int(p2p_port) < 10000 or int(p2p_port) > 15999:
                    print("The port number is invalid, please choose the valid port number")
                    continue
                else:
                    try:
                        private_room_owner_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        private_room_owner_socket.bind((HOST_IP, int(p2p_port)))
                        print("Set up server. Waiting for connection...")
                        break
                    except OSError:  # the port is not available
                        print("The port number is not available, try another one.")
                        continue
            message = "PrivateConnect " + HOST_IP + ";" + p2p_port
            lobby_socket.send(message.encode())

            private_room_owner_socket.listen(1)
            private_client, private_client_addr = private_room_owner_socket.accept()
            print("Connect by", private_client_addr)

            """
            !!!!!!!!!!!!!!!!!!! GAME START
            """
            success = game_type_handler(game_type, "host", private_client)
            private_client.close()
            private_room_owner_socket.close()
            if not success:
                print("An error occurred during the game. Returning to pre-game state.")
            else:
                print("\nGAME FINISH")
            

            # delete the private room

            dele_private_room_message = "DelPrivateRoom" + " " + roomname + " " + invite_user + " " + username
            lobby_socket.send(dele_private_room_message.encode())
            return
        else:
            private_server_work = ""
            server_info = ""
            while(True):
                private_server_m = lobby_socket.recv(1024).decode()
                # print(private_server_m)
                private_server_work, server_info = private_server_m.split()
                if(private_server_work == "PrivateConnect"):
                    break
                else:
                    continue
            private_ip, private_port, gametype = server_info.split(";")
            private_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            private_client_socket.connect((private_ip, int(private_port)))
            """
            !!!!!!!!!!!!!!!!!!! GAME START
            """
            success = game_type_handler(gametype, "client", private_client_socket)
            if not success:
                print("An error occurred during the game. Returning to pre-game state.")
            else:
                print("\nGAME FINISH")
            private_client_socket.close()
            return
    else:
        """
                    Public Room
        """
        while(True):
            if("start the game" in broadcast_message):
                break
            if("Become Public Room Owner" in broadcast_message):
                host_or_not = "host"
            choice = input("\nPlease choose the option:\n1. Start Game\n2. Exit rooms\n")
            if(choice != "1" and choice != "2"):
                print("Invalid choice, please try again!")
                continue
            else:
                if(choice == "1"):
                    if(host_or_not == "host"):
                        message = "StartPublicGame " + roomname
                        lobby_socket.send(message.encode())

                        time.sleep(1)
                        startgame_message = lobby_socket.recv(1024).decode()
                        if(startgame_message == "Not enough players join the room"):
                            print(startgame_message)
                        else:
                            break
                    else:
                        if("start the game" in broadcast_message):
                            break
                        else:
                            print("Invalid choice")
                elif(choice == "2"):
                    message = "LeaveRoomPublic " + roomname + "," + username
                    lobby_socket.send(message.encode())
                    return
        if(host_or_not == "host"):
            p2p_port = ""
            while(True):
                p2p_port = input("Please enter the port number to bind (10000~15999): ")
                if int(p2p_port) < 10000 or int(p2p_port) > 15999:
                    print("The port number is invalid, please choose the valid port number")
                    continue
                else:
                    try:
                        public_room_owner_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        public_room_owner_socket.bind((HOST_IP, int(p2p_port)))
                        print("Set up server. Waiting for connection...")
                        break
                    except OSError:  # the port is not available
                        print("The port number is not available, try another one.")
                        continue
            message = "PublicConnect " + HOST_IP + ";" + p2p_port
            lobby_socket.send(message.encode())

            public_room_owner_socket.listen(1)
            public_client, public_client_addr = public_room_owner_socket.accept()
            print("Connect by", public_client_addr)

            """
            !!!!!!!!!!!!!!!!!!! GAME START
            """
            success = game_type_handler(game_type, "host", public_client)
            public_client.close()
            public_room_owner_socket.close()
            if not success:
                print("An error occurred during the game. Returning to pre-game state.")
            else:
                print("\nGAME FINISH")

            # delete the private room

            dele_public_room_message = "DelPublicRoom" + " " + roomname  + " " + username
            lobby_socket.send(dele_public_room_message.encode())
            return
        else:
            public_server_work = ""
            server_info = ""
            while(True):
                private_server_m = lobby_socket.recv(1024).decode()
                # print(private_server_m)
                public_server_work, server_info = private_server_m.split()
                if(public_server_work == "PublicConnect"):
                    break
                else:
                    continue
            public_ip, public_port, gametype = server_info.split(";")
            public_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            public_client_socket.connect((public_ip, int(public_port)))
            """
            !!!!!!!!!!!!!!!!!!! GAME START
            """
            success = game_type_handler(gametype, "client", public_client_socket)
            if not success:
                print("An error occurred during the game. Returning to pre-game state.")
            else:
                print("\nGAME FINISH")
            public_client_socket.close()
            return

def handle_broadcasting(broadcast_socket):
    """Handle messages from the lobby server broadcasting socket."""
    while True:
        try:
            global broadcast_message
            broadcast_message = broadcast_socket.recv(1024).decode()
            time.sleep(1)
            print(f"[Broadcast] {broadcast_message}")
        except Exception as e:
            print(f"Broadcast socket disconnected: {e}")
            break

def game_type_handler(gametype, host_client, connect_socket):
    """Load and execute the 'playgame' function from the downloaded game script."""
    try:
        gametype_py = gametype + ".py"
        file_path = os.path.join("game_file_download", gametype_py)

        # 確保遊戲檔案存在
        if not os.path.exists(file_path):
            print(f"Game file '{gametype}' not found.")
            return

        # 動態載入模組
        spec = importlib.util.spec_from_file_location("game_module", file_path)
        game_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(game_module)

        # 呼叫 playgame 函數
        if hasattr(game_module, "playgame"):
            print(f"Starting game: {gametype}")
            game_module.playgame(host_client, connect_socket)
            print(f"Game '{gametype}' finished.")
            return True
        else:
            print(f"Error: The game '{gametype}' does not have a 'playgame' function.")
            return False
    except Exception as e:
        print(f"Error while executing game '{gametype}': {e}")
        return False

def after_login(username, lobby_socket):
    while(True):
        choice = input("\nPlease choose the option:\n1. Logout\n2. List palyers\n3. List rooms\n4. Create a new room\n5. Join room\n6. Invatation Management\n7. Game Development Management\n8. List Game\n")
        if(choice != "1" and choice != "2" and choice != "3" and choice != "4" and choice != "5" and choice != "6" and choice != "7" and choice != "8"):
            print("Invalid choice, please try again!")
            continue
        else:
            if(choice == "1"):
                INVATATION_LIST.clear()
                return
            elif(choice == "2"):
                message = "ListPlayers tmp"
                lobby_socket.send(message.encode())

                time.sleep(1)
                userstring = lobby_socket.recv(1024).decode()
                userlist = userstring.split()
                if (len(userlist) == 1): # only 1 player (myself)
                    print("\nCurrently, no players are online.\n")
                else:
                    print("Online Players:")
                    for userstatus in userlist:
                        if(">" in userstatus):
                            user, status = userstatus.split(">")
                            if(user == username):
                                continue
                            else:
                                print("Player Name:", user, "Status:", status)
                    print()
            elif(choice == "3"):
                """
                           Invitation and List Room
                --------------------------------------------                
                """
                message = "ListRoom tmp"
                lobby_socket.send(message.encode())

                room_dict = {}
                room_dict.clear()
                listroom = lobby_socket.recv(1024).decode()
                
                roomlist = listroom.split(";")
                if(">" not in listroom):
                    print("No public rooms waiting for players.\n")
                    continue
                else: 
                    print("Public Rooms:")
                    for roomstatus in roomlist:
                        if(">" in roomstatus):
                            roomname, room_i = roomstatus.split(">")
                            roominfo = room_i.split(",")
                            room_dict[roomname] = roominfo
                            print("Name:", roomname, "Type:", roominfo[0], "Owner:", roominfo[2], "Status:", roominfo[3])
                print()
            elif(choice == "4"):
                """
                ---------------------------------------------------
                            F. Create a game room
                ---------------------------------------------------
                """
                create_room = []
                avalible_game = []
                print("\n    Room Creating\n---------------------")
                while(True):
                    create_room.clear()
                    avalible_game.clear()
                    create_room.append(input("Please enter the room name: "))
                    
                    # 發送請求獲取所有遊戲清單
                    lobby_socket.send("ListLobbyGame tmp".encode())
                    response = lobby_socket.recv(1024).decode()

                    # 如果回傳空清單
                    if response == "NoGames":
                        print("No games are currently available in the lobby, please upload game first")
                        break
                    else:
                        print("\n[Available Lobby Games]")
                        games = response.split(";")
                        for game in games:
                            if game.strip():  # 確保不顯示空行
                                game_name, developer, description = game.split(",")
                                print(f"Game Name: {game_name}\tDeveloper: {developer}\tDescription: {description}")
                                avalible_game.append(game_name)

                    while True:
                        game_type = input("Please enter the game type: ")
                        if(game_type not in avalible_game):
                            print("The game is not provided, please select another one.")
                            continue
                        else:
                            create_room.append(game_type)
                            break

                    create_room.append(input("Please enter the room type (1. Public 2. Private): "))
                    # if(create_room[1] == "1"):
                    #     create_room[1] = "1A2B"
                    # elif(create_room[1] == "2"):
                    #     create_room[1] = "Connect_4"
                    
                    if(create_room[2] == "1"):
                        create_room[2] = "Public"
                    elif(create_room[2] == "2"):
                        create_room[2] = "Private"

                    # check the room name is valid
                    message = "createroom " + create_room[2] + ">" + create_room[0] + "," + create_room[1] + "," + create_room[2] + "," + username
                    lobby_socket.send(message.encode())

                    time.sleep(1)
                    room_valid_message = lobby_socket.recv(1024).decode()
                    if(room_valid_message == "Room name exit. Please try again."):
                        print("!!", room_valid_message)
                        continue
                    elif(room_valid_message == "Creat Room Successfully." and create_room[2] == "Public"):
                        """
                                        Public room
                        --------------------------------------------                
                        """
                        in_room_handler(create_room[0], username, "host", "public", lobby_socket, create_room[1])
                        break                        
                    elif(room_valid_message == "Creat Room Successfully." and create_room[2] == "Private"):
                        """
                                        Private room
                        --------------------------------------------                
                        """
                        in_room_handler(create_room[0], username, "host", "private", lobby_socket, create_room[1])
                        break
            elif(choice == "5"):
                message = "ListRoom tmp"
                lobby_socket.send(message.encode())

                room_dict = {}
                room_dict.clear()
                listroom = lobby_socket.recv(1024).decode()
                
                roomlist = listroom.split(";")
                if(">" not in listroom):
                    print("No public rooms waiting for players.\n")
                    continue
                else: 
                    print("Public Rooms:")
                    for roomstatus in roomlist:
                        if(">" in roomstatus):
                            roomname, room_i = roomstatus.split(">")
                            roominfo = room_i.split(",")
                            room_dict[roomname] = roominfo
                            print("Name:", roomname, "Type:", roominfo[0], "Owner:", roominfo[2], "Status:", roominfo[3])
                print()

                # print(room_dict)
                join_room_name = input("Please enter the room name: ")
                message = "Joinroom " + join_room_name + ";" + username
                lobby_socket.send(message.encode())
                
                time.sleep(1)
                lobby_join_message = lobby_socket.recv(1024).decode()
                # print(lobby_join_message)
                if(lobby_join_message == "The room does not exit"):
                    print("The room name is invalid.")
                    continue
                elif(lobby_join_message == "The room is full."):
                    print("The room is full. Please try again.")
                    continue
                else:
                    in_room_handler(join_room_name, username, "client", "public", lobby_socket, room_dict[join_room_name][0])
            elif(choice == "6"):
                if not INVATATION_LIST:
                    print("\n[Invitation Management] No invitations available.")
                    continue
                else:
                    while True:
                        print("\n[Invitation Management] Current invitations:")
                        for i, info in enumerate(INVATATION_LIST):
                            inviroom, inviter, invitype = info
                            print(f"{i + 1}. Invitation from {inviter}, room name {inviroom}, game type {invitype}.")
                        choice = input("\nEnter the invitation number to respond (or 'q' to quit): ")
                        if choice.lower() == 'q':
                            break
                        try:
                            index = int(choice) - 1
                            if index < 0 or index >= len(INVATATION_LIST):
                                print("Invalid choice. Try again.")
                                continue

                            inviroom, inviter, invitype = INVATATION_LIST[index]
                            response = input(f"Do you want to accept the invitation from {inviter}? (y/n): ")
                            if response.lower() == 'y':
                                accept_message = "InvitationAccept " + inviroom + "," + inviter + "," + username
                                lobby_socket.send(accept_message.encode())
                                response_message = lobby_socket.recv(1024).decode()
                                if response_message == "RoomFull" or response_message == "RoomClosed":
                                    print(f"[Invitation Response] Unable to join room: {response_message}")
                                    INVATATION_LIST.pop(index)
                                else:
                                    print("[Invitation Response] You have joined the room.")
                                    in_room_handler(inviroom, username, "client", "private", lobby_socket, invitype)
                                    INVATATION_LIST.pop(index)
                                    break
                                    
                            elif response.lower() == 'n':
                                lobby_socket.send(f"InvitationReject {inviter}".encode())
                                print("[Invitation Response] You rejected the invitation.")
                                INVATATION_LIST.pop(index)       
                        except ValueError:
                            print("Invalid input. Try again.")
            elif(choice == "7"):
                game_development_management(lobby_socket, username)
            elif(choice == "8"):
                list_game(lobby_socket, username)

                    

def main():
    """
    ---------------------------------------------------
                 A. Run the lobby server
    ---------------------------------------------------
    """
    # connect to the lobby server
    while (True):
        linux_server_num = input("Choose the lobby linux server (1~4): ")
        if (int(linux_server_num) < 1 or int(linux_server_num) > 4):
            print("The server number is invalid, please choose the valid server number")
            continue
        else:
            TCP_CLIENT_PORT = input("Enter the port number (10000~15999): ")
            if (int(TCP_CLIENT_PORT) < 10000 or int(TCP_CLIENT_PORT) > 15999):
                print("The port number is invalid, please choose the valid port number")
                continue
            else:
                try:
                    tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcp_client_socket.connect(("140.113.235.15" + linux_server_num, int(TCP_CLIENT_PORT)))
                    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    broadcast_socket.connect(("140.113.235.15" + linux_server_num, int(TCP_CLIENT_PORT)))
                    invatation_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    invatation_socket.connect(("140.113.235.15" + linux_server_num, int(TCP_CLIENT_PORT)))
                    # 啟動 broadcasting thread
                    threading.Thread(target=handle_broadcasting, args=(broadcast_socket,), daemon=True).start()

                    threading.Thread(target=invatation_append, args=(invatation_socket,), daemon=True).start()
                    break
                except ConnectionRefusedError:
                    print("The lobby server does not exit, please choose the correct server.")
                    continue
        
    """
    ===================================================
                      START SERVER
    ===================================================
    """
    while(True):
        player_choice = input("Please choose the option (1. Register 2. Login 3. Exit): ")
        if(player_choice != "1" and player_choice != "2" and player_choice != "3"):
            print("Invalid choice, please try again!")
            continue
        else:
            if(player_choice == "1"):
                """
                ---------------------------------------------------
                                    B. Register
                ---------------------------------------------------
                """
                while(True):
                    register_username = "register " + input("Enter your username: ")
                    tcp_client_socket.send(register_username.encode())

                    lobby_server_message = tcp_client_socket.recv(1024).decode()
                    if(lobby_server_message == "Username already exists."):
                        print(lobby_server_message)
                        continue
                    elif(lobby_server_message == "Enter the password: "):
                        password = input(lobby_server_message)
                        tcp_client_socket.send(password.encode())

                        lobby_server_message = tcp_client_socket.recv(1024).decode()
                        username, password = lobby_server_message.split()
                        print("=============================\n    Register successfully\n=============================")
                        print("Username:", username, "\nPassword:", password)
                        break
            elif(player_choice == "2"):
                """
                ---------------------------------------------------
                                     C. Login
                ---------------------------------------------------
                """
                username = input("Enter the username: ")
                login_username = "login " + username
                tcp_client_socket.send(login_username.encode())

                lobby_server_message = tcp_client_socket.recv(1024).decode()
                if(lobby_server_message == "User does not exist."):
                    print(lobby_server_message, "Please register first.")
                    continue
                elif(lobby_server_message == "Enter the password: "):
                    while(True):
                        password = input("Enter the password: ")
                        tcp_client_socket.send(password.encode())

                        lobby_server_message = tcp_client_socket.recv(1024).decode()
                        if(lobby_server_message == "Incorrect password."):
                            print(lobby_server_message, "Please try again.")
                            continue
                        elif(lobby_server_message == "AlreadyLoginUser"):
                            print("The user has already login. Please regesister a new user.")
                            break
                        elif(lobby_server_message == "login successfully"):
                            print("=============================\n      Login successfully\n=============================")
                            
                            while(True):
                                after_login(username, tcp_client_socket)

                                """
                                --------------------------------------------------
                                                    D. Logout
                                ---------------------------------------------------
                                """
                                
                                logout_message = "logout " + username
                                tcp_client_socket.send(logout_message.encode())

                                logout_server_message = tcp_client_socket.recv(1024).decode()
                                if (logout_server_message == "Deleting faild."):
                                    continue
                                elif (logout_server_message == "logout successfully."):
                                    print("=============================\n ", username, logout_server_message, "\n=============================")
                                    break
                            break 
            elif(player_choice == "3"):
                broadcast_socket.close()
                tcp_client_socket.close()
                return
            else:
                print("Invalid choice. Try again.")
                continue        
                
    

if __name__ == "__main__":
    main()