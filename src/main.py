import os
import re
import socket
import threading
import configparser
import time
from datetime import datetime, timedelta, timezone

cwd = os.getcwd()

entries_protocol = []
entries_destip = []
entries_destport = []
entries_relayport = []
entries_name = []

blocked_ips = []

version = "v0.1"

art = """
███████ ██       ██████  ██     ██     ██████   █████  ███████ ███████  █████   ██████  ███████ 
██      ██      ██    ██ ██     ██     ██   ██ ██   ██ ██      ██      ██   ██ ██       ██      
█████   ██      ██    ██ ██  █  ██     ██████  ███████ ███████ ███████ ███████ ██   ███ █████   
██      ██      ██    ██ ██ ███ ██     ██      ██   ██      ██      ██ ██   ██ ██    ██ ██      
██      ███████  ██████   ███ ███      ██      ██   ██ ███████ ███████ ██   ██  ██████  ███████ 
                                                                                                                                                                                             
"""

config = configparser.ConfigParser()
config.read(os.path.join(cwd, "server.conf"))

def bool_from_config(value): return str(value).strip() == "1"

status_ip_blocking = bool_from_config(config.get("blocking", "ip_blocking"))
status_logging = bool_from_config(config.get("logging", "logging"))

def lprint(type, message):
    struct = f"[{type}] [{datetime.now().strftime('%D - %H:%M:%S')}] -- {message}"
    print(struct)

    if status_logging:
        with open(os.path.join(cwd, "logs.txt"), "a") as logs:
            logs.write(struct + "\n")

print(art)
print(f"Version: {version}")
print("Made by github.com/ptc0\n")

if not os.path.exists(os.path.join(cwd, "logs.txt")): open(os.path.join(cwd, "logs.txt"), 'w')
if not os.path.exists(os.path.join(cwd, "fp-config")): 
    with open(os.path.join(cwd, "fp-config"), 'a') as f:
        lines = [
            "/ Flow Passage",
            "/ Config File",
            "/",
            "/ Structure:",
            "/ [protocol][dest-ip][dest-port][relay-port][name]",
            "/",
            "/ Usage Example:",
            "/ [TCP][123.456.789.10][8080][5000][Web Server]",
            ""
        ]

        for line in lines:
            f.write(line + "\n")

    lprint("INFO", "fp-config created")

if not os.path.exists(os.path.join(cwd, "server.conf")): 
    with open(os.path.join(cwd, "server.conf"), 'a') as f:
        lines = [
            "[blocking]",
            "ip_blocking = 1",
            "",
            "[logging]",
            "logging = 1"
        ]

        for line in lines:
            f.write(line + "\n")

    lprint("INFO", "server.conf created")

def load_entries():
    try:
        global entries_protocol
        global entries_destip
        global entries_destport
        global entries_relayport
        global entries_name

        tmp_c_file_lines = []
        config_test_pattern = re.compile(
            r'^\[([A-Za-z0-9_]+)\]\[(\d{1,3}(?:\.\d{1,3}){3})\]\[(\d{1,5})\]\[(\d{1,5})\]\[([^\]]+)\]$'
        )

        with open(os.path.join(cwd, "fp-config"), 'r') as c_file:
            for line in c_file:
                tmp_c_file_lines.append(line.strip())

        for line in tmp_c_file_lines:
            if not line.startswith("/"):
                if len(line) > 0:
                    if config_test_pattern.match(line):
                        entries_protocol.append(config_test_pattern.match(line).group(1))
                        entries_destip.append(config_test_pattern.match(line).group(2))
                        entries_destport.append(config_test_pattern.match(line).group(3))
                        entries_relayport.append(config_test_pattern.match(line).group(4))
                        entries_name.append(config_test_pattern.match(line).group(5))

                    else:
                        raise Exception("fp-config entries do not match expected structure!")

        lprint("INFO", f"Entries initialization completed at: {datetime.now()}")

    except Exception as e:
        lprint("ERROR", f"Error during initialization of entries: {e}")
        exit()

def load_ip():
    global blocked_ips

    tmp_ip_file_lines = []
    ip_testing_pattern = re.compile(
        r'^((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$'
    )
    with open(os.path.join(cwd, "client_blocks", "ip"), 'r') as ip_file:
        for line in ip_file:
            tmp_ip_file_lines.append(line.strip())

    for line in tmp_ip_file_lines:
        if not line.startswith("/"):
            if len(line) > 0:
                if ip_testing_pattern.match(line):
                    blocked_ips.append(line)
                else:
                    lprint("WARN", f"The IP: {line} is invalid. To get rid of this message, remove this ip from client blocks.")

if not len(entries_destip) > 0:
    lprint("WARN", "No entries loaded! Configure them at 'fp-config'.")
    lprint("WARN", "Server will not receive connections until any entry is added.")

# Handling TCP Connections

def tcp_handler(conn, addr, target_ip=None, target_port=None):
    if addr in blocked_ips and status_ip_blocking:
        lprint("TCP", f"{addr} was blocked from accessing {target_ip} due to it being in the client blocks.")
        conn.close()
        lprint("TCP", f"Connection closed: {addr}")
    else :
        lprint("TCP", f"Connection established from {addr}")

    try:
        if target_ip and target_port:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as target_sock:
                target_sock.connect((target_ip, int(target_port)))

                def forward(src, dst):
                    while True:
                        data = src.recv(4096)
                        if not data:
                            break
                        dst.sendall(data)

                t1 = threading.Thread(target=forward, args=(conn, target_sock))
                t2 = threading.Thread(target=forward, args=(target_sock, conn))
                t1.start()
                t2.start()
                t1.join()
                t2.join()
        else:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                lprint("TCP", f"Received from {addr}: {data.decode(errors='ignore')}")
                conn.sendall(data)

    except Exception as e:
        lprint("ERROR", f"TCP connection error with {addr}: {e}")
    finally:
        conn.close()
        lprint("TCP", f"Connection closed: {addr}")

def tcp_listener(dest_ip, dest_port, relay_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', int(relay_port)))
        s.listen()
        lprint("TCP", f"Listening on port {relay_port}, forwarding to {dest_ip}:{dest_port}")
        while True:
            conn, addr = s.accept()
            threading.Thread(
                target=tcp_handler, 
                args=(conn, addr, dest_ip, dest_port),
                daemon=True
            ).start()


# Handling UDP Connections

def udp_handler(sock, addr, target_ip=None, target_port=None, data=None):
    if addr[0] in blocked_ips and status_ip_blocking:
        lprint("UDP", f"{addr[0]} was blocked from accessing {target_ip} due to it being in the client blocks.")
        return

    try:
        if target_ip and target_port and data:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as target_sock:
                target_sock.sendto(data, (target_ip, int(target_port)))
                response, _ = target_sock.recvfrom(4096)
                sock.sendto(response, addr)
        else:
            if data:
                lprint("UDP", f"Received from {addr}: {data.decode(errors='ignore')}")
                sock.sendto(data, addr)
    except Exception as e:
        lprint("ERROR", f"UDP handling error for {addr}: {e}")

def udp_listener(dest_ip, dest_port, relay_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('0.0.0.0', int(relay_port)))
        lprint("UDP", f"Listening on port {relay_port}, forwarding to {dest_ip}:{dest_port}")
        while True:
            data, addr = s.recvfrom(4096)
            threading.Thread(
                target=udp_handler,
                args=(s, addr, dest_ip, dest_port, data),
                daemon=True
            ).start()

for i in range(len(entries_destip)):
    proto = entries_protocol[i].upper()
    dest_ip = entries_destip[i]
    dest_port = entries_destport[i]
    relay_port = entries_relayport[i]

    if proto == "TCP":
        threading.Thread(
            target=tcp_listener,
            args=(dest_ip, dest_port, relay_port),
            daemon=True
        ).start()

    elif proto == "UDP":
        threading.Thread(
            target=udp_listener,
            args=(dest_ip, dest_port, relay_port),
            daemon=True
        ).start()

    lprint("INFO", f"New {proto} endpoint created: {dest_ip}:{dest_port}")

while True:
    lprint("INFO", "Blocked IP Lists and Entries Lists are being reloaded in case of changes...")
    load_entries()
    load_ip()
    lprint("INFO", f"Blocked IP Lists and Entries Lists has been reloaded! Next reload in: {datetime.now(timezone.utc) + timedelta(hours=1)} (UTC Time)")
    time.sleep(3600)