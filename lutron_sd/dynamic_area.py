# import os
# import sys
# import json
# import socket
# import ssl

# from definitions import *

# def _send_json(socket, json_msg):
#     send_msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
#     socket.sendall(send_msg)

# def _recv_json(socket):
#     recv_msg = socket.recv(5000)
#     if len(recv_msg) == 0:
#         return None
#     return json.loads(recv_msg.decode("ASCII"))

# def get_all_areas(socket):
#     """Fetches all areas from the root area and returns their IDs."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
#     response = _recv_json(socket)

#     if not response:
#         print("Error: No response received from /area/rootarea")
#         return []

#     print(f"Root area response:\n{json.dumps(response, indent=4)}\n")
    
#     areas = []
#     if "Body" in response and "Area" in response["Body"]:
#         root_area = response["Body"]["Area"]
#         areas.append(root_area.get("href", ""))

#     return areas

# def get_child_areas(socket, area_href):
#     """Recursively fetches all child areas and returns only the ones where IsLeaf = True."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
#     response = _recv_json(socket)

#     if not response:
#         print(f"Error: No response received for {area_href}/childarea/summary")
#         return []

#     print(f"Response for {area_href}/childarea/summary:\n{json.dumps(response, indent=4)}\n")

#     leaf_areas = []
#     if "Body" in response and "AreaSummaries" in response["Body"]:
#         for area in response["Body"]["AreaSummaries"]:
#             area_href = area.get("href", "")
#             if area.get("IsLeaf", False):
#                 leaf_areas.append(area_href)
#             else:
#                 leaf_areas.extend(get_child_areas(socket, area_href))

#     return leaf_areas

# def get_associated_zone(socket, area_href):
#     """Fetches associated zone information for a given area."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
#     response = _recv_json(socket)

#     if not response:
#         print(f"Error: No response received for {area_href}/associatedzone")
#         return None

#     print(f"Response for {area_href}/associatedzone:\n{json.dumps(response, indent=4)}\n")
#     return response

# def main():
#     print("Checking for required certificates...")
#     if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
#         print("Error: Missing certificates. Run lap_sample.py first.")
#         sys.exit()
#     print("Certificates found.")

#     print("Establishing a secure connection to Lutron Processor...")
#     try:
#         leap_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
#         leap_context.verify_mode = ssl.CERT_REQUIRED
#         leap_context.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
#         leap_context.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
#         leap_context.check_hostname = False
#         sock = socket.create_connection((LUTRON_PROC_ADDRESS, 8081))
#         ssock = leap_context.wrap_socket(sock, server_hostname=LUTRON_PROC_HOSTNAME)
#         sock.close()
#     except Exception as e:
#         print(f"Error: {e}")
#         sys.exit()
    
#     print("Authenticated connection established.")

#     # Discover all areas
#     discovered_areas = get_all_areas(ssock)
    
#     # Discover all leaf areas dynamically
#     all_leaf_areas = []
#     for area in discovered_areas:
#         all_leaf_areas.extend(get_child_areas(ssock, area))

#     # Discover all associated zones dynamically
#     all_associated_zones = []
#     for area in discovered_areas:
#         zone_info = get_associated_zone(ssock, area)
#         if zone_info:
#             all_associated_zones.append(zone_info)

#     ssock.close()

#     print("\nAll Leaf Areas Found:")
#     print(json.dumps(all_leaf_areas, indent=4))

#     print("\nAll Associated Zones Found:")
#     print(json.dumps(all_associated_zones, indent=4))

# if __name__ == "__main__":
#     main()



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
    return json.loads(recv_msg.decode("ASCII"))

def get_all_areas(socket):
    """Fetches all areas from the root and returns their IDs."""
    _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
    response = _recv_json(socket)

    if not response:
        print("Error: No response received from /area/rootarea")
        return []

    print(f"Root area response:\n{json.dumps(response, indent=4)}\n")

    areas = []
    if "Body" in response and "Area" in response["Body"]:
        root_area = response["Body"]["Area"]
        areas.append(root_area.get("href", ""))

    return areas

def get_child_areas(socket, area_href):
    """Recursively fetches all child areas and returns only the ones where IsLeaf = True."""
    _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
    response = _recv_json(socket)

    if not response:
        print(f"Error: No response received for {area_href}/childarea/summary")
        return []

    print(f"Response for {area_href}/childarea/summary:\n{json.dumps(response, indent=4)}\n")

    leaf_areas = []
    if "Body" in response and "AreaSummaries" in response["Body"]:
        for area in response["Body"]["AreaSummaries"]:
            area_href = area.get("href", "")
            if area.get("IsLeaf", False):
                leaf_areas.append(area_href)
            else:
                leaf_areas.extend(get_child_areas(socket, area_href))

    return leaf_areas

def get_associated_zones(socket, area_href):
    """Fetches associated zones for a given area and handles multiple zones."""
    _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
    response = _recv_json(socket)

    if not response:
        print(f"Error: No response received for {area_href}/associatedzone")
        return []

    print(f"Response for {area_href}/associatedzone:\n{json.dumps(response, indent=4)}\n")

    zones = []
    if "Body" in response and "Zones" in response["Body"]:
        for zone in response["Body"]["Zones"]:
            zone_info = {
                "Zone ID": zone.get("href", ""),
                "Name": zone.get("Name", "Unknown"),
                "ControlType": zone.get("ControlType", "Unknown"),
                "IsLight": zone.get("Category", {}).get("IsLight", False),
                "Associated Area": zone.get("AssociatedArea", {}).get("href", "")
            }
            zones.append(zone_info)
    return zones

def main():
    print("Checking for required certificates...")
    if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
        print("Error: Missing certificates. Run lap_sample.py first.")
        sys.exit()
    print("Certificates found.")

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
    
    print("Authenticated connection established.")

    # Discover all areas
    discovered_areas = get_all_areas(ssock)
    
    # Discover all leaf areas dynamically
    all_leaf_areas = []
    for area in discovered_areas:
        all_leaf_areas.extend(get_child_areas(ssock, area))

    # Discover all associated zones dynamically
    all_associated_zones = []
    for area in discovered_areas:
        zones = get_associated_zones(ssock, area)
        all_associated_zones.extend(zones)

    ssock.close()

    print("\nAll Leaf Areas Found:")
    print(json.dumps(all_leaf_areas, indent=4))

    print("\nAll Associated Zones Found:")
    for zone in all_associated_zones:
        print(json.dumps(zone, indent=4))

if __name__ == "__main__":
    main()
