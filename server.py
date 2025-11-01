import socket
import threading

# ====== CẤU HÌNH ======
DIA_CHI = "0.0.0.0"
CONG = 5555

# ====== DANH SÁCH NGƯỜI CHƠI ======
danh_sach_client = {}          # {client_socket: ten_nguoi_choi}
ten_nguoi_choi_dict = {}       # {ten_nguoi_choi: client_socket}
loi_moi = {}                   # {ten_nguoi_choi: ten_nguoi_moi}
lua_chon = {}                  # {ten_nguoi_choi: lua_chon}

# ====== GỬI TIN NHẮN ======
def gui_tin_nhan(nguoi_nhan, tin_nhan):
    try:
        nguoi_nhan.send(tin_nhan.encode('utf-8'))
    except:
        nguoi_nhan.close()

def phat_broadcast(tin_nhan):
    for c in danh_sach_client:
        try:
            c.send(tin_nhan.encode('utf-8'))
        except:
            c.close()

# ====== XÁC ĐỊNH NGƯỜI THẮNG ======
def xac_dinh_thang(p1, p2):
    c1, c2 = lua_chon.get(p1), lua_chon.get(p2)
    if not c1 or not c2:
        return None

    if c1 == c2:
        return "Hòa!"
    elif (c1 == "búa" and c2 == "kéo") or \
         (c1 == "bao" and c2 == "búa") or \
         (c1 == "kéo" and c2 == "bao"):
        return f"{p1} thắng!"
    else:
        return f"{p2} thắng!"

# ====== XỬ LÝ YÊU CẦU NGƯỜI CHƠI ======
def xu_ly_client(client):
    try:
        ten = client.recv(1024).decode('utf-8')
        danh_sach_client[client] = ten
        ten_nguoi_choi_dict[ten] = client
        print(f"[+] {ten} đã kết nối")
        phat_broadcast(f"🔵 {ten} đã tham gia trò chơi.")

        while True:
            du_lieu = client.recv(1024).decode('utf-8')
            if not du_lieu:
                break

            # ----- Tin nhắn chat -----
            if du_lieu.startswith("Chat:"):
                tin_nhan = du_lieu[5:]
                phat_broadcast(f"[{ten}]: {tin_nhan}")

            # ----- Mời chơi -----
            elif du_lieu.startswith("Invite:"):
                doi_thu = du_lieu.split(":", 1)[1]
                if doi_thu in ten_nguoi_choi_dict:
                    loi_moi[doi_thu] = ten
                    gui_tin_nhan(ten_nguoi_choi_dict[doi_thu], f"📨 {ten} mời bạn chơi.")
                    gui_tin_nhan(client, f"✅ Đã gửi lời mời đến {doi_thu}.")
                else:
                    gui_tin_nhan(client, f"⚠️ Người chơi {doi_thu} không tồn tại hoặc chưa online.")

            # ----- Chấp nhận lời mời -----
            elif du_lieu == "Accept":
                if ten in loi_moi:
                    nguoi_moi = loi_moi[ten]
                    gui_tin_nhan(ten_nguoi_choi_dict[nguoi_moi], f"🎯 {ten} đã chấp nhận lời mời.")
                    gui_tin_nhan(client, f"🎮 Bắt đầu chơi với {nguoi_moi}!")
                    del loi_moi[ten]
                else:
                    gui_tin_nhan(client, "⚠️ Không có lời mời nào đang chờ.")

            # ----- Chọn nước đi -----
            elif du_lieu in ["búa", "bao", "kéo"]:
                lua_chon[ten] = du_lieu
                gui_tin_nhan(client, f"🕹 Bạn đã chọn: {du_lieu}")

                # Khi đủ 2 người đã chọn, tính kết quả
                if len(lua_chon) >= 2:
                    nguoi_choi = list(lua_chon.keys())
                    if len(nguoi_choi) >= 2:
                        p1, p2 = nguoi_choi[0], nguoi_choi[1]
                        ket_qua = xac_dinh_thang(p1, p2)
                        phat_broadcast(f"🪨 {p1}: {lua_chon[p1]} | ✂️ {p2}: {lua_chon[p2]} ➜ {ket_qua}")
                        lua_chon.clear()

    except Exception as e:
        print(f"Lỗi từ client {danh_sach_client.get(client, '?')}: {e}")

    finally:
        ten_roi = danh_sach_client.get(client, "Người chơi")
        print(f"[-] {ten_roi} đã ngắt kết nối.")
        phat_broadcast(f"🔴 {ten_roi} đã rời trò chơi.")
        if ten_roi in ten_nguoi_choi_dict:
            del ten_nguoi_choi_dict[ten_roi]
        if client in danh_sach_client:
            del danh_sach_client[client]
        client.close()

# ====== CHẠY SERVER ======
def bat_dau_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((DIA_CHI, CONG))
    server.listen()
    print(f"🚀 Server đang chạy tại {DIA_CHI}:{CONG}")

    while True:
        client, dia_chi = server.accept()
        client.send("Nhập tên của bạn:".encode('utf-8'))
        threading.Thread(target=xu_ly_client, args=(client,), daemon=True).start()

if __name__ == "__main__":
    bat_dau_server()
