import os
import socket
import ssl
import json
import schedule
import time
from datetime import datetime

from definitions import *  # cert paths and processor info

def _send_json(sock, json_msg):
    message = (json.dumps(json_msg) + "\r\n").encode("ASCII")
    sock.sendall(message)

def _recv_json(sock):
    response = sock.recv(5000)
    if not response:
        return None
    return json.loads(response.decode("ASCII"))

def create_request_zone_level(zone_id, level, control_type="Dimmed"):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Connecting to processor to set Zone {zone_id} to {level} ({control_type})")

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

    # Correct command per type
    if control_type == "Switched":
        command = {
            "CommandType": "GoToSwitchedLevel",
            "SwitchedLevelParameters": {
                "SwitchedLevel": "On" if level > 0 else "Off"
            }
        }
    else:  # Dimmed
        command = {
            "CommandType": "GoToDimmedLevel",
            "DimmedLevelParameters": {
                "Level": level
            }
        }

    request = {
        "CommuniqueType": "CreateRequest",
        "Header": {
            "Url": f"/zone/{zone_id}/commandprocessor"
        },
        "Body": {
            "Command": command
        }
    }

    _send_json(ssock, request)
    response = _recv_json(ssock)
    print("Response:", json.dumps(response, indent=4))
    ssock.close()

# Schedule Setup

def schedule_tasks():
    # Living Room Light A & B (Switched)
    schedule.every().day.at("06:01").do(create_request_zone_level, zone_id="1035", level=0, control_type="Switched")
    schedule.every().day.at("06:01").do(create_request_zone_level, zone_id="1107", level=100, control_type="Switched")
    
    # Dining Room b (Dimmed)
    # schedule.every().day.at("05:55").do(create_request_zone_level, zone_id="1719", level=100, control_type="Dimmed")

def main():
    print("🔄 Scheduler started...")
    schedule_tasks()
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
