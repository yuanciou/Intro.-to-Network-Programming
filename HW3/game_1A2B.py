def playgame(host_client, connect_socket):
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