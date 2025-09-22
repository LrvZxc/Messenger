import socket
import threading
import json

HOST = "127.0.0.1"
PORT = 45203

clients = []
users = {}
def handle_msg(conn, msg):
    if msg.strip() == "":
      
        return
    for client in clients:
        if client != conn:
            client.sendall(msg.encode("utf-8"))
              
                         
                    

def handle_client(conn, addr):
    print(f"[+] {addr} подключился")
    clients.append(conn)
    users[conn] = "default" 
    userlit = json.dumps(list(users.values())).encode()  #Может надо будет переделать отправку сообщений под json чтобы сервак различал 
    for i in clients:
        i.sendall(userlit)                                                          # Сообщение и Список пользователей
    while True:
        
        
        try:
            msg_bytes = conn.recv(1024)
            if not msg_bytes:
                
                break


            msg = msg_bytes.decode("utf-8")
            handle_msg(conn, msg)
        except Exception as e:
            print("Ошибочка: ", e)
            break
    print(f"[-] {addr} отключился")
    if conn in clients:
        print("Удаление клиента из списка клиентов")
        clients.remove(conn)
    print("закрытие соединения клиента")
    conn.close()
   
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
   
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()
        

if __name__ == "__main__":
    start_server()

