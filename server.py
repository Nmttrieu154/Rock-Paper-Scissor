import socket
import threading
import time

DIA_CHI = "0.0.0.0"
CONG = 5555

danh_sach_client = {}
ten_nguoi_choi_dict = {}
loi_moi = {}
lua_chon = {}
dang_choi = {}

def gui(nguoi_nhan, tin):
    try: nguoi_nhan.send(tin.encode('utf-8'))
    except: pass

def phat(tin):
    for c in list(danh_sach_client):
        try: c.send(tin.encode('utf-8'))
        except: c.close()

def xac_dinh_thang(p1, p2):
    c1, c2 = lua_chon.get(p1), lua_chon.get(p2)
    if not c1 or not c2: return None
    if c1 == c2: return "Hòa!"
    elif (c1 == "búa" and c2 == "kéo") or (c1 == "bao" and c2 == "búa") or (c1 == "kéo" and c2 == "bao"):
        return f"{p1} thắng!"
    else:
        return f"{p2} thắng!"

def luu_lich_su(kq):
    with open("history.txt", "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M %d/%m')}] {kq}\n")

def xu_ly(client):
    try:
        ten = client.recv(1024).decode('utf-8').strip()
        if not ten or ten in ten_nguoi_choi_dict:
            client.close()
            return
        danh_sach_client[client] = ten
        ten_nguoi_choi_dict[ten] = client
        print(f"[+] {ten} đã kết nối")
        phat(f"{ten} đã tham gia.")

        while True:
            du_lieu = client.recv(1024).decode('utf-8')
            if not du_lieu: break

            if du_lieu.startswith("Chat:"):
                phat(f"[{ten}]: {du_lieu[5:]}")

            elif du_lieu.startswith("Invite:"):
                doi_thu = du_lieu.split(":", 1)[1]
                if doi_thu in ten_nguoi_choi_dict and doi_thu != ten:
                    loi_moi[doi_thu] = ten
                    gui(ten_nguoi_choi_dict[doi_thu], f"{ten} mời bạn chơi.")
                    gui(client, f"Đã gửi lời mời đến {doi_thu}.")
                else:
                    gui(client, f"Người chơi {doi_thu} không tồn tại hoặc chưa online.")

            elif du_lieu == "Accept":
                if ten in loi_moi:
                    p1 = loi_moi[ten]
                    p2 = ten
                    dang_choi[p1] = p2
                    dang_choi[p2] = p1
                    gui(ten_nguoi_choi_dict[p1], f"{p2} đã chấp nhận. Bắt đầu!")
                    gui(client, f"Bắt đầu chơi với {p1}!")
                    del loi_moi[ten]

            elif du_lieu == "Reject":
                if ten in loi_moi:
                    nguoi_moi = loi_moi[ten]
                    gui(ten_nguoi_choi_dict[nguoi_moi], f"{ten} đã từ chối lời mời.")
                    del loi_moi[ten]

            elif du_lieu in ["búa", "bao", "kéo"]:
                if ten not in dang_choi: continue
                doi = dang_choi[ten]
                lua_chon[ten] = du_lieu
                gui(client, f"Bạn chọn: {du_lieu}")
                if ten in lua_chon and doi in lua_chon:
                    kq = xac_dinh_thang(ten, doi)
                    phat(f"{ten}: {lua_chon[ten]} | {doi}: {lua_chon[doi]} -> {kq}")
                    luu_lich_su(f"{ten} vs {doi}: {kq}")
                    lua_chon.clear()
                    del dang_choi[ten]
                    del dang_choi[doi]

    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        if client in danh_sach_client:
            ten_roi = danh_sach_client[client]
            print(f"[-] {ten_roi} rời.")
            phat(f"{ten_roi} đã rời.")
            ten_nguoi_choi_dict.pop(ten_roi, None)
            danh_sach_client.pop(client, None)
        client.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((DIA_CHI, CONG))
    s.listen()
    print(f"Server chạy tại {DIA_CHI}:{CONG}")
    while True:
        client, _ = s.accept()
        threading.Thread(target=xu_ly, args=(client,), daemon=True).start()

if __name__ == "__main__":
    main()