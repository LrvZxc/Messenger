import socket
import threading
import customtkinter as ctk
from tkinter import ttk

HOST = "127.0.0.1"
PORT = 45203

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

# Кнопка отправки
def send_msg():
    if not check_username():
        return
    msg = entry.get().strip()
    user = username.get().strip()
    if msg == "":
        return
    try:
        client.sendall(f"{user}:{msg}".encode("utf-8"))
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
# ===================== Отправить сообщение =====================
choose_tab = ctk.CTkFrame(notebook)
notebook.add(choose_tab, text="Выбор отправителя")
choosen = ""
def choose():
    choosen = id_entry.get()
id_label = ctk.CTkLabel(choose_tab, text = "напишите имя пользователя")
id_label.pack(padx=5)
id_entry = ctk.CTkEntry(choose_tab, placeholder_text="вот тут")
id_entry.pack(padx = 10)
choosewho = ctk.CTkButton(choose_tab, text = "Choose", command=choose)
choosewho.pack(padx = 20)


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

def receive_msg():
    while True:
        try:
            data = client.recv(1024).decode("utf-8")
            if data:
                sender, text = data.split(":", 1)
                app.after(0, chat_insert, text, sender)
        except:
            break

# ===================== Запуск =====================
if __name__ == "__main__":
    start_client()
    threading.Thread(target=receive_msg, daemon=True).start()
    app.mainloop()