import socket
import threading
import json

HOST = "127.0.0.1"
PORT = 45203

clients = []
users = {}
def handle_msg(conn, msg):
    if msg["message"].strip() == "":
        return     
    for client in clients:
        if client != conn:
            client.sendall(json.dumps(msg).encode("utf-8"))
              
                         
  
def handle_update_userlist(conn, nickname):
    users[conn] = nickname
    for client in clients:
        client.sendall(json.dumps({
            "type": "users",
            "users": list(users.values())
        }).encode("utf-8"))
                    

def handle_client(conn, addr):
    print(f"[+] {addr} подключился")
    clients.append(conn)



    while True:
        
        
        try:
            msg_bytes = conn.recv(1024)
            if not msg_bytes:
                
                break
            

            msg = msg_bytes.decode("utf-8")
            message = json.loads(msg)
            
            if message["type"] == "message":
                handle_msg(conn, message)
            elif message["type"] == "usernametoadd":
                nickname = message["username"]
                handle_update_userlist(conn, nickname)


            
  
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

