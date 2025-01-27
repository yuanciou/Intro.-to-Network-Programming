import socket

HOST_NAME = socket.gethostname()
HOST_IP =  "140.113.235.15" + HOST_NAME[5]
UDP_PORT = ""
TCP_IP = ""
TCP_PORT = ""

def main():
    """
    -------------------------------------------
                    UDP server
    -------------------------------------------
    """
    # choose the port of UDP
    while (True):
        UDP_PORT = input("Choose the port number of the UDP server(15000~15001): ")
        if (int(UDP_PORT) < 15000 or int(UDP_PORT) > 15001):
            print("The port number is invalid, please choose the valid port number")
            continue
        else:
            break
    
    # build the UDP server
    udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_socket.bind((HOST_IP, int(UDP_PORT)))

    # waiting for invitaion
    print("Waiting for invitaion")
    while (True):
        sent_message, addr = udp_server_socket.recvfrom(1024)
        if sent_message.decode() == "Ping waiting UDP server":
            response = "Waiting for inviting"
            udp_server_socket.sendto(response.encode(), addr)
            continue
        elif sent_message.decode() == "Game invitaion":
            print("IP:", addr[0], "Port:", addr[1], "invite you to join the game.")
            accept_invitaion = input("Do you want to accept the invitaion? [y/n]")
            if accept_invitaion == "y":
                response = "accept"
                udp_server_socket.sendto(response.encode(), addr)
                
                # get TCP ip and port number
                tcp_info, _ = udp_server_socket.recvfrom(1024)
                TCP_IP, TCP_PORT = tcp_info.decode().split()
                break
            elif accept_invitaion == "n":
                response = "reject"
                udp_server_socket.sendto(response.encode(), addr)
                continue
    
    udp_server_socket.close()

    """
    -------------------------------------------
                    TCP client
    -------------------------------------------
    """
    # server connecting
    tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client_socket.connect((TCP_IP, int(TCP_PORT)))

    """
    -------------------------------------------
                   Game Playing
    -------------------------------------------
    """
    print("Start Rock-Paper-Scissors")
    while (True):
        B_action = input("Please choose your action? [rock/paper/scissors]")
        tcp_client_socket.send(B_action.encode())
        
        A_action = tcp_client_socket.recv(1024).decode()
        print("Player A choose", A_action)

        if (A_action == B_action):
            print("It's a tie.")
            continue
        elif ((A_action == "rock" and B_action == "scissors") or (A_action == "paper" and B_action == "rock") or (A_action == "scissors" and B_action == "paper")):
            print("You lose.")
            break
        else:
            print("You win.")
            break

    tcp_client_socket.close()

if __name__ == "__main__":
    main()