import ssl, socket, json

LUTRON_IP = "athena-98:03:8a:31:0d:e2-server"  #processor IP
PORT = 8081

CERT_PATH = "./cert"
CERT_FILE = f"{CERT_PATH}/leap_signed_csr.pem"
KEY_FILE = f"{CERT_PATH}/leap_private_key.pem"
CA_FILE = f"{CERT_PATH}/lap_lutron_root.crt"

def connect_to_leap():
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    context.load_verify_locations(CA_FILE)

    sock = socket.create_connection((LUTRON_IP, PORT))
    return context.wrap_socket(sock, server_hostname=LUTRON_IP)

def send_leap_command(command: dict):
    conn = connect_to_leap()
    try:
        conn.sendall((json.dumps(command) + "\r\n").encode())
        data = conn.recv(65536)
        return json.loads(data.decode())
    finally:
        conn.close()
