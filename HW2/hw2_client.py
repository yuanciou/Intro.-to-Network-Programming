import socket
import time

HOST_NAME = socket.gethostname()
HOST_IP =  "140.113.235.15" + HOST_NAME[5]

def game_1A2B(host_client, connect_socket):
    def has_unique_digits(number):
        return len(set(number)) == len(number)
    def host_game():
        # Host sets up the number after the connection is established
        while True:
            secret_number = input("Host, enter a 4-digit number with unique digits: ")
            if len(secret_number) == 4 and has_unique_digits(secret_number):
                break
            else:
                print("Invalid input. The number must be 4 digits with unique digits. Try again.")
        
        rounds = 0
        game_over = False

        while not game_over:
            guess = connect_socket.recv(1024).decode()
            print(f"\nClient guessed: {guess}")
            rounds += 1

            if len(guess) != 4 or not has_unique_digits(guess):
                connect_socket.send("Invalid input. The number must be 4 unique digits.".encode())
                continue
            
            # Host manually inputs the number of A's and B's
            while True:
                try:
                    A = int(input("Enter the number of A's (correct digits in the correct positions): "))
                    B = int(input("Enter the number of B's (correct digits in the wrong positions): "))
                    if 0 <= A <= 4 and 0 <= B <= 4 and A + B <= 4:
                        break
                    else:
                        print("Invalid A and B values. Make sure they are within valid range and A + B <= 4.")
                except ValueError:
                    print("Invalid input. Please enter integers only.")

            connect_socket.send(f"{A}A{B}B".encode())
            
            if A == 4:
                connect_socket.send(f" Congratulations! You guessed the number in {rounds} rounds.".encode())
                game_over = True

        #conn.close()
    def client_game():
        game_over = False

        while not game_over:
            guess = input("Enter your 4-digit guess with unique digits: ")
            if len(guess) != 4 or not has_unique_digits(guess):
                print("Invalid input. The number must be 4 unique digits. Try again.")
                continue

            connect_socket.send(guess.encode())
            response = connect_socket.recv(1024).decode()
            print("Host response:", response)
            
            if "Congratulations!" in response:
                game_over = True
    
    if(host_client == "host"):
        host_game()
    elif(host_client == "client"):
        client_game()


def connect_four_game(host_client, connect_socket):
    ROWS = 6
    COLUMNS = 7

    def create_board():
        return [[' ' for _ in range(COLUMNS)] for _ in range(ROWS)]
    def print_board(board):
        for row in board:
            print(' | '.join(row))
            print('-' * (COLUMNS * 4 - 1))
    def is_valid_location(board, col):
        return board[0][col] == ' '
    def get_next_open_row(board, col):
        for r in range(ROWS-1, -1, -1):
            if board[r][col] == ' ':
                return r
    def drop_piece(board, row, col, piece):
        board[row][col] = piece
    def check_win(board, piece):
        for r in range(ROWS):
            for c in range(COLUMNS - 3):
                if all(board[r][c + i] == piece for i in range(4)):
                    return True

        for r in range(ROWS - 3):
            for c in range(COLUMNS):
                if all(board[r + i][c] == piece for i in range(4)):
                    return True

        for r in range(ROWS - 3):
            for c in range(COLUMNS - 3):
                if all(board[r + i][c + i] == piece for i in range(4)):
                    return True

        for r in range(3, ROWS):
            for c in range(COLUMNS - 3):
                if all(board[r - i][c + i] == piece for i in range(4)):
                    return True

        return False
    def play_turn(connection, board, piece, is_my_turn):
        if is_my_turn:
            try:
                while True:
                    col = int(input("Enter the column number (0-6): "))
                    if col < 0 or col >= COLUMNS:
                        print("Invalid column. Please choose a number between 0 and 6.")
                        continue  # Stay on the current turn

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, piece)
                        print_board(board)

                        # Send the move to the opponent
                        connection.send(f"MOVE {col}".encode())

                        if check_win(board, piece):
                            print("You win!")
                            connection.send("WIN".encode())
                            return True  # Game over

                        return False  # Switch turn to the opponent
                    else:
                        print("Column is full. Try a different column.")
                        return False  # Stay on the current turn
            except ValueError:
                print("Invalid input. Please enter a number between 0 and 6.")
                return False  # Stay on the current turn
        else:
            print("\nWaiting for opponent's move...")
            data = connection.recv(1024).decode()

            if data == "WIN":
                print("Opponent wins!")
                return True  # Game over

            if data.startswith("MOVE"):
                try:
                    col = int(data.split()[1])
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, 'O' if piece == 'X' else 'X')
                    print("\nOpponent's move:")
                    print_board(board)
                except (ValueError, IndexError) as e:
                    print(f"Error processing move: {e}")
                    return False  # Invalid data, stay on current turn

            return False  # Continue playing if no "WIN" signal
        
    """
    ========================================
                  Connect four
    ========================================
    """
    
    board = create_board()
    player_piece = 'X'
    opponent_piece = 'O'
    game_over = False
    is_my_turn = True  # Host starts first

    if host_client == "host":
    
        while not game_over:
            game_over = play_turn(connect_socket, board, player_piece, is_my_turn)
            is_my_turn = not is_my_turn  # Toggle the turn

        return
        #connect_socket.close()

    elif host_client == "client":
        is_my_turn = False  # Joiner moves second

        while not game_over:
            game_over = play_turn(connect_socket, board, opponent_piece, is_my_turn)
            is_my_turn = not is_my_turn  # Toggle the turn

        return
        #connect_socket.close()

def after_login(username, lobby_socket):
    while(True):
        choice = input("Please choose the option (1. Logout 2. List rooms 3. Create a new room 4. Join room): ")
        if(choice != "1" and choice != "2" and choice != "3" and choice != "4"):
            print("Invalid choice, please try again!")
            continue
        else:
            if(choice == "1"):
                return
            elif(choice == "2"):
                """
                           Invitation and List Room
                --------------------------------------------                
                """
                message = "ListRoom tmp"
                lobby_socket.send(message.encode())

                while(True):
                    lobby_socket.settimeout(6.0)
                    try:
                        time.sleep(1)
                        invitaion_listroom = lobby_socket.recv(1024).decode()
                        print(invitaion_listroom)
                        invi_list, item = invitaion_listroom.split()
                        if(invi_list == "RoomInviting"):
                            lobby_socket.settimeout(None)
                            while(True):
                                print("Whould you want to accept the invitation from " + item + " (1. Yes 2. No)?")
                                response = input()
                                if(response == "1"):
                                    message = "InvitationAccept"
                                    lobby_socket.send(message.encode())

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
                                    if(gametype == "Connect_4"):
                                        connect_four_game("client", private_client_socket)
                                    elif(gametype == "1A2B"):
                                        game_1A2B("client", private_client_socket)
                                    print("\nGAME FINISH")
                                    private_client_socket.close()
                                    break
                                elif(response == "2"):
                                    message = "InvitationReject"
                                    lobby_socket.send(message.encode())
                                    break
                                else:
                                    print("Invalid reponse, try again.")
                                    continue
                        elif(invi_list == "ListRoom"):
                            roomlist = item.split(";")
                            if(">" not in item):
                                print("No public rooms waiting for players.\n")
                            else: 
                                print("Public Rooms:")
                                for roomstatus in roomlist:
                                    if(">" in roomstatus):
                                        roomname, room_i = roomstatus.split(">")
                                        roominfo = room_i.split(",")
                                        print("Name:", roomname, "Type:", roominfo[0], "Owner:", roominfo[2], "Status:", roominfo[3])
                            print()
                            continue
                    except socket.timeout:
                        lobby_socket.settimeout(None)
                        break
                        
            elif(choice == "3"):
                """
                ---------------------------------------------------
                            F. Create a game room
                ---------------------------------------------------
                """
                create_room = []
                print("\n    Room Creating\n---------------------")
                while(True):
                    create_room.clear()
                    create_room.append(input("Please enter the room name: "))
                    create_room.append(input("Please enter the game type (1. 1A2B 2. Connect Four): "))
                    create_room.append(input("Please enter the room type (1. Public 2. Private): "))
                    if(create_room[1] == "1"):
                        create_room[1] = "1A2B"
                    elif(create_room[1] == "2"):
                        create_room[1] = "Connect_4"
                    
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
                                    print("Set up server. Waiting for other player...")
                                    break
                                except OSError:  # the port is not available
                                    print("The port number is not available, try another one.")
                                    continue
                        
                        lobby_request_message = lobby_socket.recv(1024).decode()
                        if(lobby_request_message == "PublicRequestIpPort"):
                            lobby_respose_message = HOST_IP + " " + p2p_port
                            lobby_socket.send(lobby_respose_message.encode())
                        
                        public_room_owner_socket.listen(1)
                        public_client, public_client_addr = public_room_owner_socket.accept()
                        print("Connect by", public_client_addr)

                        """
                        !!!!!!!!!!!!!!!!!!! GAME START
                        """
                        # delete the public room
                        # user->idle
                        if(create_room[1] == "Connect_4"):
                            connect_four_game("host", public_client)
                        elif(create_room[1] == "1A2B"):
                            game_1A2B("host", public_client)
                        public_client.close()
                        public_room_owner_socket.close()
                        print("\nGAME FINISH")

                        # delete the private room

                        dele_public_room_message = "DelPublicRoom" + " " + create_room[0] + " " + username
                        lobby_socket.send(dele_public_room_message.encode())
                        
                        break
                        
                    elif(room_valid_message == "Creat Room Successfully." and create_room[2] == "Private"):
                        """
                                        Private room
                        --------------------------------------------                
                        """
                        print("Inviting the player...")
                        message = "RequestIdlePlayer tmp"
                        lobby_socket.send(message.encode())
                        
                        time.sleep(1)
                        private_lobby_message = lobby_socket.recv(1024).decode()
                        work_type, job = private_lobby_message.split(">")
                        idleplayers = []
                        invite_user = ""
                        if(work_type == "IdlePlayer"):
                            idleplayers = job.split()
                            print("\nIdle Player List:")
                            for idleplayer in idleplayers:
                                print(idleplayer)
                        
                        while(True):
                            invitation_accept = False
                            private_choice = input("Enter the choice (1. List Player 2. Invite Player): ")
                            
                            if(private_choice == "1"):
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
                            elif(private_choice == "2"):
                                while(True):
                                    invite_user = input("Enter the inviting username: ")
                                    if(invite_user not in idleplayers):
                                        print("The invited user is invalid, try again.")
                                        break
                                    message = "InviteUser " + invite_user + "," + username
                                    lobby_socket.send(message.encode())

                                    time.sleep(1)
                                    player_reponse = lobby_socket.recv(1024).decode()
                                    if(player_reponse == "InvitationReject"):
                                        break
                                    elif(player_reponse == "InvitationAccept"):
                                        invitation_accept = True
                                        break
                            else:
                                print("Invalid choice. Try again.")
                            if(invitation_accept == True):
                                break
                        
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
                        if(create_room[1] == "Connect_4"):
                            connect_four_game("host", private_client)
                        elif(create_room[1] == "1A2B"):
                            game_1A2B("host", private_client)
                        private_client.close()
                        private_room_owner_socket.close()
                        print("\nGAME FINISH")

                        # delete the private room

                        dele_private_room_message = "DelPrivateRoom" + " " + create_room[0] + " " + invite_user + " " + username
                        lobby_socket.send(dele_private_room_message.encode())
                        break
            elif(choice == "4"):
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
                    public_ip, public_port, public_game_type = lobby_join_message.split()
                    public_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    public_client_socket.connect((public_ip, int(public_port)))
                    """
                    !!!!!!!!!!!!!!!!!!! GAME START
                    """
                    if(public_game_type == "Connect_4"):
                        connect_four_game("client", public_client_socket)
                    elif(public_game_type == "1A2B"):
                        game_1A2B("client", public_client_socket)
                    print("\nGAME FINISH")
                    public_client_socket.close()

                    # delet_public_client = "DelPubClient " + username
                    # lobby_socket.send(delet_public_client.encode())
                    

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
                        else:
                            print("=============================\n      Login successfully\n=============================")
                            """
                                --------------------------------------------------
                                            E. Display the online status
                                ---------------------------------------------------
                            """
                            userstring, roomstring = lobby_server_message.split(";")
                            userlist = userstring.split()
                            roomlist = roomstring.split()

                            # online player status
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
                            
                            # Room status
                            if(len(roomlist) == 0):
                                print("\nNo public rooms waiting for players.\n")
                            else: 
                                print("Public Rooms:")
                                for roomstatus in roomlist:
                                    if(">" in roomstatus):
                                        roomname, room_i = roomstatus.split(">")
                                        roominfo = room_i.split(",")
                                        print("Name:", roomname, "Type:", roominfo[0], "Owner:", roominfo[2], "Status:", roominfo[3])
                            print() 
                            
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
                return
            else:
                print("Invalid choice. Try again.")
                continue        
                
    

if __name__ == "__main__":
    main()