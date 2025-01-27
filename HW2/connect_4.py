# import socket
# import threading

# # Game board setup
# ROWS = 6
# COLUMNS = 7

# def create_board():
#     return [[' ' for _ in range(COLUMNS)] for _ in range(ROWS)]

# def print_board(board):
#     for row in board:
#         print(' | '.join(row))
#         print('-' * (COLUMNS * 4 - 1))

# def board_to_string(board):
#     return '\n'.join([' | '.join(row) for row in board]) + '\n' + '-' * (COLUMNS * 4 - 1)

# def is_valid_location(board, col):
#     return board[0][col] == ' '

# def get_next_open_row(board, col):
#     for r in range(ROWS-1, -1, -1):
#         if board[r][col] == ' ':
#             return r

# def drop_piece(board, row, col, piece):
#     board[row][col] = piece

# def check_win(board, piece):
#     # Check horizontal, vertical, and diagonal locations for a win
#     for r in range(ROWS):
#         for c in range(COLUMNS - 3):
#             if all(board[r][c + i] == piece for i in range(4)):
#                 return True

#     for r in range(ROWS - 3):
#         for c in range(COLUMNS):
#             if all(board[r + i][c] == piece for i in range(4)):
#                 return True

#     for r in range(ROWS - 3):
#         for c in range(COLUMNS - 3):
#             if all(board[r + i][c + i] == piece for i in range(4)):
#                 return True

#     for r in range(3, ROWS):
#         for c in range(COLUMNS - 3):
#             if all(board[r - i][c + i] == piece for i in range(4)):
#                 return True

#     return False

# # Thread for listening for incoming messages
# def listen_for_moves(server_socket, board, opponent_piece, turn_control):
#     while True:
#         try:
#             data = server_socket.recv(1024).decode()
#             if data.startswith("MOVE"):
#                 col = int(data.split()[1])
#                 row = get_next_open_row(board, col)
#                 drop_piece(board, row, col, opponent_piece)
#                 print("\nOpponent's move:")
#                 print_board(board)

#                 if check_win(board, opponent_piece):
#                     print(f"Player {opponent_piece} wins!")
#                     turn_control["game_over"] = True
#                     break

#                 # Change turn after opponent's move
#                 turn_control["is_my_turn"] = True  # Ensure this switches to true after receiving a move
#         except Exception as e:
#             print(f"Error: {e}")
#             break

# # Main P2P function
# def main():
#     board = create_board()
#     player_piece = 'X'
#     opponent_piece = 'O'
#     game_over = False
#     turn_control = {"is_my_turn": True}  # Host starts the game

#     mode = input("Choose mode: (1) Host a game, (2) Join a game: ")

#     if mode == '1':
#         # Host a game (player 'X')
#         while True:
#             port = input("Choose the port number of the lobby server (10000~15999): ")
#             if int(port) < 10000 or int(port) > 15999:
#                 print("The port number is invalid, please choose a valid port number.")
#                 continue
#             else:
#                 try:
#                     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                     server_socket.bind(('140.113.235.151', int(port)))
#                     break
#                 except OSError:
#                     print("The port number is not available, try another one.")
#                     continue
        
#         server_socket.listen(1)
#         print("Waiting for a player to connect...")
#         conn, addr = server_socket.accept()
#         print(f"Player connected from {addr}")

#         threading.Thread(target=listen_for_moves, args=(conn, board, opponent_piece, turn_control)).start()

#         while not game_over:
#             if turn_control["is_my_turn"]:
#                 try:
#                     col = int(input("Enter the column number (0-6): "))
#                     if col < 0 or col >= COLUMNS:
#                         print("Invalid column. Please choose a number between 0 and 6.")
#                         continue
                    
#                     if is_valid_location(board, col):
#                         row = get_next_open_row(board, col)
#                         drop_piece(board, row, col, player_piece if mode == '1' else opponent_piece)
#                         print_board(board)

#                         # Send the move to the other player
#                         conn.send(f"MOVE {col}".encode()) if mode == '1' else client_socket.send(f"MOVE {col}".encode())

#                         if check_win(board, player_piece if mode == '1' else opponent_piece):
#                             print("You win!")
#                             game_over = True
#                             (conn if mode == '1' else client_socket).send("WIN".encode())

#                         turn_control["is_my_turn"] = False  # Switch turn to the opponent
#                     else:
#                         print("Column is full. Try a different column.")
#                 except ValueError:
#                     print("Invalid input. Please enter a number between 0 and 6.")

#         conn.close()

#     elif mode == '2':
#         # Join a game (player 'O')
#         client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         host_port = input("Enter the host port: ")
#         client_socket.connect(('140.113.235.151', int(host_port)))
#         print("Connected to the host.")

#         threading.Thread(target=listen_for_moves, args=(client_socket, board, player_piece, turn_control)).start()

#         while not game_over:
#             if turn_control["is_my_turn"]:
#                 try:
#                     col = int(input("Enter the column number (0-6): "))
#                     if col < 0 or col >= COLUMNS:
#                         print("Invalid column. Please choose a number between 0 and 6.")
#                         continue
                    
#                     if is_valid_location(board, col):
#                         row = get_next_open_row(board, col)
#                         drop_piece(board, row, col, player_piece if mode == '1' else opponent_piece)
#                         print_board(board)

#                         # Send the move to the other player
#                         conn.send(f"MOVE {col}".encode()) if mode == '1' else client_socket.send(f"MOVE {col}".encode())

#                         if check_win(board, player_piece if mode == '1' else opponent_piece):
#                             print("You win!")
#                             game_over = True
#                             (conn if mode == '1' else client_socket).send("WIN".encode())

#                         turn_control["is_my_turn"] = False  # Switch turn to the opponent
#                     else:
#                         print("Column is full. Try a different column.")
#                 except ValueError:
#                     print("Invalid input. Please enter a number between 0 and 6.")

#         client_socket.close()

# if __name__ == "__main__":
#     main()
import socket

# Game board setup
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
            col = int(input("Enter the column number (0-6): "))
            if col < 0 or col >= COLUMNS:
                print("Invalid column. Please choose a number between 0 and 6.")
                return False  # Stay on the current turn

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
        if data.startswith("MOVE"):
            col = int(data.split()[1])
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, 'O' if piece == 'X' else 'X')
            print("\nOpponent's move:")
            print_board(board)

            if check_win(board, 'O' if piece == 'X' else 'X'):
                print("Opponent wins!")
                return True  # Game over

        return True if data == "WIN" else False  # Switch turn if not a win

def main():
    board = create_board()
    player_piece = 'X'
    opponent_piece = 'O'
    game_over = False
    is_my_turn = True  # Host starts first

    mode = input("Choose mode: (1) Host a game, (2) Join a game: ")

    if mode == '1':
        port = int(input("Choose the port number of the lobby server (10000~15999): "))
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('140.113.235.151', port))
        server_socket.listen(1)
        print("Waiting for a player to connect...")
        conn, addr = server_socket.accept()
        print(f"Player connected from {addr}")

        while not game_over:
            game_over = play_turn(conn, board, player_piece, is_my_turn)
            is_my_turn = not is_my_turn  # Toggle the turn

        conn.close()

    elif mode == '2':
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_port = int(input("Enter the host port: "))
        client_socket.connect(('140.113.235.151', host_port))
        print("Connected to the host.")

        is_my_turn = False  # Joiner moves second

        while not game_over:
            game_over = play_turn(client_socket, board, opponent_piece, is_my_turn)
            is_my_turn = not is_my_turn  # Toggle the turn

        client_socket.close()

if __name__ == "__main__":
    main()
