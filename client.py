import socket

def discover_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(("", 5002))
        print("Searching for file server...")
        while True:
            data, addr = s.recvfrom(1024)
            if data == b"FILE_SERVER":
                print(f"Server found at: {addr[0]}")
                return addr[0]

if __name__ == "__main__":
    server_ip = discover_server()
    print(f"Access the server at: http://{server_ip}:5001")
