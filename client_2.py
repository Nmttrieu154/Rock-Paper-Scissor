import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import os

# Đảm bảo chương trình chạy trong đúng thư mục chứa ảnh
os.chdir(os.path.dirname(os.path.abspath(__file__)))

DIA_CHU = "127.0.0.1"
CONG = 5555

class ClientBBK:
    def __init__(self, cua_so, tieu_de):
        self.cua_so = cua_so
        self.cua_so.title(tieu_de)
        self.cua_so.geometry("620x650")
        self.ket_noi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.ten_nguoi_choi = None

        # ===== Khung hiển thị =====
        tk.Label(cua_so, text="🎮 Búa – Bao – Kéo 🎮", font=("Helvetica", 18, "bold")).pack(pady=10)
        self.khung_tin_nhan = tk.Text(cua_so, height=15, width=70, state="disabled", bg="#f0f4f8")
        self.khung_tin_nhan.pack(pady=10)

        # ===== Khung nhập tin nhắn =====
        khung_chat = tk.Frame(cua_so)
        khung_chat.pack()
        self.nhap_tin_nhan = tk.Entry(khung_chat, width=45)
        self.nhap_tin_nhan.pack(side=tk.LEFT, padx=5)
        tk.Button(khung_chat, text="💬 Gửi", command=self.gui_tin_nhan).pack(side=tk.LEFT)

        # ===== Khung mời người chơi =====
        khung_moi = tk.Frame(cua_so)
        khung_moi.pack(pady=10)
        tk.Label(khung_moi, text="Mời người chơi:").pack(side=tk.LEFT)
        self.nhap_nguoi_moi = tk.Entry(khung_moi, width=20)
        self.nhap_nguoi_moi.pack(side=tk.LEFT, padx=5)
        tk.Button(khung_moi, text="🎯 Mời", command=self.moi_nguoi_choi).pack(side=tk.LEFT)
        tk.Button(khung_moi, text="✅ Chấp nhận", command=self.dong_y_moi).pack(side=tk.LEFT, padx=5)

        # ===== Khung chọn nước đi =====
        khung_nuoc_di = tk.Frame(cua_so)
        khung_nuoc_di.pack(pady=15)
        self.load_anh(khung_nuoc_di)

        # ===== Nút thoát =====
        tk.Button(cua_so, text="🚪 Thoát", command=self.thoat).pack(pady=5)

        # ===== Kết nối server =====
        self.ket_noi_server()

    # ===== Tải ảnh =====
    def load_anh(self, khung):
        try:
            self.anh_bua = ImageTk.PhotoImage(Image.open("img/rock.png").resize((100, 100)))
            self.anh_bao = ImageTk.PhotoImage(Image.open("img/paper.png").resize((100, 100)))
            self.anh_keo = ImageTk.PhotoImage(Image.open("img/scissors.png").resize((100, 100)))
        except Exception as e:
            messagebox.showerror("Lỗi ảnh", f"Không tìm thấy ảnh trong thư mục img/!\n{e}")
            self.cua_so.destroy()
            return

        tk.Button(khung, image=self.anh_bua, command=lambda: self.chon_nuoc_di("búa")).pack(side=tk.LEFT, padx=10)
        tk.Button(khung, image=self.anh_keo, command=lambda: self.chon_nuoc_di("kéo")).pack(side=tk.LEFT, padx=10)
        tk.Button(khung, image=self.anh_bao, command=lambda: self.chon_nuoc_di("bao")).pack(side=tk.LEFT, padx=10)

    # ===== Kết nối server =====
    def ket_noi_server(self):
        try:
            self.ket_noi.connect((DIA_CHU, CONG))
            self.ten_nguoi_choi = simpledialog.askstring("Tên người chơi", "Nhập tên của bạn:")
            if not self.ten_nguoi_choi:
                self.cua_so.destroy()
                return
            self.ket_noi.send(self.ten_nguoi_choi.encode('utf-8'))
            threading.Thread(target=self.nhan_tin_nhan, daemon=True).start()
            self.hien_thi("✅ Đã kết nối đến server.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể kết nối server:\n{e}")
            self.cua_so.destroy()

    # ===== Hiển thị tin nhắn =====
    def hien_thi(self, tin_nhan):
        self.khung_tin_nhan.config(state="normal")
        self.khung_tin_nhan.insert(tk.END, tin_nhan + "\n")
        self.khung_tin_nhan.config(state="disabled")
        self.khung_tin_nhan.see(tk.END)

    # ===== Gửi tin nhắn chat =====
    def gui_tin_nhan(self):
        tin_nhan = self.nhap_tin_nhan.get().strip()
        if tin_nhan:
            self.ket_noi.send(f"Chat:{tin_nhan}".encode('utf-8'))
            self.nhap_tin_nhan.delete(0, tk.END)

    # ===== Mời người chơi khác =====
    def moi_nguoi_choi(self):
        ten_moi = self.nhap_nguoi_moi.get().strip()
        if ten_moi:
            self.ket_noi.send(f"Invite:{ten_moi}".encode('utf-8'))
            self.nhap_nguoi_moi.delete(0, tk.END)

    # ===== Chấp nhận lời mời =====
    def dong_y_moi(self):
        self.ket_noi.send("Accept".encode('utf-8'))

    # ===== Chọn nước đi =====
    def chon_nuoc_di(self, nuoc_di):
        self.ket_noi.send(nuoc_di.encode('utf-8'))

    # ===== Nhận tin nhắn từ server =====
    def nhan_tin_nhan(self):
        while True:
            try:
                tin_nhan = self.ket_noi.recv(1024).decode('utf-8')
                if not tin_nhan:
                    break
                self.hien_thi(tin_nhan)
            except:
                break
        self.ket_noi.close()
        self.hien_thi("❌ Mất kết nối với server.")

    # ===== Thoát chương trình =====
    def thoat(self):
        self.ket_noi.close()
        self.cua_so.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientBBK(root, "🎮 Client 2 - Búa Bao Kéo")
    root.mainloop()
