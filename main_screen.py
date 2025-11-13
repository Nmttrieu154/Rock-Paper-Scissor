# main_menu.py
import tkinter as tk
from tkinter import messagebox
from game_screen import GameScreen

class MainMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Búa Bao Kéo Online")
        self.root.geometry("500x600")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)
        self.show_menu()
        self.root.mainloop()

    def show_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        canvas = tk.Canvas(self.root, width=500, height=600, bg="#1a1a2e", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_text(250, 120, text="BÚA – BAO – KÉO", font=("Helvetica", 28, "bold"), fill="#ff6b6b")
        canvas.create_text(250, 250, text="Nhập tên của bạn:", font=("Arial", 12), fill="white")
        self.entry_ten = tk.Entry(canvas, font=("Arial", 14), width=20, justify="center", bd=0, relief="flat",
                                  highlightthickness=2, highlightcolor="#4ecdc4", insertbackground="white")
        canvas.create_window(250, 290, window=self.entry_ten)
        btn_vao = tk.Button(canvas, text="VÀO CHƠI", font=("Arial", 12, "bold"), bg="#4ecdc4", fg="white",
                            command=self.vao_tro_choi, width=20, height=2, relief="flat", cursor="hand2")
        canvas.create_window(250, 360, window=btn_vao)
        btn_thoat = tk.Button(canvas, text="THOÁT", font=("Arial", 10), bg="#ee5a52", fg="white",
                              command=self.root.destroy, width=15, height=1, relief="flat", cursor="hand2")
        canvas.create_window(250, 420, window=btn_thoat)
        def hover_in(e): e.widget.config(bg="#45b7a0")
        def hover_out(e): e.widget.config(bg="#4ecdc4")
        btn_vao.bind("<Enter>", hover_in)
        btn_vao.bind("<Leave>", hover_out)
        self.entry_ten.focus()
        self.entry_ten.bind("<Return>", lambda e: self.vao_tro_choi())

    def vao_tro_choi(self):
        ten = self.entry_ten.get().strip()
        if not ten:
            messagebox.showwarning("Lỗi", "Vui lòng nhập tên!", parent=self.root)
            return
        if len(ten) > 15:
            messagebox.showwarning("Lỗi", "Tên tối đa 15 ký tự!", parent=self.root)
            return
        self.root.withdraw()
        GameScreen(ten, self.root)

if __name__ == "__main__":
    MainMenu()