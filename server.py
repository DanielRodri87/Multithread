import socket
import threading

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345
MAX_CLIENTS = 3

clients = {}

def update_client_list():
    user_list = "Usuários online: " + ", ".join(clients.values())
    for client in clients:
        client.send(user_list.encode('utf-8'))

def handle_client(client_socket, client_address):
    client_socket.send("Escolha um nome de usuário: ".encode('utf-8'))
    client_name = client_socket.recv(1024).decode('utf-8')
    clients[client_socket] = client_name
    print(f"[CONEXÃO] {client_name} conectado com o endereço {client_address}")
    
    update_client_list()

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            
            if message.startswith("@"):
                target_name, private_message = message[1:].split(" ", 1)
                send_private_message(client_socket, target_name, private_message)
            else:
                client_socket.send("Para enviar uma mensagem privada, use o formato '@nome_usuario Mensagem'.".encode('utf-8'))
        except:
            break

    print(f"[DESCONECTADO] {client_name} desconectado.")
    del clients[client_socket]
    client_socket.close()
    update_client_list()

def send_private_message(sender_socket, target_name, message):
    sender_name = clients[sender_socket]
    for client_socket, client_name in clients.items():
        if client_name == target_name:
            client_socket.send(f"[PRIVADO de {sender_name}]: {message}".encode('utf-8'))
            return
    sender_socket.send(f"Usuário '{target_name}' não encontrado.".encode('utf-8'))

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(MAX_CLIENTS)
    print(f"[INICIADO] Servidor escutando em {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, client_address = server.accept()
        
        if len(clients) >= MAX_CLIENTS:
            print(f"[CHEIO] Conexão recusada para {client_address}. Limite de clientes atingido.")
            client_socket.close()
            continue

        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()

if __name__ == "__main__":
    start_server()