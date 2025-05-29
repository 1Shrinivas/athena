

import os
import sys
import json
import socket
import ssl

from definitions import *

def _send_json(socket, json_msg):
    send_msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
    socket.sendall(send_msg)

def _recv_json(socket):
    recv_msg = socket.recv(5000)
    if len(recv_msg) == 0:
        return None
    else:
        return json.loads(recv_msg.decode("ASCII"))

def get_child_areas(socket, area_href):
    """
    Recursively fetches all child areas under the given area_href 
    and returns only the areas where IsLeaf = True.
    """
    _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
    response = _recv_json(socket)

    if not response:
        print(f"Error: No response received for {area_href}\n")
        return []

    print(f"Response for {area_href}:\n{json.dumps(response, indent=4)}\n")

    leaf_areas = []
    body = response.get("Body", {})

    if "AreaSummaries" in body:
        for area in body["AreaSummaries"]:
            area_name = area.get("Name", "Unknown")
            area_href = area.get("href", "")

            if area.get("IsLeaf", False):
                print(f"Found Leaf Area: {area_name} ({area_href})\n")
                leaf_areas.append(area)
            else:
                print(f"Exploring non-leaf area: {area_name} ({area_href})\n")
                leaf_areas.extend(get_child_areas(socket, area_href))

    return leaf_areas

def get_associated_zone(socket, area_href):
    """
    Fetches associated zone information for a given area.
    """
    _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
    response = _recv_json(socket)

    if not response:
        print(f"Error: No response received for {area_href}/associatedzone\n")
        return None

    print(f"Response for {area_href}/associatedzone:\n{json.dumps(response, indent=4)}\n")
    return response

def main():
    print("Look for certs")
    if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
        print("Error: You need to run lap_sample.py first to generate the keys needed for the API connection")
        sys.exit()
    print("Success")

    print("Establishing a secure connection to Lutron Processor...")
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
        print(f"Error: {e}")
        sys.exit()

    print("Success: Authenticated connection established")

    # List of predefined URLs to query
    urls_to_query = [
        "/area/rootarea",
        "/area/3/childarea/summary",
        "/area/114/childarea/summary",
        "/area/127/childarea/summary",
        "/area/983/associatedzone",
        "/area/1009/associatedzone"
    ]

    all_leaf_areas = []

    for url in urls_to_query:
        if "childarea/summary" in url:
            all_leaf_areas.extend(get_child_areas(ssock, url.replace("/childarea/summary", "")))
        elif "associatedzone" in url:
            get_associated_zone(ssock, url.replace("/associatedzone", ""))

    ssock.close()

    # Print final result
    print("\nAll Leaf Areas Found:")
    print(json.dumps(all_leaf_areas, indent=4))

if __name__ == "__main__":
    main()
