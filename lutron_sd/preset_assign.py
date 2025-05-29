# import os
# import socket
# import ssl
# import json
# import sys
# from definitions import *

# # Function to send a JSON request over the secure socket connection
# def _send_json(sock, json_msg):
#     message = (json.dumps(json_msg) + "\r\n").encode("ASCII")
#     sock.sendall(message)

# # Function to receive a JSON response from the server
# def _recv_json(sock):
#     response = sock.recv(5000)
#     if not response:
#         return None
#     return json.loads(response.decode("ASCII"))

# # Function to read area information from the Lutron processor
# def read_area_info(sock, area_url):
#     request = {
#         "CommuniqueType": "ReadRequest",
#         "Header": {
#             "Url": area_url
#         }
#     }
#     print(f"Sending ReadRequest to {area_url}...")
#     _send_json(sock, request)
#     response = _recv_json(sock)
#     print(f"ReadResponse for {area_url} received:")
#     print(json.dumps(response, indent=2))
#     return response

# # Function to read button group information for a specific device
# def read_button_group_info(sock, device_url):
#     request = {
#         "CommuniqueType": "ReadRequest",
#         "Header": {
#             "Url": f"{device_url}/buttongroup"
#         }
#     }
#     print(f"Sending ReadRequest to {device_url}/buttongroup...")
#     _send_json(sock, request)
#     response = _recv_json(sock)
#     print(f"ReadResponse for {device_url}/buttongroup received:")

#     if response and "Body" in response and "ButtonGroups" in response["Body"]:
#         button_groups = response["Body"]["ButtonGroups"]
#         print(f"Found {len(button_groups)} button group(s) for device {device_url}:")
#         for button_group in button_groups:
#             print(f"Button Group href: {button_group['href']}")
#             print(f"Category: {button_group['Category']['Type']}")
#             print(f"Programming Type: {button_group['ProgrammingType']}")
#             print(f"Sort Order: {button_group['SortOrder']}")
#             print("Buttons:")
#             for button in button_group["Buttons"]:
#                 print(f"  Button href: {button['href']}")
#             print("\n")
#     else:
#         print("No button groups found in the response.")

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

#     # === Step 1: Read all areas ===
#     request = {
#         "CommuniqueType": "ReadRequest",
#         "Header": {
#             "Url": "/area"
#         }
#     }
#     print("Sending ReadRequest to /area to get all areas...")
#     _send_json(ssock, request)
#     response = _recv_json(ssock)

#     if response and "Body" in response and "Areas" in response["Body"]:
#         areas = response["Body"]["Areas"]
#         print(f"Found {len(areas)} areas:")

#         # === Step 2: Loop through each area ===
#         for area in areas:
#             area_url = area.get("href")
#             print(f"\nChecking details for area: {area['Name']} (href: {area_url})")
#             area_response = read_area_info(ssock, area_url)

#             # === Step 3: Check for devices in the area ===
#             if "Devices" in area_response["Body"]:
#                 devices = area_response["Body"]["Devices"]
#                 print(f"Found {len(devices)} device(s) in area: {area['Name']}")

#                 for device in devices:
#                     device_url = device.get("href")
#                     print(f"Checking button group info for device: {device_url}")
#                     read_button_group_info(ssock, device_url)
#     else:
#         print("No areas found or invalid response.")

#     # === Step 4: Read specific button /button/1148 ===
#     print("\nReading details for button /button/1148...")
#     button_request = {
#         "CommuniqueType": "ReadRequest",
#         "Header": {
#             "Url": "/button/1148"
#         }
#     }
#     _send_json(ssock, button_request)
#     button_response = _recv_json(ssock)

#     if button_response:
#         print("Button /button/1148 read response:")
#         print(json.dumps(button_response, indent=2))
#     else:
#         print("Failed to read button /button/1148.")

#     ssock.close()

# if __name__ == "__main__":
#     main()



import os
import socket
import ssl
import json
from definitions import *

def _send_json(sock, json_msg):
    message = (json.dumps(json_msg) + "\r\n").encode("ASCII")
    sock.sendall(message)

def _recv_json(sock):
    response = sock.recv(5000)
    if not response:
        return None
    return json.loads(response.decode("ASCII"))

def read_area_info(sock, area_url):
    request = {
        "CommuniqueType": "ReadRequest",
        "Header": {
            "Url": area_url
        }
    }
    print(f"Sending ReadRequest to {area_url}...")
    _send_json(sock, request)
    response = _recv_json(sock)
    print(f"ReadResponse for {area_url} received:")
    print(json.dumps(response, indent=2))
    return response

def read_button_group_info(sock, device_url):
    request = {
        "CommuniqueType": "ReadRequest",
        "Header": {
            "Url": f"{device_url}/buttongroup"
        }
    }
    print(f"Sending ReadRequest to {device_url}/buttongroup...")
    _send_json(sock, request)
    response = _recv_json(sock)
    print(f"ReadResponse for {device_url}/buttongroup received:")

    if response and "Body" in response and "ButtonGroups" in response["Body"]:
        button_groups = response["Body"]["ButtonGroups"]
        print(f"Found {len(button_groups)} button group(s) for device {device_url}:")
        for button_group in button_groups:
            print(f"Button Group href: {button_group['href']}")
            print(f"Category: {button_group['Category']['Type']}")
            print(f"Programming Type: {button_group['ProgrammingType']}")
            print(f"Sort Order: {button_group['SortOrder']}")
            print("Buttons:")
            for button in button_group["Buttons"]:
                print(f"  Button href: {button['href']}")
            print("\n")
    else:
        print("No button groups found in the response.")

def read_button_info(sock, button_url):
    print(f"\nReading details for button {button_url}...")
    request = {
        "CommuniqueType": "ReadRequest",
        "Header": {
            "Url": button_url
        }
    }
    _send_json(sock, request)
    response = _recv_json(sock)
    print(f"Button {button_url} read response:")
    print(json.dumps(response, indent=2))
    return response

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

    # Step 1: Read all areas
    request = {
        "CommuniqueType": "ReadRequest",
        "Header": {
            "Url": "/area"
        }
    }
    print("Sending ReadRequest to /area to get all areas...")
    _send_json(ssock, request)
    response = _recv_json(ssock)

    if response and "Body" in response and "Areas" in response["Body"]:
        areas = response["Body"]["Areas"]
        print(f"Found {len(areas)} areas:")
        for area in areas:
            area_url = area.get("href")
            print(f"\nChecking details for area: {area['Name']} (href: {area_url})")
            area_response = read_area_info(ssock, area_url)

            if "Devices" in area_response["Body"]:
                devices = area_response["Body"]["Devices"]
                print(f"Found {len(devices)} device(s) in area: {area['Name']}")
                for device in devices:
                    device_url = device.get("href")
                    print(f"Checking button group info for device: {device_url}")
                    read_button_group_info(ssock, device_url)
    else:
        print("No areas found or invalid response.")

    # === Step 4: Read /button/1148 specifically ===
    button_url = "/button/1148"
    button_response = read_button_info(ssock, button_url)

    # === Step 5: Read parent button group ===
    if button_response and "Body" in button_response and "Button" in button_response["Body"]:
        parent_url = button_response["Body"]["Button"]["Parent"]["href"]
        print(f"\nReading parent button group: {parent_url}")
        _send_json(ssock, {
            "CommuniqueType": "ReadRequest",
            "Header": { "Url": parent_url }
        })
        parent_response = _recv_json(ssock)
        print("Button group read response:")
        print(json.dumps(parent_response, indent=2))

        # === Step 6: Read programming model ===
        program_url = button_response["Body"]["Button"]["ProgrammingModel"]["href"]
        print(f"\nReading programming model: {program_url}")
        _send_json(ssock, {
            "CommuniqueType": "ReadRequest",
            "Header": { "Url": program_url }
        })
        program_response = _recv_json(ssock)
        print("Programming model read response:")
        print(json.dumps(program_response, indent=2))
    else:
        print("Could not extract parent or programming model info.")

    ssock.close()

if __name__ == "__main__":
    main()
