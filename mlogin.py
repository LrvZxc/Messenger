import psycopg2
import customtkinter as ctk
from tkinter import ttk
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.geometry("750x600")
app.title("Login Tab")
login_tab = ctk.CTkFrame(app)
switch = ctk.CTkButton(app, text="Go to Chat", command=lambda: [login_tab.pack_forget()])
login_tab.pack(pady=20, padx=60, fill="both", expand=True)
switch.pack(pady=10)





app.mainloop()
