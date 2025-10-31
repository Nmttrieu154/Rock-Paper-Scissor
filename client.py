#!/usr/bin/env python3
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
import tkinter as tk
from tkinter import messagebox

HOST = "127.0.0.1"
PORT = 33000
BUFSIZ = 2048
ADDR = (HOST, PORT)

my_name = None
current_opponent = None

def receive():
    global current_opponent
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8").strip()
            if not msg:
                break

            if msg.startswith("[[INVITE]] "):
                inviter = msg.split()[1]
                if messagebox.askyesno("Lời mời", f"{inviter} mời chơi, đồng ý?"):
                    client_socket.send(f"/accept {inviter}".encode())
                else:
                    client_socket.send(f"/decline {inviter}".encode())
                continue

            if msg.startswith("[[GAME_START]] "):
                players = msg.split()[1]
                p1, p2 = players.split(",")
                global my_name
                current_opponent = p2 if p1 == my_name else p1
                lbl_game.config(text=f"Đang chơi với: {current_opponent}")
                set_game_ui(True)
                continue

            if msg.startswith("[[YOU_MOVED]] "):
                log("(Bạn đã chọn) " + msg.split()[1])
                continue

            if msg.startswith("[[ROUND]] "):
                log(msg)
                continue

            if msg.startswith("[[GAME_END]] "):
                log(msg)
                current_opponent = None
                set_game_ui(False)
                continue

            if msg.startswith("[[INFO]] "):
                log(msg)
                continue

            log(msg)
        except:
            break

def log(t):
    msg_list.insert(tk.END, t)
    msg_list.yview(tk.END)

def send_text(event=None):
    msg = my_msg.get().strip()
    my_msg.set("")
    if not msg:
        return
    client_socket.send((msg + "\n").encode())
    global my_name
    if my_name is None:
        my_name = msg  # dòng đầu là tên
    if msg == "{quit}":
        top.quit()

def on_close():
    my_msg.set("{quit}")
    send_text()

def do_invite():
    t = invite_var.get().strip()
    if t:
        client_socket.send(f"/invite @{t}".encode())

def do_move(m):
    if current_opponent:
        client_socket.send(f"/move {m}".encode())
    else:
        messagebox.showinfo("RPS", "Chưa trong ván nào")

def set_game_ui(en):
    st = tk.NORMAL if en else tk.DISABLED
    for b in (btn_rock, btn_paper, btn_scis):
        b.config(state=st)
    if not en:
        lbl_game.config(text="Chưa trong ván nào")

# ===== GUI =====
top = tk.Tk()
top.title("Chat + Kéo Búa Bao")

messages_frame = tk.Frame(top)
scrollbar = tk.Scrollbar(messages_frame)
msg_list = tk.Listbox(messages_frame, height=18, width=60, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
msg_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
messages_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

game_frame = tk.Frame(top)
lbl_game = tk.Label(game_frame, text="Chưa trong ván nào")
lbl_game.pack(side=tk.LEFT, padx=6)
invite_var = tk.StringVar()
tk.Entry(game_frame, textvariable=invite_var, width=14).pack(side=tk.LEFT, padx=4)
tk.Button(game_frame, text="Mời chơi", command=do_invite).pack(side=tk.LEFT, padx=4)
btn_rock = tk.Button(game_frame, text="Kéo", command=lambda: do_move("rock"))
btn_paper = tk.Button(game_frame, text="Búa", command=lambda: do_move("paper"))
btn_scis = tk.Button(game_frame, text="Bao", command=lambda: do_move("scissors"))
btn_rock.pack(side=tk.LEFT)
btn_paper.pack(side=tk.LEFT, padx=2)
btn_scis.pack(side=tk.LEFT)
game_frame.pack(pady=4)

entry_frame = tk.Frame(top)
my_msg = tk.StringVar()
my_msg.set("Nhập tên của bạn!")
entry_field = tk.Entry(entry_frame, textvariable=my_msg, width=50)
entry_field.bind("<Return>", send_text)
entry_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(entry_frame, text="Gửi", command=send_text).pack(side=tk.LEFT, padx=4)
entry_frame.pack(fill=tk.X, padx=6, pady=6)

top.protocol("WM_DELETE_WINDOW", on_close)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)
Thread(target=receive, daemon=True).start()
set_game_ui(False)
top.mainloop()
