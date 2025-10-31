#!/usr/bin/env python3
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
import tkinter as tk
from tkinter import messagebox, ttk
import sys
import ast

HOST = "127.0.0.1"
PORT = 33000
BUFSIZ = 2048
ADDR = (HOST, PORT)

my_name = None
current_opponent = None

# ICONS
ICON = {"rock": "✊", "paper": "✋", "scissors": "✌️"}
NAME = {"rock": "Kéo", "paper": "Búa", "scissors": "Bao"}

def receive():
    global current_opponent
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8").strip()
            if not msg: break

            if msg.startswith("[[INVITE]] "):
                inviter = msg.split()[1]
                if messagebox.askyesno("Lời mời chơi", f"{inviter} mời bạn chơi Kéo Búa Bao!\n\nĐồng ý?"):
                    client_socket.send(f"/accept {inviter}\n".encode())
                else:
                    client_socket.send(f"/decline {inviter}\n".encode())
                continue

            if msg.startswith("[[GAME_START]] "):
                p1, p2 = msg.split()[1].split(",")
                global my_name
                current_opponent = p2 if p1 == my_name else p1

                # GÁN LABEL CHO MÌNH
                if my_name not in score_labels:
                    score_labels[my_name] = lbl_my_score
                    lbl_my.config(text=f"{my_name}:")
                    del score_labels["placeholder"]

                # GÁN LABEL CHO ĐỐI THỦ
                score_labels[current_opponent] = lbl_opp_score
                lbl_opponent.config(text=f"Đối thủ: {current_opponent}")

                score_labels[my_name].config(text="0")
                score_labels[current_opponent].config(text="0")
                lbl_round.config(text="Vòng 1 / 3")
                log(f"Trận đấu bắt đầu với {current_opponent}!", "info")
                set_game_ui(True)
                continue

            if msg.startswith("[[YOU_MOVED]] "):
                mv = msg.split()[1]
                log(f"Bạn ra: {ICON[mv]} {NAME[mv]}", "move")
                continue

            # SỬA LỖI HIỂN THỊ + CỘNG ĐIỂM
            if msg.startswith("[[ROUND]] "):
                try:
                    content = msg[10:].strip()
                    parts = content.split()
                    rnd = parts[0]
                    p1, m1 = parts[1].split(":")
                    p2, m2 = parts[2].split(":")

                    result_parts = []
                    score_str = None
                    for i in range(len(parts)-1, -1, -1):
                        if parts[i].startswith("{") and parts[i].endswith("}"):
                            score_str = parts[i]
                            del parts[i]
                            break
                        else:
                            result_parts.insert(0, parts[i])

                    result = " ".join(result_parts[3:]) if len(result_parts) > 3 else ""

                    log(f"--- Vòng {rnd} ---", "round")
                    log(f"{p1}: {ICON[m1]} {NAME[m1]}", "move")
                    log(f"{p2}: {ICON[m2]} {NAME[m2]}", "move")
                    if "DRAW" in result:
                        log("HÒA!", "draw")
                    elif "WIN" in result:
                        winner = result.split(":")[1]
                        log(f"Thắng: {winner}", "win")

                    if score_str:
                        scores = ast.literal_eval(score_str)
                        for player, score in scores.items():
                            if player in score_labels:
                                score_labels[player].config(text=str(score))

                    lbl_round.config(text=f"Vòng {rnd} / 3")
                except Exception as e:
                    log(f"[Lỗi hiển thị] {e}", "info")
                continue

            if msg.startswith("[[GAME_END]] "):
                winner = msg.split()[1]
                final = " ".join(msg.split()[2:])
                log("="*35, "end")
                log(f"KẾT THÚC – Người thắng: {winner}", "win")
                log(f"Tỷ số: {final}", "end")
                log("="*35, "end")
                current_opponent = None
                set_game_ui(False)
                lbl_round.config(text="Chưa chơi")
                continue

            if msg.startswith("[[INFO]] "):
                log(msg[8:], "info")
                continue

            log(msg)
        except Exception as e:
            print("Recv error:", e)
            break

def log(txt, tag="normal"):
    msg_list.config(state=tk.NORMAL)
    msg_list.insert(tk.END, txt + "\n", tag)
    msg_list.config(state=tk.DISABLED)
    msg_list.see(tk.END)

def send_text(event=None):
    txt = my_msg.get().strip()
    my_msg.set("")
    if not txt: return
    client_socket.send((txt + "\n").encode())
    global my_name
    if my_name is None:
        my_name = txt
        log(f"Đăng nhập: {my_name}", "info")
    if txt == "{quit}":
        top.quit()

def on_close():
    try: client_socket.send("{quit}\n".encode())
    except: pass
    top.quit()

def do_invite():
    target = invite_var.get().strip()
    if not target: return
    if not target.startswith("@"):
        target = "@" + target
    if target[1:] == my_name:
        messagebox.showwarning("Lỗi", "Không thể mời chính mình!")
        return
    client_socket.send(f"/invite {target}\n".encode())
    invite_var.set("")

def do_move(m):
    if current_opponent:
        client_socket.send(f"/move {m}\n".encode())
    else:
        messagebox.showinfo("RPS", "Chưa vào trận nào!")

def set_game_ui(en):
    st = tk.NORMAL if en else tk.DISABLED
    for b in (btn_rock, btn_paper, btn_scis):
        b.config(state=st)
    if not en:
        lbl_opponent.config(text="Chưa có đối thủ")
        for lbl in score_labels.values():
            lbl.config(text="-")

# ========== GUI ==========
top = tk.Tk()
top.title("Kéo Búa Bao – Chat & Play")
top.geometry("750x580")
top.configure(bg="#f0f2f5")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)

# HEADER
hdr = tk.Frame(top, bg="#4a90e2", pady=8)
tk.Label(hdr, text="KÉO BÚA BAO", font=("Segoe UI", 16, "bold"), fg="white", bg="#4a90e2").pack()
hdr.pack(fill=tk.X)

# MAIN
main = tk.Frame(top, bg="#f0f2f5")
main.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

# CHAT
chat_f = tk.LabelFrame(main, text="Phòng Chat", font=("Segoe UI", 11, "bold"), bg="#f0f2f5")
chat_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

msg_frame = tk.Frame(chat_f, bg="white", bd=2, relief=tk.SUNKEN)
scroll = tk.Scrollbar(msg_frame)
msg_list = tk.Text(msg_frame, height=22, width=52, state=tk.DISABLED,
                   yscrollcommand=scroll.set, font=("Consolas", 10), bg="#ffffff")
scroll.pack(side=tk.RIGHT, fill=tk.Y)
msg_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
msg_frame.pack(fill=tk.BOTH, expand=True, pady=(0,6))

msg_list.tag_config("info", foreground="#2980b9")
msg_list.tag_config("move", foreground="#27ae60")
msg_list.tag_config("win",  foreground="#c0392b", font=("Consolas",10,"bold"))
msg_list.tag_config("draw", foreground="#e67e22")
msg_list.tag_config("round", foreground="#8e44ad", font=("Consolas",10,"bold"))
msg_list.tag_config("end",   foreground="#2c3e50", font=("Consolas",11,"bold"))

# GAME PANEL
game_f = tk.LabelFrame(main, text="Trận Đấu", font=("Segoe UI", 11, "bold"), bg="#f0f2f5", width=260)
game_f.pack(side=tk.RIGHT, fill=tk.Y, padx=(10,0))
game_f.pack_propagate(False)

# SCORE
score_fr = tk.Frame(game_f, bg="#f8f9fa", bd=1, relief=tk.SOLID)
score_fr.pack(fill=tk.X, pady=(0,10), padx=5)
tk.Label(score_fr, text="ĐIỂM SỐ", font=("Segoe UI",10,"bold"), bg="#f8f9fa").pack(pady=3)
lbl_round = tk.Label(score_fr, text="Chưa chơi", font=("Segoe UI",9), bg="#f8f9fa", fg="#7f8c8d")
lbl_round.pack(pady=2)

# MY SCORE
p1_fr = tk.Frame(score_fr, bg="#f8f9fa")
p1_fr.pack(fill=tk.X, pady=3)
lbl_my = tk.Label(p1_fr, text="Bạn:", font=("Segoe UI",10), bg="#f8f9fa", anchor="w")
lbl_my.pack(side=tk.LEFT, padx=5)
lbl_my_score = tk.Label(p1_fr, text="-", font=("Segoe UI",12,"bold"), bg="#f8f9fa", fg="#3498db")
lbl_my_score.pack(side=tk.RIGHT, padx=5)

# OPPONENT
p2_fr = tk.Frame(score_fr, bg="#f8f9fa")
p2_fr.pack(fill=tk.X, pady=3)
lbl_opponent = tk.Label(p2_fr, text="Chưa có đối thủ", font=("Segoe UI",10), bg="#f8f9fa", anchor="w")
lbl_opponent.pack(side=tk.LEFT, padx=5)
lbl_opp_score = tk.Label(p2_fr, text="-", font=("Segoe UI",12,"bold"), bg="#f8f9fa", fg="#e74c3c")
lbl_opp_score.pack(side=tk.RIGHT, padx=5)

score_labels = {"placeholder": lbl_my_score, "opponent": lbl_opp_score}

# INVITE
inv_fr = tk.Frame(game_f, bg="#f0f2f5")
inv_fr.pack(fill=tk.X, pady=6)
invite_var = tk.StringVar()
tk.Entry(inv_fr, textvariable=invite_var, width=12, font=("Segoe UI",9)).pack(side=tk.LEFT, padx=2)
tk.Button(inv_fr, text="Mời", command=do_invite, bg="#2ecc71", fg="white", font=("Segoe UI",9,"bold")).pack(side=tk.LEFT)

# MOVES
move_fr = tk.Frame(game_f, bg="#f0f2f5")
move_fr.pack(pady=12)
btn_rock = tk.Button(move_fr, text=f"{ICON['rock']} Kéo", font=("Segoe UI",11,"bold"), width=10, bg="#95a5a6", fg="white", command=lambda: do_move("rock"))
btn_paper = tk.Button(move_fr, text=f"{ICON['paper']} Búa", font=("Segoe UI",11,"bold"), width=10, bg="#3498db", fg="white", command=lambda: do_move("paper"))
btn_scis = tk.Button(move_fr, text=f"{ICON['scissors']} Bao", font=("Segoe UI",11,"bold"), width=10, bg="#e74c3c", fg="white", command=lambda: do_move("scissors"))
btn_rock.grid(row=0, column=0, padx=5)
btn_paper.grid(row=0, column=1, padx=5)
btn_scis.grid(row=0, column=2, padx=5)

# INPUT
inp_fr = tk.Frame(top, bg="#ecf0f1", pady=8)
inp_fr.pack(fill=tk.X, side=tk.BOTTOM)
my_msg = tk.StringVar()
my_msg.set("Nhập tên của bạn!")
entry = tk.Entry(inp_fr, textvariable=my_msg, font=("Segoe UI",10), bd=0)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(15,5), ipady=6)
entry.bind("<Return>", send_text)
tk.Button(inp_fr, text="Gửi", command=send_text, bg="#1abc9c", fg="white", font=("Segoe UI",10,"bold")).pack(side=tk.RIGHT, padx=15)

# CONNECT
client_socket = socket(AF_INET, SOCK_STREAM)
try:
    client_socket.connect(ADDR)
except:
    messagebox.showerror("Lỗi", "Không kết nối được server!")
    sys.exit()

Thread(target=receive, daemon=True).start()
set_game_ui(False)
top.protocol("WM_DELETE_WINDOW", on_close)
top.mainloop()