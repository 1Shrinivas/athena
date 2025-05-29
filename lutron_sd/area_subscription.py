import os
import sys
import json
import socket
import ssl
from definitions import *  # Your certificate and connection settings

def _send_json(sock, json_msg):
    send_msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
    sock.sendall(send_msg)

def _recv_json(sock):
    buffer = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buffer += chunk
        if b"\r\n" in buffer:
            break
    try:
        return json.loads(buffer.decode("ASCII").strip())
    except json.JSONDecodeError as e:
        print("❌ JSON Decode Error:", e)
        print("🔹 Raw buffer:", buffer.decode("ASCII", errors="ignore"))
        return None

def main():
    print("🔐 Checking for required certificates...")
    if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
        print("❌ Missing certificates. Run lap_sample.py first.")
        sys.exit()

    print("✅ Certificates found. Connecting to processor...")
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
        print(f"❌ Connection error: {e}")
        sys.exit()

    print("✅ Connected to Lutron processor.\n")

    # Subscribe to all area status changes
    subscribe_msg = {
        "CommuniqueType": "SubscribeRequest",
        "Header": {
            "Url": "/area/983/status"
        }
    }

    print("📡 Subscribing to /area/status...\n")
    _send_json(ssock, subscribe_msg)

    response = _recv_json(ssock)
    if response:
        print("✅ Subscription confirmed:")
        print(json.dumps(response, indent=4))

    print("\n👂 Listening for area occupancy changes...\n")

    last_occupancy = {}

    try:
        while True:
            update = _recv_json(ssock)
            if not update:
                continue

            area_status = update.get("Body", {}).get("AreaStatus")
            if not area_status:
                continue

            # If single object
            if isinstance(area_status, dict):
                area_status = [area_status]

            for area in area_status:
                href = area.get("href", "")
                area_id = href.split("/")[-2] if "/area/" in href else "unknown"
                occupancy = area.get("OccupancyStatus", "Unknown")
                level = area.get("Level", "N/A")
                scene = area.get("CurrentScene", {}).get("href", "None")

                if last_occupancy.get(area_id) != occupancy:
                    print(f"🚨 Area {area_id} occupancy changed: {occupancy}")
                    print(f"   🔆 Level: {level}")
                    print(f"   🎭 Scene: {scene}")
                    print("-" * 60)
                    last_occupancy[area_id] = occupancy

    except KeyboardInterrupt:
        print("🛑 Interrupted by user.")
        ssock.close()

if __name__ == "__main__":
    main()



# import os
# import sys
# import json
# import socket
# import ssl
# from definitions import *

# def _send_json(sock, json_msg):
#     send_msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
#     sock.sendall(send_msg)

# def _recv_json(sock):
#     buffer = b""
#     while True:
#         chunk = sock.recv(4096)
#         if not chunk:
#             break
#         buffer += chunk
#         if b"\r\n" in buffer:
#             break
#     try:
#         return json.loads(buffer.decode("ASCII").strip())
#     except json.JSONDecodeError as e:
#         print(" JSON Decode Error:", e)
#         print("Raw buffer:", buffer.decode("ASCII", errors="ignore"))
#         return None

# def main():
#     print(" Checking for required certificates...")
#     if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
#         print(" Missing certificates. Run lap_sample.py first.")
#         sys.exit()
#     print(" Certs found. Connecting to processor...")

#     try:
#         context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
#         context.verify_mode = ssl.CERT_REQUIRED
#         context.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
#         context.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
#         context.check_hostname = False
#         sock = socket.create_connection((LUTRON_PROC_ADDRESS, 8081))
#         ssock = context.wrap_socket(sock, server_hostname=LUTRON_PROC_HOSTNAME)
#         sock.close()
#     except Exception as e:
#         print(f" Connection error: {e}")
#         sys.exit()

#     print(" Connected to Lutron processor.\n")

#     # Send subscription request to /area/status
#     subscribe_msg = {
#         "CommuniqueType": "SubscribeRequest",
#         "Header": {
#             "Url": "/area/status"
#         }
#     }

#     print(" Sending SubscribeRequest to /area/status...\n")
#     _send_json(ssock, subscribe_msg)

#     # Read initial SubscribeResponse
#     response = _recv_json(ssock)
#     if response:
#         print("SubscribeResponse:")
#         print(json.dumps(response, indent=4))

#     print("\n Listening for area status changes (Ctrl+C to stop)...\n")

#     last_status = {}

#     try:
#         while True:
#             update = _recv_json(ssock)
#             if update:
#                 area_status = update.get("Body", {}).get("AreaStatus")
#                 if not area_status:
#                     continue

#                 # Normalize single or multiple area entries
#                 if isinstance(area_status, dict):
#                     area_status = [area_status]

#                 for area in area_status:
#                     href = area.get("href", "")
#                     area_id = href.split("/")[-2] if "/area/" in href else "unknown"
#                     occupancy = area.get("OccupancyStatus", "Unknown")
#                     level = area.get("Level", "N/A")
#                     scene = area.get("CurrentScene", {}).get("href", "None")

#                     # Only show update if occupancy changed
#                     if last_status.get(area_id) != occupancy:
#                         print(f" Area {area_id} Status Update:")
#                         print(f"  ↳ Occupancy: {occupancy}")
#                         print(f"  ↳ Level: {level}")
#                         print(f"  ↳ CurrentScene: {scene}")
#                         print("-" * 80)
#                         last_status[area_id] = occupancy

#     except KeyboardInterrupt:
#         print(" Stopped by user.")
#         ssock.close()

# if __name__ == "__main__":
#     main()
