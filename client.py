import socket
import threading

# Configurações do servidor
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

# Função para receber mensagens do servidor
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(message)
        except:
            print("['ERRO] Conexão com o servidor perdida.")
            client_socket.close()
            break

# Função principal para iniciar o cliente
def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    # Inicia thread para receber mensagens
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Loop para enviar mensagens ao servidor
    while True:
        message = input("Digite sua mensagem ou '@nome_usuario Mensagem' para mensagem privada: ")
        if message.lower() == 'sair':
            print("[DESCONECTANDO] Encerrando a conexão.")
            client_socket.close()
            break
        client_socket.send(message.encode('utf-8'))

# Inicia o cliente
if __name__ == "__main__":
    start_client()
