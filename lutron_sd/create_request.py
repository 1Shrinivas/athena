# for Dimmed Lighting

import os
import socket
import ssl
import json

from definitions import *  # Paths to certs and processor info

def _send_json(sock, json_msg):
    message = (json.dumps(json_msg) + "\r\n").encode("ASCII")
    sock.sendall(message)

def _recv_json(sock):
    response = sock.recv(5000)
    if not response:
        return None
    return json.loads(response.decode("ASCII"))

def create_request_dimmed_level(sock, zone_id, level):
    request = {
        "CommuniqueType": "CreateRequest",
        "Header": {
            "Url": f"/zone/{zone_id}/commandprocessor"
        },
        "Body": {
            "Command": {
                "CommandType": "GoToDimmedLevel",
                "DimmedLevelParameters": {
                    "Level": level
                }
            }
        }
    }
    print(f"Sending CreateRequest to set dimmed level of zone {zone_id} to {level}")
    _send_json(sock, request)
    response = _recv_json(sock)
    print("Response:", response)

def main():
    print("Checking certificates...")
    if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
        print("Certificates not found. Run provisioning first.")
        return

    print("Establishing TLS connection to processor...")
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
        context.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
        context.check_hostname = False

        sock = socket.create_connection((LUTRON_PROC_ADDRESS, 8081))
        ssock = context.wrap_socket(sock, server_hostname=LUTRON_PROC_HOSTNAME)
        sock.close()
    except Exception as e:
        print("Connection error:", e)
        return

    # === Replace with actual zone ID and desired level ===
    zone_id =  "1035"   # Example dimmed zone (Dining Room b)
    level = 100 # Brightness level from 0 to 100

    create_request_dimmed_level(ssock, zone_id, level)

    ssock.close()

if __name__ == "__main__":
    main()

