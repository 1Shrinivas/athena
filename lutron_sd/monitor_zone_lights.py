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
    zone_id = "1035"   # Example dimmed zone (Dining Room b)
    level = 100      # Brightness level from 0 to 100

    create_request_dimmed_level(ssock, zone_id, level)

    ssock.close()

if __name__ == "__main__":
    main()


# For Calling an Area Scene 
# import os
# import socket
# import ssl
# import json

# from definitions import *  # Certs and processor connection details

# def _send_json(sock, json_msg):
#     message = (json.dumps(json_msg) + "\r\n").encode("ASCII")
#     sock.sendall(message)

# def _recv_json(sock):
#     response = sock.recv(5000)
#     if not response:
#         return None
#     return json.loads(response.decode("ASCII"))

# def create_request_goto_scene(sock, area_id, scene_id):
#     request = {
#         "CommuniqueType": "CreateRequest",
#         "Header": {
#             "URL": f"/area/983/commandprocessor"
#         },
#         "Body": {
#             "Command": {
#                 "CommandType": "GoToScene",
#                 "GoToSceneParameters": {
#                     "CurrentScene": {
#                         "href": f"/areascene/983"
#                     }
#                 }
#             }
#         }
#     }
#     print(f"Sending CreateRequest to trigger scene {scene_id} in area {area_id}")
#     _send_json(sock, request)
#     response = _recv_json(sock)
#     print("Response:", response)

# def main():
#     print("Checking certificates...")
#     if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
#         print("Certificates not found. Run provisioning first.")
#         return

#     print("Establishing TLS connection to processor...")
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
#         print("Connection error:", e)
#         return

#     # === Replace with actual area ID and scene ID ===
#     area_id = "983"
#     scene_id = "987"

#     create_request_goto_scene(ssock, area_id, scene_id)

#     ssock.close()

# if __name__ == "__main__":
#     main()

# 983 -> ON
# import os
# import socket
# import ssl
# import json
# from fastapi import FastAPI

# from definitions import *  # Certs and processor connection details


# # api = FastAPI()

# def _send_json(sock, json_msg):
#     message = (json.dumps(json_msg) + "\r\n").encode("ASCII")
#     sock.sendall(message)

# def _recv_json(sock):
#     response = sock.recv(5000)
#     if not response:
#         return None
#     return json.loads(response.decode("ASCII"))


# # @api.get('/test')
# # def check():
# #     return 'all good'


# # @api.get('/trigger_scene')
# def trigger_scene(sock, area_id, scene_id):
#     request = {
#         "CommuniqueType": "CreateRequest",
#         "Header": {
#             "URL": f"/area/{area_id}/commandprocessor"
#         },
#         "Body": {
#             "Command": {
#                 "CommandType": "GoToScene",
#                 "GoToSceneParameters": {
#                     "CurrentScene": {
#                         "href": f"/areascene/{scene_id}"
#                     }
#                 }
#             }
#         }
#     }
#     print(f"Triggering scene {scene_id} in area {area_id}...")
#     _send_json(sock, request)
#     response = _recv_json(sock)
#     print("Response:", response)



# def main():
#     print("Checking certificates...")
#     if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
#         print("Certificates not found.")
#         return

#     print("Connecting to Lutron processor...")
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
#         print("Connection error:", e)
#         return

#     # === Living Room = /area/983
#     # === "Full ON" Scene = /areascene/988
#     area_id = "983"
#     scene_id = "988"

#     trigger_scene(ssock, area_id, scene_id)

#     ssock.close()

# if __name__ == "__main__":
#     main()



