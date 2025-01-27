def playgame(host_client, connect_socket):
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