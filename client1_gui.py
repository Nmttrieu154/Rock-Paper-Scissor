import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import os
import pygame
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

DIA_CHI = "127.0.0.1"  # Thay bằng ngrok khi chơi online
CONG = 5555

pygame.mixer.init()

class ClientBBK:
    def __init__(self, cua_so, tieu_de):
        self.cua_so = cua_so
        self.cua_so.title(tieu_de)
        self.cua_so.geometry("620x680")
        self.ket_noi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ten_nguoi_choi = None
        self.nut_bua = None
        self.nut_bao = None
        self.nut_keo = None

        # === GIAO DIỆN ===
        tk.Label(cua_so, text="Búa – Bao – Kéo", font=("Helvetica", 18, "bold"), fg="#d62828").pack(pady=10)
        
        self.khung_tin_nhan = tk.Text(cua_so, height=15, width=70, state="disabled", bg="#f8f9fa", font=("Arial", 10))
        self.khung_tin_nhan.pack(pady=10)

        khung_chat = tk.Frame(cua_so)
        khung_chat.pack(pady=5)
        self.nhap_tin_nhan = tk.Entry(khung_chat, width=45)
        self.nhap_tin_nhan.pack(side=tk.LEFT, padx=5)
        tk.Button(khung_chat, text="Gửi", command=self.gui_tin_nhan, bg="#4361ee", fg="white").pack(side=tk.LEFT)

        khung_moi = tk.Frame(cua_so)
        khung_moi.pack(pady=8)
        tk.Label(khung_moi, text="Mời:").pack(side=tk.LEFT)
        self.nhap_nguoi_moi = tk.Entry(khung_moi, width=20)
        self.nhap_nguoi_moi.pack(side=tk.LEFT, padx=5)
        tk.Button(khung_moi, text="Mời", command=self.moi_nguoi_choi, bg="#2d6a4f", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(khung_moi, text="Chấp nhận", command=self.dong_y_moi, bg="#9b2226", fg="white").pack(side=tk.LEFT, padx=2)

        khung_nuoc_di = tk.Frame(cua_so)
        khung_nuoc_di.pack(pady=15)
        self.load_anh(khung_nuoc_di)

        self.khung_lich_su = tk.LabelFrame(cua_so, text="Lịch sử trận đấu", font=("Arial", 10, "bold"))
        self.khung_lich_su.pack(pady=10, fill=tk.X, padx=20)
        self.lich_su_text = tk.Text(self.khung_lich_su, height=3, state="disabled", bg="#e9ecef")
        self.lich_su_text.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(cua_so, text="Thoát", command=self.thoat, bg="#6c757d", fg="white").pack(pady=5)

        self.ket_noi_server()

    def load_anh(self, khung):
        try:
            self.anh_bua = ImageTk.PhotoImage(Image.open("img/rock.png").resize((100, 100)))
            self.anh_bao = ImageTk.PhotoImage(Image.open("img/paper.png").resize((100, 100)))
            self.anh_keo = ImageTk.PhotoImage(Image.open("img/scissors.png").resize((100, 100)))
        except Exception as e:
            messagebox.showerror("Lỗi ảnh", f"Không tìm thấy ảnh trong thư mục img/!\n{e}")
            self.cua_so.destroy()
            return

        self.nut_bua = tk.Button(khung, image=self.anh_bua, command=lambda: self.chon_nuoc_di("búa"))
        self.nut_keo = tk.Button(khung, image=self.anh_keo, command=lambda: self.chon_nuoc_di("kéo"))
        self.nut_bao = tk.Button(khung, image=self.anh_bao, command=lambda: self.chon_nuoc_di("bao"))

        self.nut_bua.pack(side=tk.LEFT, padx=15)
        self.nut_keo.pack(side=tk.LEFT, padx=15)
        self.nut_bao.pack(side=tk.LEFT, padx=15)

    def nhap_nhay_thang(self, nut):
        def blink(count=6):
            if count <= 0: return
            nut.config(bg="#52b788" if count % 2 else "", relief=tk.SUNKEN if count % 2 else tk.RAISED)
            self.cua_so.after(300, blink, count-1)
        blink()

    def phat_am_thanh_thang(self):
        try:
            if os.path.exists("sound/win.mp3"):
                pygame.mixer.music.load("sound/win.mp3")
                pygame.mixer.music.play()
        except:
            pass

    def ket_noi_server(self):
        try:
            self.ket_noi.connect((DIA_CHI, CONG))
            self.ten_nguoi_choi = simpledialog.askstring("Tên", "Nhập tên của bạn:")
            if not self.ten_nguoi_choi:
                self.cua_so.destroy()
                return
            self.ket_noi.send(self.ten_nguoi_choi.encode('utf-8'))
            threading.Thread(target=self.nhan_tin_nhan, daemon=True).start()
            self.hien_thi("Đã kết nối đến server.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể kết nối server:\n{e}")
            self.cua_so.destroy()

    def hien_thi(self, tin):
        self.khung_tin_nhan.config(state="normal")
        self.khung_tin_nhan.insert(tk.END, tin + "\n")
        self.khung_tin_nhan.config(state="disabled")
        self.khung_tin_nhan.see(tk.END)

    def cap_nhat_lich_su(self, ket_qua):
        try:
            with open("history.txt", "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%H:%M %d/%m')}] {ket_qua}\n")
            with open("history.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()[-3:]
            self.lich_su_text.config(state="normal")
            self.lich_su_text.delete(1.0, tk.END)
            self.lich_su_text.insert(tk.END, "".join(lines))
            self.lich_su_text.config(state="disabled")
        except:
            pass

    def gui_tin_nhan(self):
        tin = self.nhap_tin_nhan.get().strip()
        if tin:
            self.ket_noi.send(f"Chat:{tin}".encode('utf-8'))
            self.nhap_tin_nhan.delete(0, tk.END)

    def moi_nguoi_choi(self):
        ten = self.nhap_nguoi_moi.get().strip()
        if ten:
            self.ket_noi.send(f"Invite:{ten}".encode('utf-8'))
            self.nhap_nguoi_moi.delete(0, tk.END)
        else:
            messagebox.showwarning("Lỗi", "Vui lòng nhập tên người chơi!")

    def dong_y_moi(self):
        self.ket_noi.send("Accept".encode('utf-8'))

    def chon_nuoc_di(self, nuoc_di):
        self.ket_noi.send(nuoc_di.encode('utf-8'))

    def nhan_tin_nhan(self):
        while True:
            try:
                tin = self.ket_noi.recv(1024).decode('utf-8')
                if not tin: break

                self.hien_thi(tin)

                # === POP-UP KHI MỜI ===
                if "Đã gửi lời mời đến" in tin:
                    ten_moi = tin.split("đến")[-1].strip().rstrip(".")
                    messagebox.showinfo("Mời chơi", f"Đã gửi lời mời đến {ten_moi}!")

                elif "không tồn tại" in tin or "chưa online" in tin:
                    messagebox.showerror("Lỗi mời", tin)

                # === POP-UP KHI ĐƯỢC MỜI ===
                elif "mời bạn chơi" in tin:
                    ten_moi = tin.split(" ")[0]
                    if messagebox.askyesno("Lời mời chơi", f"{ten_moi} mời bạn chơi!\n\nChấp nhận?"):
                        self.dong_y_moi()
                    else:
                        self.ket_noi.send("Reject".encode('utf-8'))

                # === POP-UP KẾT QUẢ ===
                elif "thắng!" in tin or "Hòa!" in tin:
                    self.cap_nhat_lich_su(tin)
                    if self.ten_nguoi_choi in tin:
                        self.phat_am_thanh_thang()
                        if "búa" in tin: self.nhap_nhay_thang(self.nut_bua)
                        elif "bao" in tin: self.nhap_nhay_thang(self.nut_bao)
                        elif "kéo" in tin: self.nhap_nhay_thang(self.nut_keo)
                    messagebox.showinfo("Kết quả", tin)

            except Exception as e:
                break
        self.ket_noi.close()
        self.hien_thi("Mất kết nối với server.")

    def thoat(self):
        try:
            self.ket_noi.close()
        except:
            pass
        self.cua_so.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientBBK(root, "Client - Búa Bao Kéo")
    root.mainloop()