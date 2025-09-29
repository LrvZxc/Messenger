import customtkinter as ctk
from tkinter import ttk
import socket
import threading
import json

HOST = "127.0.0.1"
PORT = 45203

# ===================== Класс для одной вкладки чата =====================
class ChatTab(ctk.CTkFrame):
    def __init__(self, master, title="Общий Чат"):
        super().__init__(master)
        self.title = title
        self.client = None
        self.choosen = ""
        self.userslist = []

        # Никнейм
        self.username_frame = ctk.CTkFrame(self)
        self.username_frame.pack(pady=5)

        self.username_label = ctk.CTkLabel(self.username_frame, text="Введите никнейм:")
        self.username_label.pack(side="left", padx=5)

        self.username = ctk.CTkEntry(self.username_frame, width=250)
        self.username.pack(side="left", padx=5)

        self.warning = ctk.CTkLabel(self, text="", text_color="red")
        self.warning.pack(pady=5)
        self.warning.pack_forget()

        self.submit = ctk.CTkButton(self, text="Submit", command=self.check_username)
        self.submit.pack(pady=5)

        # Чат
        self.chat = ctk.CTkTextbox(self, width=500, height=200)
        self.chat.pack(pady=10)
        self.chat.configure(state="disabled")

        # Поле ввода сообщения
        self.entry = ctk.CTkEntry(self, placeholder_text="Введите сообщение...", width=300)
        self.entry.pack(side="left", padx=5)

        self.send_btn = ctk.CTkButton(self, text="Send", command=self.send_msg)
        self.send_btn.pack(side="left", padx=5)

        # Личные сообщения
        threading.Thread(target=self.receive_personal_msg, daemon=True).start()


        self.id_entry = ctk.CTkEntry(self, placeholder_text="Никнейм для ЛС")
        self.id_entry.pack(padx=5)

        self.choose_btn = ctk.CTkButton(self, text="Choose", command=self.choose)
        self.choose_btn.pack(padx=5)

        

       
        # Socket
        self.start_client()
        threading.Thread(target=self.receive_msg, daemon=True).start()

    # ===== Методы =====
    def check_username(self):
        name = self.username.get().strip()
        if len(name) > 17:
            self.warning.configure(text="Никнейм не должен быть длиннее 17 символов")
            self.warning.pack()
            return False
        elif len(name) < 3:
            self.warning.configure(text="Никнейм не должен быть короче 3 символов")
            self.warning.pack()
            return False
        self.warning.pack_forget()
        self.username.configure(state="disabled")
        self.submit.configure(state="disabled")
        self.client.sendall(json.dumps({"type": "usernametoadd", "username": name}).encode("utf-8"))
        return True

    def receive_personal_msg(self):
        data = self.client.recv(1024).decode("utf-8")
        while True:
            try:
               
                dataa = json.loads(data)
                if data["type"] == "personal_message":
                    new_cchat = PersonalChatTab(self.master, self.client, dataa["to"], dataa["username"], title=f"ЛС с {dataa['username']}")
                    self.master.add(new_cchat, text=f"ЛС с {dataa['username']}")
                    sender = dataa["username"]
                    recipient = dataa["to"]
                    message = dataa["message"]
                    new_cchat.personal_chat.configure(state="normal")
                    new_cchat.personal_chat.insert("end", f"{sender} to {recipient}: {message}\n")
                    new_cchat.personal_chat.configure(state="disabled")
                    new_cchat.personal_chat.see("end")  #добавить бы чтобы вообщем клиент писал и у другого клиента появлялся чат с этим клиентом
            except:
                break
    def send_msg(self):
        if not self.check_username():
            return
        msg = self.entry.get().strip()
        user = self.username.get().strip()
        if msg == "":
            return
        try:
            self.client.sendall(json.dumps({"type": "message", "username": user, "message": msg}).encode("utf-8"))
            self.chat.configure(state="normal")
            self.chat.insert("end", f"{user}: {msg}\n")
            self.chat.configure(state="disabled")
            self.entry.delete(0, "end")
            self.chat.see("end")
        except:
            print("Соединение с сервером потеряно")

    def choose(self):
        self.choosen = self.id_entry.get().strip()
        if not self.choosen:
            return

    # Создаём новую вкладку для ЛС
        personal_tab = PersonalChatTab(self.master, self.client, self.username, self.id_entry, title=f"ЛС с {self.choosen}")
        self.master.add(personal_tab, text=f"ЛС с {self.choosen}")
        self.master.select(personal_tab)

        print(f"Выбран получатель: {self.choosen}")
    

    def start_client(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((HOST, PORT))

    def receive_msg(self):
        while True:
            try:
                data = self.client.recv(1024).decode("utf-8")
                data = json.loads(data)
                if data["type"] == "message":
                    sender = data["username"]
                    text = data["message"]
                    self.after(0, self.chat_insert, text, sender)
            except:
                break

    def chat_insert(self, text, sender):
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{sender}: {text}\n")
        self.chat.configure(state="disabled")
        self.chat.see("end")





# ===================== Класс для вкладки ЛС =====================
class PersonalChatTab(ctk.CTkFrame):
    def __init__(self, master, client, username_entry, choosen_entry, title="Лс С кем-то"):
        super().__init__(master)
        
        self.client = client                
        self.username_entry = username_entry  
        self.choosen_entry = choosen_entry 

        #Сам чат, текст бокс с которым надо работать 

        self.personal_chat = ctk.CTkTextbox(self, width=400, height=150)
        self.personal_chat.pack(pady=5)
        self.personal_chat.configure(state="disabled")
        self.personal_entry = ctk.CTkEntry(self, placeholder_text="Введите ЛС", width=200)
        self.personal_entry.pack(pady=5)

        # Кнопка отправки ЛС
        self.send_personal_btn = ctk.CTkButton(self, text="Send Personal", command=self.send_personal_msg)
        self.send_personal_btn.pack(pady=5)

        
    def send_personal_msg(self):
        user = self.username_entry.get().strip()
        choosen = self.choosen_entry.get().strip()
        msg = self.personal_entry.get().strip()

        if not user or not msg: 
            return

        try:
            self.client.sendall(json.dumps({
                "type": "personal_message",
                "username": user,
                "message": msg,
                "to": choosen
            }).encode("utf-8"))

            self.personal_chat.configure(state="normal")
            self.personal_chat.insert("end", f"{user} to {choosen}: {msg}\n")
            self.personal_chat.configure(state="disabled")
            self.personal_entry.delete(0, "end")
            self.personal_chat.see("end")
        except:
            print("Соединение с сервером потеряно")

    


# ===================== Главный класс приложения =====================
class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x700")
        self.title("Multi Chat Client")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)


    

# ===================== Запуск =====================
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = MainApp()
    app.mainloop()
