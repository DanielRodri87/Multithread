import socket
import threading

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345
MAX_CLIENTS = 3

clients = {}
client_threads = []  # Lista para armazenar as threads dos clientes
server = None
is_running = False

def update_client_list():
    user_list = "Usuários online: " + ", ".join(clients.values())
    disconnected_clients = []  # Lista para armazenar soquetes desconectados

    for client in clients:
        try:
            client.send(user_list.encode('utf-8'))
        except OSError:
            # Se o envio falhar, adiciona o cliente à lista de desconectados
            disconnected_clients.append(client)

    # Remove os clientes desconectados do dicionário de clientes
    for client in disconnected_clients:
        del clients[client]

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
    
    # Verifica se o cliente ainda está no dicionário antes de remover
    if client_socket in clients:
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
    global server, is_running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(MAX_CLIENTS)
    is_running = True
    print(f"[INICIADO] Servidor escutando em {SERVER_HOST}:{SERVER_PORT}")

    while is_running:
        try:
            client_socket, client_address = server.accept()
            
            if len(clients) >= MAX_CLIENTS:
                print(f"[CHEIO] Conexão recusada para {client_address}. Limite de clientes atingido.")
                client_socket.close()
                continue

            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_threads.append(client_thread)  # Adiciona a thread à lista
            client_thread.start()
        except:
            break

def stop_server():
    global is_running
    is_running = False
    for client_socket in list(clients.keys()):
        client_socket.close()
    for thread in client_threads:
        thread.join()  # Espera as threads dos clientes finalizarem
    clients.clear()
    client_threads.clear()
    if server:
        server.close()
    print("[ENCERRADO] Servidor foi encerrado.")

def main_menu():
    while True:
        print("\nMenu:")
        print("1. Iniciar servidor")
        print("2. Encerrar servidor")
        print("3. Sair")
        choice = input("Escolha uma opção: ")

        if choice == "1":
            if not is_running:
                threading.Thread(target=start_server).start()
            else:
                print("[AVISO] O servidor já está em execução.")
        elif choice == "2":
            if is_running:
                stop_server()
            else:
                print("[AVISO] O servidor já está encerrado.")
        elif choice == "3":
            if is_running:
                stop_server()
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main_menu()
