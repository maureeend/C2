import socket
import subprocess
import os

ip_add = "127.0.0.1"
port = 3280

# Bind and listen socket
def listen_socket(s):
    s.bind((ip_add, port))
    s.listen(5)

# Accepter le socket
def accept_socket(s):
    print(f"Listening on {ip_add}:{port}")
    conn, address = s.accept()
    print(f"New connection from {address} !")
    send_command(conn)
    conn.close()

# Envoyer une commande
def send_command(conn):
    while True:
        
        command = input("> ")

        if command.lower() == "exit":
            print("Closing connection.")
            conn.close()
            break

        # Envoi de la commande
        conn.send(command.encode("utf-8"))

        # Réception du résultat
        result = conn.recv(4096).decode("utf-8", errors="replace") 
        print(result)  # Affichage du résultat côté serveur
        


if __name__ == "__main__":
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket(s)
        accept_socket(s)
    except:
        print(f"cannot listen on port : {port}")




   
