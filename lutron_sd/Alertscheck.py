import os
import sys
import json
import socket
import ssl

from definitions import *  # Make sure this file defines cert paths and constants

def _send_json(sock, json_msg):
    send_msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
    sock.sendall(send_msg)

def _recv_json(sock):
    recv_msg = sock.recv(5000)
    if len(recv_msg) == 0:
        return None
    return json.loads(recv_msg.decode("ASCII"))

def send_client_setting_update(sock, version=3):
    request =   {
"CommuniqueType":"CreateRequest",
"Header":{
"Url":"/reportgenerator"
},
"Body":{
"LinkHealthReportParameters":{
"ReportType":"LinkHealthReport",
"Links":[
    {
        # 1305
"href":"/link/1310"
}
    ]
}
}
} 
#     {
# "CommuniqueType":"CreateRequest",
# "Header":{
# "Url":"/timeclockevent/1859/commandprocessor"
# },
# "Body":{
# "Command":{
# "CommandType":"TestThisTimeclockEvent"
# }
# }
# }
#     {
#     "CommuniqueType": "UpdateRequest",
#     "Header": {
#         "Url": "/timeclockevent/1842/status"
#     },
#     "Body": {
#         "TimeclockEventStatus": {
#             "State": "Disabled"
#         }
#     }
#  }
#         "CommuniqueType": "ReadRequest",
#         "Header": {
            
#                 # "Url": "/timeclockevent"
#                 "Url": "/timeclockevent/status" 
                
#                 # 1842 and 1859  or check the single 
#                 # "Url": "/timeclockevent/1842/status"   

#         }
#  }

    print(f"\n📤 Sending UpdateRequest to /clientsetting with version {version}...")
    _send_json(sock, request)
    response = _recv_json(sock)
    print(f"\n✅ Response:\n{json.dumps(response, indent=4)}")

def main():
    print("📦 Checking for required certificates...")
    if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
        print("❌ Missing certificates. Run lap_sample.py first.")
        sys.exit()

    print("✅ Certificates found. Establishing secure connection to Lutron processor...")

    try:
        leap_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        leap_context.verify_mode = ssl.CERT_REQUIRED
        leap_context.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
        leap_context.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
        leap_context.check_hostname = False

        sock = socket.create_connection((LUTRON_PROC_ADDRESS, 8081))
        ssock = leap_context.wrap_socket(sock, server_hostname=LUTRON_PROC_HOSTNAME)
        sock.close()
    except Exception as e:
        print(f"❌ Connection error: {e}")
        sys.exit()

    print("✅ Authenticated connection established.")

    # 🔧 Send the UpdateRequest for clientsetting
    send_client_setting_update(ssock, version=3)

    # 🔒 Close connection
    ssock.close()
    print("🔒 Connection closed.")

if __name__ == "__main__":
    main()
