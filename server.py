# server.py
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
diem_so = {}
van_hien_tai = {}
trang_thai_tran = {}
choi_lai = {}  # MỚI: Lưu trạng thái chơi lại

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

def bat_dau_tran(p1, p2):
    diem_so[p1] = 0
    diem_so[p2] = 0
    van_hien_tai[p1] = 1
    van_hien_tai[p2] = 1
    trang_thai_tran[p1] = "choi"
    trang_thai_tran[p2] = "choi"
    choi_lai.pop(p1, None)
    choi_lai.pop(p2, None)

    c1 = ten_nguoi_choi_dict[p1]
    c2 = ten_nguoi_choi_dict[p2]

    gui(c1, f"Đối thủ: {p2}")
    gui(c2, f"Đối thủ: {p1}")
    time.sleep(0.1)
    gui(c1, "Trận đấu bắt đầu! BO3.")
    gui(c2, "Trận đấu bắt đầu! BO3.")
    gui(c1, "Ván 1/3\n")
    gui(c2, "Ván 1/3\n")
    gui(c1, f"TỈ SỐ {p1} : {diem_so[p1]} - {diem_so[p2]} : {p2}")
    gui(c2, f"TỈ SỐ {p1} : {diem_so[p1]} - {diem_so[p2]} : {p2}")

def cap_nhat_diem(p1, p2, kq):
    if "thắng!" in kq:
        winner = p1 if p1 in kq else p2
        diem_so[winner] += 1
    
    c1 = ten_nguoi_choi_dict[p1]
    c2 = ten_nguoi_choi_dict[p2]
    
    gui(c1, f"Ván {van_hien_tai[p1] + 1}/3\n")
    gui(c2, f"Ván {van_hien_tai[p2] + 1}/3\n")
    gui(c1, f"TỈ SỐ {p1} : {diem_so[p1]} - {diem_so[p2]} : {p2}")
    gui(c2, f"TỈ SỐ {p1} : {diem_so[p1]} - {diem_so[p2]} : {p2}")

def kiem_tra_ket_thuc(p1, p2):
    if diem_so[p1] >= 2 or diem_so[p2] >= 2:
        winner = p1 if diem_so[p1] >= 2 else p2
        c1 = ten_nguoi_choi_dict[p1]
        c2 = ten_nguoi_choi_dict[p2]
        gui(c1, f"\n*** {winner} THẮNG TRẬN! ***\n")
        gui(c2, f"\n*** {winner} THẮNG TRẬN! ***\n")
        luu_lich_su(f"{p1} vs {p2}: {winner} thắng trận (BO3)")
        trang_thai_tran[p1] = "ket_thuc"
        trang_thai_tran[p2] = "ket_thuc"
        return True
    return False

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
                    bat_dau_tran(p1, p2)
                    del loi_moi[ten]

            elif du_lieu == "Reject":
                if ten in loi_moi:
                    nguoi_moi = loi_moi[ten]
                    gui(ten_nguoi_choi_dict[nguoi_moi], f"{ten} đã từ chối lời mời.")
                    del loi_moi[ten]

            elif du_lieu in ["búa", "bao", "kéo"]:
                if ten not in dang_choi or trang_thai_tran.get(ten) != "choi": 
                    continue
                doi = dang_choi[ten]
                lua_chon[ten] = du_lieu

                if ten in lua_chon and doi in lua_chon:
                    kq = xac_dinh_thang(ten, doi)
                    c1 = ten_nguoi_choi_dict[ten]
                    c2 = ten_nguoi_choi_dict[doi]
                    gui(c1, f"{ten}: {lua_chon[ten]} | {doi}: {lua_chon[doi]} -> {kq}")
                    gui(c2, f"{ten}: {lua_chon[ten]} | {doi}: {lua_chon[doi]} -> {kq}")
                    luu_lich_su(f"{ten} vs {doi}: {kq}")
                    cap_nhat_diem(ten, doi, kq)

                    if not kiem_tra_ket_thuc(ten, doi):
                        van_hien_tai[ten] += 1
                        van_hien_tai[doi] += 1
                    else:
                        gui(c1, "Kết thúc! Chờ chơi lại...")
                        gui(c2, "Kết thúc! Chờ chơi lại...")
                    lua_chon.clear()

            elif du_lieu == "Chơi lại":
                if ten not in dang_choi or trang_thai_tran.get(ten) != "ket_thuc":
                    continue
                doi = dang_choi[ten]
                choi_lai[ten] = True
                gui(client, "Bạn đã chọn chơi lại. Đang chờ đối thủ...")

                if choi_lai.get(doi, False):
                    choi_lai.pop(ten, None)
                    choi_lai.pop(doi, None)
                    bat_dau_tran(ten, doi)
                    gui(ten_nguoi_choi_dict[ten], "Cả hai đã đồng ý! Bắt đầu lại...")
                    gui(ten_nguoi_choi_dict[doi], "Cả hai đã đồng ý! Bắt đầu lại...")
                else:
                    gui(ten_nguoi_choi_dict[doi], f"{ten} muốn chơi lại!")

    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        if client in danh_sach_client:
            ten_roi = danh_sach_client[client]
            print(f"[-] {ten_roi} rời.")
            phat(f"{ten_roi} đã rời.")
            # Thông báo đối thủ nếu đang chơi
            if ten_roi in dang_choi:
                doi = dang_choi[ten_roi]
                if doi in ten_nguoi_choi_dict:
                    gui(ten_nguoi_choi_dict[doi], f"{ten_roi} đã rời trận đấu.")
                dang_choi.pop(ten_roi, None)
                dang_choi.pop(doi, None)
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