#!/usr/bin/env python3
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, socket
from threading import Thread, Lock
import uuid

HOST = "127.0.0.1"
PORT = 33000
BUFSIZ = 2048
ADDR = (HOST, PORT)

clients = {}        # socket -> name
names_to_sock = {}  # name -> socket
addresses = {}

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
SERVER.bind(ADDR)

# ======= HÀM GỬI =======
def send_to(target, text: str):
    try:
        sock = names_to_sock.get(target) if isinstance(target, str) else target
        if sock:
            sock.send((text + "\n").encode("utf8"))
    except Exception:
        pass

def broadcast(data: bytes, prefix: str = ""):
    dead = []
    for sock in list(clients.keys()):
        try:
            sock.send(prefix.encode("utf8") + data)
        except Exception:
            dead.append(sock)
    for d in dead:
        name = clients.pop(d, None)
        if name:
            names_to_sock.pop(name, None)

# ======= LOGIC GAME =======
rps_lock = Lock()
rooms = {}          # room_id -> dict
game_of = {}        # name -> room_id
pending_invite = {} # target_name -> inviter_name

def judge(a, b):
    if a == b:
        return "draw"
    wins = {("rock", "scissors"), ("scissors", "paper"), ("paper", "rock")}
    return "a" if (a, b) in wins else "b"

def can_play(name):
    with rps_lock:
        return name not in game_of

def create_room(p1, p2, best_of=3):
    with rps_lock:
        if p1 in game_of or p2 in game_of:
            return None
        room_id = str(uuid.uuid4())[:8]
        rooms[room_id] = {
            "players": [p1, p2],
            "scores": {p1: 0, p2: 0},
            "moves": {},
            "best_of": best_of,
            "round": 1,
            "active": True
        }
        game_of[p1] = room_id
        game_of[p2] = room_id
        return room_id

def end_room(room_id):
    with rps_lock:
        room = rooms.get(room_id)
        if not room:
            return
        for p in room["players"]:
            game_of.pop(p, None)
        room["active"] = False

def handle_move(name, move):
    room_id = game_of.get(name)
    if not room_id:
        send_to(name, "[[INFO]] Bạn chưa ở trong ván nào.")
        return
    with rps_lock:
        room = rooms.get(room_id)
        if not room or not room["active"]:
            return
        if move not in ("rock", "paper", "scissors"):
            send_to(name, "[[INFO]] Nước đi không hợp lệ.")
            return
        room["moves"][name] = move
        p1, p2 = room["players"]

    send_to(name, f"[[YOU_MOVED]] {move}")

    # nếu cả hai đã ra tay
    with rps_lock:
        room = rooms.get(room_id)
        if not room or not room["active"]:
            return
        p1, p2 = room["players"]
        if p1 in room["moves"] and p2 in room["moves"]:
            a, b = room["moves"][p1], room["moves"][p2]
            res = judge(a, b)
            winner = None
            if res == "a":
                room["scores"][p1] += 1
                winner = p1
            elif res == "b":
                room["scores"][p2] += 1
                winner = p2
            for pl in (p1, p2):
                send_to(pl, f"[[ROUND]] {room['round']} {p1}:{a} {p2}:{b} "
                             f"{'DRAW' if not winner else 'WIN:'+winner} {room['scores']}")
            room["moves"].clear()
            room["round"] += 1
            need = (room["best_of"] // 2) + 1
            if room["scores"][p1] >= need or room["scores"][p2] >= need:
                final = p1 if room["scores"][p1] > room["scores"][p2] else p2
                for pl in (p1, p2):
                    send_to(pl, f"[[GAME_END]] {final} {room['scores']}")
                end_room(room_id)

def handle_command(name, text):
    if text.startswith("/invite "):
        target = text.split()[1][1:]
        if target == name:
            send_to(name, "[[INFO]] Không thể mời chính bạn.")
            return
        if target not in names_to_sock:
            send_to(name, "[[INFO]] Không tìm thấy người.")
            return
        if not can_play(name) or not can_play(target):
            send_to(name, "[[INFO]] Một trong hai đang bận.")
            return
        pending_invite[target] = name
        send_to(name, f"[[INFO]] Đã gửi lời mời tới {target}.")
        send_to(target, f"[[INVITE]] {name}")
        return

    if text.startswith("/accept "):
        inviter = text.split()[1]
        if pending_invite.get(name) != inviter:
            send_to(name, "[[INFO]] Không có lời mời hợp lệ.")
            return
        pending_invite.pop(name, None)
        if not can_play(name) or not can_play(inviter):
            send_to(name, "[[INFO]] Một trong hai đang bận.")
            return
        create_room(inviter, name)
        send_to(inviter, f"[[GAME_START]] {inviter},{name}")
        send_to(name, f"[[GAME_START]] {inviter},{name}")
        return

    if text.startswith("/decline "):
        inviter = text.split()[1]
        pending_invite.pop(name, None)
        send_to(inviter, f"[[INFO]] {name} từ chối lời mời.")
        return

    if text.startswith("/move "):
        mv = text.split()[1]
        handle_move(name, mv)
        return

    if text.startswith("/quitgame"):
        rid = game_of.get(name)
        if rid:
            end_room(rid)
        send_to(name, "[[INFO]] Đã thoát ván.")
        return

# ======= CORE SERVER =======
def accept_incoming():
    while True:
        client, addr = SERVER.accept()
        print(f"[NEW CONNECTION] {addr}")
        client.send("Nhập tên:".encode("utf8"))
        Thread(target=handle_client, args=(client,), daemon=True).start()

def handle_client(client):
    name = client.recv(BUFSIZ).decode("utf8").strip()
    if not name:
        name = f"user_{addresses.get(client, ('?', 0))[1]}"
    clients[client] = name
    names_to_sock[name] = client
    broadcast(f"{name} đã tham gia!".encode("utf8"))
    while True:
        try:
            data = client.recv(BUFSIZ)
        except:
            break
        if not data:
            break
        text = data.decode("utf8").strip()
        if text == "{quit}":
            break
        if text.startswith("/"):
            handle_command(name, text)
        else:
            broadcast(data, prefix=name + ": ")
    print(f"[DISCONNECT] {name}")
    clients.pop(client, None)
    names_to_sock.pop(name, None)
    client.close()
    broadcast(f"{name} đã thoát.".encode("utf8"))

if __name__ == "__main__":
    print("[STARTING] Server đang khởi động...")
    SERVER.listen(5)
    print(f"[LISTENING] Server đang chạy tại {HOST}:{PORT}")
    accept_incoming()
