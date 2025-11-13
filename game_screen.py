# game_screen.py
import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import os
import pygame
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))
DIA_CHI = "127.0.0.1"
CONG = 5555
pygame.mixer.init()

class GameScreen:
    def __init__(self, ten_nguoi_choi, root_menu):
        self.ten_nguoi_choi = ten_nguoi_choi
        self.root_menu = root_menu
        self.root = tk.Toplevel(root_menu)
        self.root.title("Búa Bao Kéo Online")
        self.root.geometry("720x820")
        self.root.configure(bg="#16213e")
        self.root.protocol("WM_DELETE_WINDOW", self.ve_menu)
        self.ket_noi = None
        self.doi_thu = None
        self.dang_choi = False
        self.nut = [None, None, None]
        self.trang_thai_tran = "cho"
        self.van_hien_tai = 0

        if not self.ket_noi_server():
            self.ve_menu()
            return
        self.build_game_screen()

    def ket_noi_server(self):
        try:
            self.ket_noi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ket_noi.connect((DIA_CHI, CONG))
            self.ket_noi.send(self.ten_nguoi_choi.encode('utf-8'))
            threading.Thread(target=self.nhan_tin_nhan, daemon=True).start()
            return True
        except Exception as e:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối server!\n{e}", parent=self.root)
            self.ve_menu()
            return False

    def build_game_screen(self):
        header = tk.Frame(self.root, bg="#0f3460", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="BÚA – BAO – KÉO", font=("Helvetica", 20, "bold"), fg="#e8f0f2", bg="#0f3460").pack(side=tk.LEFT, padx=20, pady=15)
        tk.Label(header, text=f"Chào: {self.ten_nguoi_choi}", font=("Arial", 11), fg="#a2d2ff", bg="#0f3460").pack(side=tk.RIGHT, padx=20, pady=15)

        main = tk.Frame(self.root, bg="#16213e")
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        status_frame = tk.Frame(main, bg="#16213e")
        status_frame.pack(pady=(0, 10), fill=tk.X)
        self.lbl_van = tk.Label(status_frame, text="Ván: 0/3", font=("Arial", 14, "bold"), fg="#4ecdc4", bg="#16213e")
        self.lbl_van.pack(side=tk.LEFT, padx=10)
        # ĐÃ XÓA lbl_diem HOÀN TOÀN

        msg_frame = tk.LabelFrame(main, text="Trạng thái trận đấu", font=("Arial", 11, "bold"), bg="#1f4068", fg="#e8f0f2", bd=2)
        msg_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.khung_tin = tk.Text(msg_frame, height=12, state="disabled", bg="#1a1a2e", fg="#e8f0f2", font=("Consolas", 10))
        self.khung_tin.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        chat_frame = tk.Frame(main, bg="#16213e")
        chat_frame.pack(fill=tk.X, pady=5)
        self.nhap_chat = tk.Entry(chat_frame, font=("Arial", 10), bg="#1a1a2e", fg="white", insertbackground="white")
        self.nhap_chat.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.nhap_chat.bind("<Return>", lambda e: self.gui_chat())
        tk.Button(chat_frame, text="Gửi", command=self.gui_chat, bg="#4ecdc4", fg="white", font=("Arial", 9, "bold")).pack(side=tk.RIGHT)

        action_frame = tk.Frame(main, bg="#16213e")
        action_frame.pack(pady=10)
        self.btn_moi = tk.Button(action_frame, text="MỜI CHƠI", command=self.moi_nguoi_choi, bg="#2d6a4f", fg="white", font=("Arial", 10, "bold"), width=14)
        self.btn_moi.pack(side=tk.LEFT, padx=5)
        self.lbl_trang_thai = tk.Label(action_frame, text="Chưa có đối thủ", fg="#a2d2ff", bg="#16213e", font=("Arial", 10))
        self.lbl_trang_thai.pack(side=tk.LEFT, padx=20)
        # ĐÃ XÓA NÚT CHƠI LẠI

        play_frame = tk.LabelFrame(main, text="Chọn nước đi", font=("Arial", 11, "bold"), bg="#1f4068", fg="#e8f0f2")
        play_frame.pack(fill=tk.X, pady=10)
        self.load_nuoc_di(play_frame)

        history_frame = tk.LabelFrame(main, text="Lịch sử 3 trận gần nhất", font=("Arial", 10, "bold"), bg="#1f4068", fg="#e8f0f2")
        history_frame.pack(fill=tk.X, pady=10)
        self.lich_su = tk.Text(history_frame, height=3, state="disabled", bg="#1a1a2e", fg="#a2d2ff", font=("Consolas", 9))
        self.lich_su.pack(fill=tk.X, padx=8, pady=8)

        tk.Button(main, text="Thoát về Menu", command=self.ve_menu, bg="#ee5a52", fg="white", font=("Arial", 9, "bold")).pack(pady=5)
        self.hien_thi("Đã kết nối đến server.")

    def load_nuoc_di(self, khung):
        try:
            self.anh_bua = ImageTk.PhotoImage(Image.open("img/rock.png").resize((85, 85)))
            self.anh_bao = ImageTk.PhotoImage(Image.open("img/paper.png").resize((85, 85)))
            self.anh_keo = ImageTk.PhotoImage(Image.open("img/scissors.png").resize((85, 85)))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không tìm thấy ảnh!\n{e}", parent=self.root)
            self.ve_menu()
            return
        btn_bua = tk.Button(khung, image=self.anh_bua, command=lambda: self.chon("búa"), bg="#1f4068", relief="flat", state="disabled")
        btn_keo = tk.Button(khung, image=self.anh_keo, command=lambda: self.chon("kéo"), bg="#1f4068", relief="flat", state="disabled")
        btn_bao = tk.Button(khung, image=self.anh_bao, command=lambda: self.chon("bao"), bg="#1f4068", relief="flat", state="disabled")
        btn_bua.pack(side=tk.LEFT, expand=True, padx=15, pady=10)
        btn_keo.pack(side=tk.LEFT, expand=True, padx=15, pady=10)
        btn_bao.pack(side=tk.LEFT, expand=True, padx=15, pady=10)
        self.nut = [btn_bua, btn_keo, btn_bao]

    def chon(self, nuoc):
        if not self.dang_choi: return
        self.ket_noi.send(nuoc.encode('utf-8'))
        for nut in self.nut:
            if nut is not None:
                nut.config(state="disabled")

    def nhap_nhay(self, nut):
        def blink(n=8):
            if n <= 0 or nut is None: return
            nut.config(bg="#ffd43b" if n % 2 else "#1f4068")
            self.root.after(250, blink, n-1)
        blink()

    def nhap_nhay_tat_ca_nut(self):
        for nut in self.nut:
            if nut is not None:
                self.nhap_nhay(nut)

    def phat_am_thanh(self):
        try:
            if os.path.exists("sound/win.mp3"):
                pygame.mixer.music.load("sound/win.mp3")
                pygame.mixer.music.play()
        except: pass

    def gui_chat(self):
        msg = self.nhap_chat.get().strip()
        if msg:
            self.ket_noi.send(f"Chat:{msg}".encode('utf-8'))
            self.nhap_chat.delete(0, tk.END)

    def moi_nguoi_choi(self):
        ten = simpledialog.askstring("Mời chơi", "Nhập tên đối thủ:", parent=self.root)
        if ten and ten != self.ten_nguoi_choi:
            self.ket_noi.send(f"Invite:{ten}".encode('utf-8'))
        elif ten == self.ten_nguoi_choi:
            messagebox.showwarning("Lỗi", "Không thể mời chính mình!", parent=self.root)

    def ve_menu(self):
        try: self.ket_noi.close()
        except: pass
        self.root.destroy()
        self.root_menu.deiconify()

    def hien_thi(self, tin):
        if hasattr(self, 'khung_tin') and self.khung_tin.winfo_exists():
            self.khung_tin.config(state="normal")
            self.khung_tin.insert(tk.END, tin + "\n")
            self.khung_tin.config(state="disabled")
            self.khung_tin.see(tk.END)

    def cap_nhat_lich_su_tu_file(self):
        try:
            if os.path.exists("history.txt"):
                with open("history.txt", "r", encoding="utf-8") as f:
                    lines = [line for line in f.readlines() if "thắng trận" in line][-3:]
                self.lich_su.config(state="normal")
                self.lich_su.delete(1.0, tk.END)
                self.lich_su.insert(tk.END, "".join(lines))
                self.lich_su.config(state="disabled")
        except: pass

    def cap_nhat_van(self):
        self.lbl_van.config(text=f"Ván: {self.van_hien_tai}/3")
        self.root.update_idletasks()

    def nhan_tin_nhan(self):
        while True:
            try:
                tin = self.ket_noi.recv(1024).decode('utf-8')
                if not tin: break
                self.hien_thi(tin)

                if tin.startswith("Đối thủ: "):
                    self.doi_thu = tin.split(": ")[1]
                    self.lbl_trang_thai.config(text=f"Đang chơi với: {self.doi_thu}", fg="#ffd43b")
                    self.btn_moi.config(state="disabled")

                elif "Ván" in tin and "/3" in tin:
                    if not self.doi_thu: continue
                    try:
                        van = int(tin.split()[1].split('/')[0])
                        self.van_hien_tai = van
                        self.cap_nhat_van()
                        if van == 1:
                            self.dang_choi = True
                            self.trang_thai_tran = "choi"
                            for nut in self.nut:
                                if nut is not None:
                                    nut.config(state="normal")
                    except: pass

                elif "Trận đấu bắt đầu" in tin:
                    self.lbl_trang_thai.config(text=f"Đang chơi với: {self.doi_thu}", fg="#ffd43b")
                    self.dang_choi = True
                    self.trang_thai_tran = "choi"

                elif "mời bạn chơi" in tin:
                    ten_moi = tin.split(" ")[0]
                    if messagebox.askyesno("Lời mời", f"{ten_moi} mời bạn chơi!\nChấp nhận?", parent=self.root):
                        self.ket_noi.send("Accept".encode('utf-8'))
                    else:
                        self.ket_noi.send("Reject".encode('utf-8'))

                elif "*** THẮNG TRẬN" in tin:
                    self.trang_thai_tran = "ket_thuc"
                    self.dang_choi = False
                    for nut in self.nut:
                        if nut is not None:
                            nut.config(state="disabled")
                    if self.ten_nguoi_choi in tin:
                        self.phat_am_thanh()
                        self.nhap_nhay_tat_ca_nut()
                    messagebox.showinfo("KẾT THÚC", tin, parent=self.root)
                    self.root.after(100, self.cap_nhat_lich_su_tu_file)
                    self.lbl_trang_thai.config(text="Trận kết thúc! Đang chờ chơi lại...", fg="#a2d2ff")
                    # TỰ ĐỘNG GỬI CHƠI LẠI
                    self.ket_noi.send("Chơi lại".encode('utf-8'))

                elif "Bạn đã chọn chơi lại" in tin:
                    self.lbl_trang_thai.config(text="Đang chờ đối thủ chơi lại...", fg="#ffd43b")

                elif "muốn chơi lại!" in tin:
                    self.lbl_trang_thai.config(text=tin, fg="#ffd43b")

                elif "Cả hai đã đồng ý! Bắt đầu lại" in tin:
                    self.lbl_trang_thai.config(text=f"Đang chơi với: {self.doi_thu}", fg="#ffd43b")
                    self.dang_choi = True
                    self.trang_thai_tran = "choi"
                    self.van_hien_tai = 1
                    self.cap_nhat_van()

                elif "->" in tin and ("thắng!" in tin or "Hòa!" in tin):
                    if self.ten_nguoi_choi in tin:
                        self.phat_am_thanh()
                        try:
                            idx = ["búa", "bao", "kéo"].index(tin.split(":")[1].split()[0])
                            self.nhap_nhay(self.nut[idx])
                        except: pass
                    messagebox.showinfo("Kết quả ván", tin, parent=self.root)
                    if self.trang_thai_tran == "choi":
                        for nut in self.nut:
                            if nut is not None:
                                nut.config(state="normal")

            except Exception as e:
                print("Lỗi nhận tin:", e)
                break
        self.hien_thi("Mất kết nối. Về menu...")
        self.ve_menu()