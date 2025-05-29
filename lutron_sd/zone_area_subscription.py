# import os
# import sys
# import json
# import socket
# import ssl
# from definitions import *  # Contains certs and host config

# def _send_json(sock, json_msg):
#     msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
#     sock.sendall(msg)

# def _recv_json(sock):
#     recv_msg = sock.recv(5000)
#     if not recv_msg:
#         return None
#     return json.loads(recv_msg.decode("ASCII"))

# def get_root_area(sock):
#     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
#     response = _recv_json(sock)
#     return response.get("Body", {}).get("Area")

# def get_child_areas(sock, area_href):
#     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
#     response = _recv_json(sock)
#     return response.get("Body", {}).get("AreaSummaries", [])

# def get_zones(sock, area_href):
#     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
#     response = _recv_json(sock)
#     return response.get("Body", {}).get("Zones", [])

# def build_area_tree(sock, area, parent_href=None):
#     node = {
#         "href": area["href"],
#         "name": area.get("Name", ""),
#         "is_leaf": area.get("IsLeaf", False),
#         "parent": parent_href,
#         "children": [],
#         "zones": []
#     }

#     if area.get("IsLeaf", False):
#         zones = get_zones(sock, area["href"])
#         for z in zones:
#             node["zones"].append({
#                 "href": z.get("href"),
#                 "name": z.get("Name", "")
#             })
#     else:
#         for child in get_child_areas(sock, area["href"]):
#             node["children"].append(build_area_tree(sock, child, parent_href=area["href"]))

#     return node

# def collect_status_hrefs(area_node, area_hrefs, zone_hrefs):
#     area_hrefs.append(f"{area_node['href']}/status")
#     for zone in area_node.get("zones", []):
#         zone_hrefs.append(f"{zone['href']}/status")
#     for child in area_node.get("children", []):
#         collect_status_hrefs(child, area_hrefs, zone_hrefs)

# def subscribe(sock, url):
#     _send_json(sock, {
#         "CommuniqueType": "SubscribeRequest",
#         "Header": {"Url": url}
#     })

# def listen_for_updates(sock):
#     print("\n🔔 Listening for real-time Area/Zone updates...\n(Press Ctrl+C to stop)")
#     try:
#         while True:
#             msg = _recv_json(sock)
#             if msg:
#                 print(f"\n🔔 Update: {msg['Header']['Url']}")
#                 print(json.dumps(msg.get("Body", {}), indent=4))
#     except KeyboardInterrupt:
#         print("Stopped listening.")

# def main():
#     # Check certs
#     if not (os.path.isfile(LEAP_SIGNED_CSR_FILE) and os.path.isfile(LEAP_PRIVATE_KEY_FILE)):
#         print("❌ Missing certificates. Run provisioning first.")
#         sys.exit(1)

#     # Connect to Lutron processor
#     print("🔐 Connecting securely to Lutron...")
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
#         print(f"❌ Connection error: {e}")
#         sys.exit(1)

#     print("✅ Connected to Lutron.")

#     # Get root area and build full tree
#     root_area = get_root_area(ssock)
#     if not root_area:
#         print("❌ Could not fetch root area.")
#         sys.exit(1)

#     print("🌳 Building full area tree...")
#     area_tree = build_area_tree(ssock, root_area)

#     # Collect all /status hrefs
#     area_status_hrefs = []
#     zone_status_hrefs = []
#     collect_status_hrefs(area_tree, area_status_hrefs, zone_status_hrefs)

#     print("\n📡 Subscribing to all Area & Zone statuses...")

#     for href in area_status_hrefs:
#         subscribe(ssock, href)
#         print(f"✅ Subscribed to Area: {href}")

#     for href in zone_status_hrefs:
#         subscribe(ssock, href)
#         print(f"✅ Subscribed to Zone: {href}")

#     # Start listening for updates
#     listen_for_updates(ssock)

# if __name__ == "__main__":
#     main()



import os
import sys
import json
import socket
import ssl
from definitions import *  # Contains certs and host config

def _send_json(sock, json_msg):
    msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
    sock.sendall(msg)

def _recv_json(sock):
    recv_msg = sock.recv(5000)
    if not recv_msg:
        return None
    return json.loads(recv_msg.decode("ASCII"))

def get_root_area(sock):
    _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
    response = _recv_json(sock)
    return response.get("Body", {}).get("Area")

def get_child_areas(sock, area_href):
    _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
    response = _recv_json(sock)
    return response.get("Body", {}).get("AreaSummaries", [])

def get_zones(sock, area_href):
    _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
    response = _recv_json(sock)
    return response.get("Body", {}).get("Zones", [])

def build_area_tree(sock, area, parent_href=None):
    node = {
        "href": area["href"],
        "name": area.get("Name", ""),
        "is_leaf": area.get("IsLeaf", False),
        "parent": parent_href,
        "children": [],
        "zones": []
    }

    if area.get("IsLeaf", False):
        zones = get_zones(sock, area["href"])
        for z in zones:
            node["zones"].append({
                "href": z.get("href"),
                "name": z.get("Name", "")
            })
    else:
        for child in get_child_areas(sock, area["href"]):
            node["children"].append(build_area_tree(sock, child, parent_href=area["href"]))

    return node

def collect_status_hrefs(area_node, area_hrefs, zone_hrefs):
    area_hrefs.append(f"{area_node['href']}/status")
    for zone in area_node.get("zones", []):
        zone_hrefs.append(f"{zone['href']}/status")
    for child in area_node.get("children", []):
        collect_status_hrefs(child, area_hrefs, zone_hrefs)

def subscribe(sock, url):
    _send_json(sock, {
        "CommuniqueType": "SubscribeRequest",
        "Header": {"Url": url}
    })

def check_area_occupancy(area_status_msg):
    """
    area_status_msg: dict containing the "AreaStatus" dictionary
    Checks occupancy status and prints Occupied/Unoccupied summary.
    """
    area_status = area_status_msg.get("AreaStatus", {})
    occupancy = area_status.get("OccupancyStatus")
    if occupancy:
        if occupancy.lower() == "occupied":
            print("🏢 Area is currently OCCUPIED.")
        elif occupancy.lower() == "unoccupied":
            print("🏢 Area is currently UNOCCUPIED.")
        else:
            print(f"🏢 Area Occupancy Status: {occupancy}")

def listen_for_updates(sock):
    print("\n🔔 Listening for real-time Area/Zone updates...\n(Press Ctrl+C to stop)")
    try:
        while True:
            msg = _recv_json(sock)
            if msg:
                url = msg['Header']['Url']
                print(f"\n🔔 Update: {url}")
                print(json.dumps(msg.get("Body", {}), indent=4))

                # If it's an area status update, check occupancy
                if url.endswith("/status") and "/area/" in url:
                    check_area_occupancy(msg.get("Body", {}))

    except KeyboardInterrupt:
        print("Stopped listening.")

def main():
    # Check certs
    if not (os.path.isfile(LEAP_SIGNED_CSR_FILE) and os.path.isfile(LEAP_PRIVATE_KEY_FILE)):
        print("❌ Missing certificates. Run provisioning first.")
        sys.exit(1)

    # Connect to Lutron processor
    print("🔐 Connecting securely to Lutron...")
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
        sys.exit(1)

    print("✅ Connected to Lutron.")

    # Get root area and build full tree
    root_area = get_root_area(ssock)
    if not root_area:
        print("❌ Could not fetch root area.")
        sys.exit(1)

    print("🌳 Building full area tree...")
    area_tree = build_area_tree(ssock, root_area)

    # Collect all /status hrefs
    area_status_hrefs = []
    zone_status_hrefs = []
    collect_status_hrefs(area_tree, area_status_hrefs, zone_status_hrefs)

    print("\n📡 Subscribing to all Area & Zone statuses...")

    for href in area_status_hrefs:
        subscribe(ssock, href)
        print(f"✅ Subscribed to Area: {href}")

    for href in zone_status_hrefs:
        subscribe(ssock, href)
        print(f"✅ Subscribed to Zone: {href}")

    # Start listening for updates
    listen_for_updates(ssock)

if __name__ == "__main__":
    main()
