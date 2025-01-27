import socket

# Utility function to check if a number has unique digits
def has_unique_digits(number):
    return len(set(number)) == len(number)

# Host sets up the game and waits for the client's guess
def host_game():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = int(input("Enter the port number (10000~15999): "))
    server_socket.bind(('140.113.235.151', port))
    server_socket.listen(1)
    print("Waiting for a player to connect...")
    conn, addr = server_socket.accept()
    print(f"Player connected from {addr}")

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
        guess = conn.recv(1024).decode()
        print(f"\nClient guessed: {guess}")
        rounds += 1

        if len(guess) != 4 or not has_unique_digits(guess):
            conn.send("Invalid input. The number must be 4 unique digits.".encode())
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

        conn.send(f"{A}A{B}B".encode())
        
        if A == 4:
            conn.send(f"Congratulations! You guessed the number in {rounds} rounds.".encode())
            game_over = True

    conn.close()

# Client attempts to guess the host's number
def client_game():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_port = int(input("Enter the host port: "))
    client_socket.connect(('140.113.235.151', host_port))
    print("Connected to the host.")

    game_over = False

    while not game_over:
        guess = input("Enter your 4-digit guess with unique digits: ")
        if len(guess) != 4 or not has_unique_digits(guess):
            print("Invalid input. The number must be 4 unique digits. Try again.")
            continue

        client_socket.send(guess.encode())
        response = client_socket.recv(1024).decode()
        print("Host response:", response)
        
        if "Congratulations!" in response:
            game_over = True

    client_socket.close()

# Main function to choose the game mode
def main():
    mode = input("Choose mode: (1) Host a game, (2) Join a game: ")
    if mode == '1':
        host_game()
    elif mode == '2':
        client_game()
    else:
        print("Invalid mode. Choose 1 or 2.")

if __name__ == "__main__":
    main()
