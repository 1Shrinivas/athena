# import os
# import sys
# import json
# import socket
# import ssl

# from definitions import *  # Certs and Lutron processor details

# def _send_json(sock, json_msg):
#     send_msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
#     sock.sendall(send_msg)

# def _recv_json(sock):
#     recv_msg = sock.recv(5000)
#     if len(recv_msg) == 0:
#         return None
#     return json.loads(recv_msg.decode("ASCII"))

# def get_root_area(sock):
#     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
#     response = _recv_json(sock)
#     if response and "Body" in response and "Area" in response["Body"]:
#         return response["Body"]["Area"]
#     return None

# def get_child_areas(sock, area_href):
#     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
#     response = _recv_json(sock)
#     return response.get("Body", {}).get("AreaSummaries", [])

# def get_zones(sock, area_href):
#     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
#     response = _recv_json(sock)
#     return response.get("Body", {}).get("Zones", [])

# def get_scenes(sock, area_href):
#     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/areascene"}})
#     response = _recv_json(sock)
#     return response.get("Body", {}).get("AreaScenes", [])

# def build_area_tree(sock, area, parent_href=None):
#     node = {
#         "href": area["href"],
#         "name": area.get("Name", ""),
#         "is_leaf": area.get("IsLeaf", False),
#         "parent": parent_href,
#         "children": [],
#         "zones": [],
#         "scenes": []
#     }

#     if area.get("IsLeaf", False):
#         node["zones"] = [{
#             "Zone ID": z.get("href", ""),
#             "Name": z.get("Name", ""),
#             "ControlType": z.get("ControlType", ""),
#             "IsLight": z.get("Category", {}).get("IsLight", False),
#             "Associated Area": z.get("AssociatedArea", {}).get("href", "")
#         } for z in get_zones(sock, area["href"])]

#         node["scenes"] = [{
#             "Scene ID": s.get("href", ""),
#             "Name": s.get("Name", ""),
#             "Associated Area": s.get("Parent", {}).get("href", "")
#         } for s in get_scenes(sock, area["href"])]
#     else:
#         for child in get_child_areas(sock, area["href"]):
#             child_node = build_area_tree(sock, child, parent_href=area["href"])
#             node["children"].append(child_node)

#     return node

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
#     root_area = get_root_area(ssock)

#     if not root_area:
#         print("Failed to fetch root area.")
#         sys.exit()

#     full_tree = build_area_tree(ssock, root_area)

#     ssock.close()

#     print("\n Final JSON Structure:")
#     print(json.dumps(full_tree, indent=4))

# if __name__ == "__main__":
#     main()

import os
import sys
import json
import socket
import ssl

from definitions import *  # Certs and Lutron processor details

def _send_json(sock, json_msg):
    send_msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
    sock.sendall(send_msg)

def _recv_json(sock):
    recv_msg = sock.recv(5000)
    if len(recv_msg) == 0:
        return None
    return json.loads(recv_msg.decode("ASCII"))

def get_root_area(sock):
    _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
    response = _recv_json(sock)
    if response and "Body" in response and "Area" in response["Body"]:
        return response["Body"]["Area"]
    return None

def get_child_areas(sock, area_href):
    _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
    response = _recv_json(sock)
    return response.get("Body", {}).get("AreaSummaries", [])

def get_zones(sock, area_href):
    _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
    response = _recv_json(sock)
    return response.get("Body", {}).get("Zones", [])

def get_zone_status(sock, zone_href):
    _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{zone_href}/status"}})
    response = _recv_json(sock)
    return response.get("Body", {}).get("ZoneStatus", {})

def get_area_status(sock, area_href):
    _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/status"}})
    response = _recv_json(sock)
    return response.get("Body", {}).get("AreaStatus", {})

def get_scenes(sock, area_href):
    _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/areascene"}})
    response = _recv_json(sock)
    return response.get("Body", {}).get("AreaScenes", [])

def get_control_stations(sock, area_href):
    _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedcontrolstation"}})
    response = _recv_json(sock)
    return response.get("Body", {}).get("ControlStations", [])

def get_buttons(sock, device_href):
    _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{device_href}/buttongroup/expanded"}})
    response = _recv_json(sock)
    button_groups = response.get("Body", {}).get("ButtonGroupsExpanded", [])
    buttons = []
    for group in button_groups:
        buttons.extend(group.get("Buttons", []))
    return buttons

def build_area_tree(sock, area, parent_href=None):
    node = {
        "href": area["href"],
        "name": area.get("Name", ""),
        "is_leaf": area.get("IsLeaf", False),
        "parent": parent_href,
        "children": [],
        "zones": [],
        "scenes": [],
        "control_stations": [],
        "area_status": {}
    }

    node["area_status"] = get_area_status(sock, area["href"])

    if area.get("IsLeaf", False):
        # Fetch zones and status
        zones = get_zones(sock, area["href"])
        for z in zones:
            zone_status = get_zone_status(sock, z["href"])
            node["zones"].append({
                "Zone ID": z.get("href", ""),
                "Name": z.get("Name", ""),
                "ControlType": z.get("ControlType", ""),
                "IsLight": z.get("Category", {}).get("IsLight", False),
                "Associated Area": z.get("AssociatedArea", {}).get("href", ""),
                "Status": zone_status
            })

        # Fetch scenes
        node["scenes"] = [{
            "Scene ID": s.get("href", ""),
            "Name": s.get("Name", ""),
            "Associated Area": s.get("Parent", {}).get("href", "")
        } for s in get_scenes(sock, area["href"])]

        # Fetch control stations + buttons
        control_stations = get_control_stations(sock, area["href"])
        for cs in control_stations:
            buttons = []
            for dev in cs.get("AssociatedGangedDevices", []):
                dev_href = dev.get("Device", {}).get("href", "")
                if dev_href:
                    buttons.extend(get_buttons(sock, dev_href))
            node["control_stations"].append({
                "ControlStation ID": cs.get("href", ""),
                "Name": cs.get("Name", ""),
                "DeviceType": cs.get("AssociatedGangedDevices", [{}])[0].get("Device", {}).get("DeviceType", ""),
                "Buttons": buttons
            })
    else:
        for child in get_child_areas(sock, area["href"]):
            child_node = build_area_tree(sock, child, parent_href=area["href"])
            node["children"].append(child_node)

    return node

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
    root_area = get_root_area(ssock)

    if not root_area:
        print("Failed to fetch root area.")
        sys.exit()

    full_tree = build_area_tree(ssock, root_area)

    ssock.close()

    print("\n Final JSON Structure with All ReadRequest Data:")
    print(json.dumps(full_tree, indent=4))

if __name__ == "__main__":
    main()
