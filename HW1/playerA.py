import socket

HOST_NAME = socket.gethostname()
HOST_IP =  "140.113.235.15" + HOST_NAME[5]
HOST_LIST = ["140.113.235.151", "140.113.235.152", "140.113.235.153", "140.113.235.154"]
TCP_SERVER_PORT = "16006"

def main():
    """
    -------------------------------------------
                    UDP client
    -------------------------------------------
    """
    udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while (True): # if player B reject the invitation, re-searching
        # searching the waiting UDP server
        print("Searching the waiting server")
        for host_addr in HOST_LIST:
            for port_num in range (15000, 15002): # set in the UDP server
                udp_client_socket.settimeout(1) # for searching (if the ip and port doesn't exit)

                sent_message = "Ping waiting UDP server"
                udp_client_socket.sendto(sent_message.encode(), (host_addr, port_num))

                # !! use try, except here to handle the condition which ip and port doesn't exit
                try:
                    response, addr = udp_client_socket.recvfrom(1024) # addr is a list [IP, port]
                    if response.decode() == "Waiting for inviting":
                        print("IP:", addr[0], "Port:", addr[1], "is waiting for invitation.")
                except socket.timeout:
                    pass
        # remove the setting of timeout
        udp_client_socket.settimeout(None)

        # sending the invitaion
        chosen_ip = input("Input the IP you want to choose: ")
        chosen_port = input("Input the port number you want to choose: ")
        print("Sending invitaion to player B")
        sent_game_invi = "Game invitaion"
        udp_client_socket.sendto(sent_game_invi.encode(), (chosen_ip, int(chosen_port)))
        game_accept, game_addr = udp_client_socket.recvfrom(1024)
        if game_accept.decode() == "accept":
            print("Player B accept the game")

            # send tcp server info to tcp client to set up connection
            tcp_server_info = HOST_IP + " " + TCP_SERVER_PORT
            udp_client_socket.sendto(tcp_server_info.encode(), (chosen_ip, int(chosen_port)))
            break
        elif game_accept.decode() == "reject":
            print("Player B reject the game")
            continue
        
    """
    -------------------------------------------
                    TCP server
    -------------------------------------------
    """
    # build the TCP server
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.bind((HOST_IP, int(TCP_SERVER_PORT)))
    tcp_server_socket.listen(1) # accept 1 socket connection
    print("Waiting for TCP connection.")

    tcp_client, _ = tcp_server_socket.accept()
    print("Successfully connected by", tcp_client)

    """
    -------------------------------------------
                   Game Playing
    -------------------------------------------
    """
    print("Start Rock-Paper-Scissors")
    while (True):
        A_action = input("Please choose your action? [rock/paper/scissors]")
        tcp_client.send(A_action.encode())
        
        B_action = tcp_client.recv(1024).decode()
        print("Player B choose", B_action)

        if (A_action == B_action):
            print("It's a tie.")
            continue
        elif ((A_action == "rock" and B_action == "scissors") or (A_action == "paper" and B_action == "rock") or (A_action == "scissors" and B_action == "paper")):
            print("You win.")
            break
        else:
            print("You lose.")
            break
    
    tcp_client.close()
    udp_client_socket.close()
    tcp_server_socket.close()

if __name__ == "__main__":
    main()