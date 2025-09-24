import socket
import threading
import customtkinter as ctk
from tkinter import ttk
import json

HOST = "127.0.0.1"
PORT = 45203
userslist = []

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("750x600")
app.title("Chat Client")

# Notebook для вкладок
notebook = ttk.Notebook(app)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# ===================== Вкладка Чат =====================
chat_tab = ctk.CTkFrame(notebook)
notebook.add(chat_tab, text="Чат")

# Никнейм
username_frame = ctk.CTkFrame(chat_tab)
username_frame.pack(pady=10)

username_label = ctk.CTkLabel(username_frame, text="Введите никнейм:")
username_label.pack(side="left", padx=5)

username = ctk.CTkEntry(username_frame, width=250)
username.pack(side="left", padx=5)

warning = ctk.CTkLabel(chat_tab, text="", text_color="red")
warning.pack(pady=5)
warning.pack_forget()


def check_username():
    name = username.get().strip()
    if len(name) > 17:
        warning.configure(text="Никнейм не должен быть длиннее 17 символов")
        warning.pack()
        return False
    elif len(name) < 3:
        warning.configure(text="Никнейм не должен быть короче 3 символов")
        warning.pack()
        return False
    warning.pack_forget()
    username.configure(state="disabled")
    submit.configure(state="disabled")
    client.sendall(json.dumps({
        "type": "usernametoadd",
        "username": name
    }).encode("utf-8"))
    print(f"Отправлено {name}")
    return True


submit = ctk.CTkButton(chat_tab, text="Submit", command=check_username)
submit.pack(pady=5)

# Чат
chat = ctk.CTkTextbox(chat_tab, width=700, height=350)
chat.pack(pady=10)
chat.configure(state="disabled")

# Поле ввода сообщения
entry = ctk.CTkEntry(chat_tab, placeholder_text="Введите сообщение...", width=500)
entry.pack(side="left", padx=10, pady=5)


# Отправка общего сообщения
def send_msg():
    if not check_username():
        return
    msg = entry.get().strip()
    user = username.get().strip()
    if msg == "":
        return
    try:
        client.sendall(json.dumps({
            "type": "message",
            "username": user,
            "message": msg
        }).encode("utf-8"))
        chat.configure(state="normal")
        chat.insert("end", f"{user}: {msg}\n")
        chat.configure(state="disabled")
        entry.delete(0, "end")
        chat.see("end")
    except:
        print("Соединение с сервером потеряно")


send = ctk.CTkButton(chat_tab, text="Send", command=send_msg)
send.pack(side="left", pady=5)

app.bind("<Return>", lambda event: send_msg())

# ===================== Личные сообщения =====================
choose_tab = ctk.CTkFrame(notebook)
personal_chat = ctk.CTkTextbox(choose_tab, width=400, height=300)
personal_chat.pack(pady=10)

notebook.add(choose_tab, text="ЛС")
choosen = ""


def choose():
    global choosen
    choosen = id_entry.get().strip()
    print(f"Выбран получатель: {choosen}")


id_label = ctk.CTkLabel(choose_tab, text="Введите имя пользователя для ЛС")
id_label.pack(padx=5)

id_entry = ctk.CTkEntry(choose_tab, placeholder_text="Никнейм")
id_entry.pack(padx=10)

choosewho = ctk.CTkButton(choose_tab, text="Choose", command=choose)
choosewho.pack(padx=20)

# Поле для личного сообщения
personal_entry = ctk.CTkEntry(choose_tab, placeholder_text="Введите личное сообщение...", width=300)
personal_entry.pack(pady=5)


def send_personal_msg():
    if not check_username():
        return
    msg = personal_entry.get().strip()
    user = username.get().strip()
    if msg == "" or choosen == "":
        return
    try:
        client.sendall(json.dumps({
            "type": "personal_message",
            "username": user,
            "message": msg,
            "to": choosen
        }).encode("utf-8"))
        personal_chat.configure(state="normal")
        personal_chat.insert("end", f"{user} to {choosen}: {msg}\n")
        personal_chat.configure(state="disabled")
        personal_entry.delete(0, "end")
        personal_chat.see("end")
    except:
        print("Соединение с сервером потеряно")


send_personal_btn = ctk.CTkButton(choose_tab, text="Send Personal", command=send_personal_msg)
send_personal_btn.pack(pady=5)

# ===================== Socket =====================
client = None


def start_client():
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))


def chat_insert(text, sender):
    chat.configure(state="normal")
    chat.insert("end", f"{sender}: {text}\n")
    chat.configure(state="disabled")
    chat.see("end")


def receive_users(data):
    global userslist
    userslist = json.loads(data)
    print("Текущие пользователи:", userslist)


def receive_msg():
    while True:
        try:
            data = client.recv(1024).decode("utf-8")
            data = json.loads(data)
            if data["type"] == "message":
                sender = data["username"]
                text = data["message"]
                app.after(0, chat_insert, text, sender)

            elif data["type"] == "message_from_server":
                personal_chat.configure(state="normal")
                personal_chat.insert("end", f'{data["from"]} to {data["to"]}: {data["message"]}\n')
                personal_chat.configure(state="disabled")
                personal_chat.see("end")

            elif data["type"] == "users":
                users_data = json.dumps(data["users"])
                app.after(0, receive_users, users_data)
        except:
            break


# ===================== Запуск =====================
if __name__ == "__main__":
    personal_chat.configure(state="disabled")
    start_client()
    threading.Thread(target=receive_msg, daemon=True).start()
    app.mainloop()
