
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

# def get_all_areas(socket, area_href="/area/rootarea"):
#     """Recursively fetches all areas, both leaf and non-leaf, and finds associated zones."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": area_href}})
#     response = _recv_json(socket)

#     if not response:
#         print(f"Error: No response received from {area_href}")
#         return [], []

#     print(f"Response for {area_href}:\n{json.dumps(response, indent=4)}\n")

#     areas = []
#     zones = []

#     if "Body" in response and "Area" in response["Body"]:
#         area = response["Body"]["Area"]
#         area_href = area.get("href", "")
#         is_leaf = area.get("IsLeaf", False)
#         areas.append({"href": area_href, "name": area.get("Name", "Unknown"), "is_leaf": is_leaf})

#         # Fetch associated zones for this area
#         zones.extend(get_associated_zones(socket, area_href))

#         # Recursively find child areas if not a leaf
#         if not is_leaf:
#             child_areas, child_zones = get_child_areas(socket, area_href)
#             areas.extend(child_areas)
#             zones.extend(child_zones)

#     return areas, zones

# def get_child_areas(socket, parent_href):
#     """Recursively discovers all child areas under a parent."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{parent_href}/childarea/summary"}})
#     response = _recv_json(socket)

#     if not response:
#         print(f"Error: No response received for {parent_href}/childarea/summary")
#         return [], []

#     print(f"Response for {parent_href}/childarea/summary:\n{json.dumps(response, indent=4)}\n")

#     areas = []
#     zones = []

#     if "Body" in response and "AreaSummaries" in response["Body"]:
#         for area in response["Body"]["AreaSummaries"]:
#             area_href = area.get("href", "")
#             is_leaf = area.get("IsLeaf", False)
#             areas.append({"href": area_href, "name": area.get("Name", "Unknown"), "is_leaf": is_leaf})

#             # Fetch associated zones
#             zones.extend(get_associated_zones(socket, area_href))

#             # Recursively get child areas if not a leaf
#             if not is_leaf:
#                 child_areas, child_zones = get_child_areas(socket, area_href)
#                 areas.extend(child_areas)
#                 zones.extend(child_zones)

#     return areas, zones

# def get_associated_zones(socket, area_href):
#     """Fetches associated zones for a given area."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
#     response = _recv_json(socket)

#     if not response:
#         print(f"Error: No response received for {area_href}/associatedzone")
#         return []

#     print(f"Response for {area_href}/associatedzone:\n{json.dumps(response, indent=4)}\n")

#     zones = []
#     if "Body" in response and "Zones" in response["Body"]:
#         for zone in response["Body"]["Zones"]:
#             zone_info = {
#                 "Zone ID": zone.get("href", ""),
#                 "Name": zone.get("Name", "Unknown"),
#                 "ControlType": zone.get("ControlType", "Unknown"),
#                 "IsLight": zone.get("Category", {}).get("IsLight", False),
#                 "Associated Area": zone.get("AssociatedArea", {}).get("href", "")
#             }
#             zones.append(zone_info)

#     return zones

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

#     # Recursively discover all areas and zones
#     all_areas, all_zones = get_all_areas(ssock)

#     ssock.close()

#     print("\nAll Areas Found (Leaf and Non-Leaf):")
#     print(json.dumps(all_areas, indent=4))

#     print("\nAll Associated Zones Found:")
#     for zone in all_zones:
#         print(json.dumps(zone, indent=4))

# if __name__ == "__main__":
#     main()


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

# def get_all_areas(socket, area_href="/area/rootarea"):
#     """Recursively fetches all areas, both leaf and non-leaf, and finds associated zones."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": area_href}})
#     response = _recv_json(socket)

#     if not response:
#         print(f"Error: No response received from {area_href}")
#         return [], [], []

#     print(f"Response for {area_href}:\n{json.dumps(response, indent=4)}\n")

#     areas = []
#     zones = []
#     area_scenes = []  # Store scene information for leaf areas

#     if "Body" in response and "Area" in response["Body"]:
#         area = response["Body"]["Area"]
#         area_href = area.get("href", "")
#         is_leaf = area.get("IsLeaf", False)
#         area_info = {"href": area_href, "name": area.get("Name", "Unknown"), "is_leaf": is_leaf}
#         areas.append(area_info)

#         # Fetch associated zones for this area
#         zones.extend(get_associated_zones(socket, area_href))

#         if is_leaf:
#             # Fetch area scenes for leaf areas
#             area_scenes.extend(get_area_scenes(socket, area_href))
#         else:
#             # Recursively find child areas
#             child_areas, child_zones, child_scenes = get_child_areas(socket, area_href)
#             areas.extend(child_areas)
#             zones.extend(child_zones)
#             area_scenes.extend(child_scenes)

#     return areas, zones, area_scenes

# # def get_child_areas(socket, parent_href):
# #     """Recursively discovers all child areas under a parent."""
# #     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{parent_href}/childarea/summary"}})
# #     response = _recv_json(socket)

# #     if not response:
# #         print(f"Error: No response received for {parent_href}/childarea/summary")
# #         return [], [], []

# #     print(f"Response for {parent_href}/childarea/summary:\n{json.dumps(response, indent=4)}\n")

# #     areas = []
# #     zones = []
# #     area_scenes = []
# #     all_child = []

# #     if "Body" in response and "AreaSummaries" in response["Body"]:
# #         for area in response["Body"]["AreaSummaries"]:
# #             area_href = area.get("href", "")
# #             is_leaf = area.get("IsLeaf", False)
# #             area_info = {"href": area_href, "name": area.get("Name", "Unknown"), "is_leaf": is_leaf}
# #             areas.append(area_info)

# #             # Fetch associated zones
# #             zones.extend(get_associated_zones(socket, area_href))
# #             all_child.extend(get_child_areas(socket,area_href))

# #             if is_leaf:
# #                 # Fetch area scenes for leaf areas
# #                 area_scenes.extend(get_area_scenes(socket, area_href))
# #             else:
# #                 # Recursively get child areas
# #                 child_areas, child_zones, child_scenes = get_child_areas(socket, area_href)
# #                 areas.extend(child_areas)
# #                 zones.extend(child_zones)
# #                 area_scenes.extend(child_scenes)

# #     return areas, zones, area_scenes, child_scenes

# def get_child_areas(socket, parent_href):
#     """Recursively discovers all child areas under a parent."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{parent_href}/childarea/summary"}})
#     response = _recv_json(socket)

#     if not response:
#         print(f"Error: No response received for {parent_href}/childarea/summary")
#         return [], [], [], []  # Ensure all return values are defined

#     print(f"Response for {parent_href}/childarea/summary:\n{json.dumps(response, indent=4)}\n")

#     areas = []
#     zones = []
#     area_scenes = []
#     child_scenes = []  # Initialize child_scenes properly
#     all_child = []

#     if "Body" in response and "AreaSummaries" in response["Body"]:
#         for area in response["Body"]["AreaSummaries"]:
#             area_href = area.get("href", "")
#             is_leaf = area.get("IsLeaf", False)
#             area_info = {"href": area_href, "name": area.get("Name", "Unknown"), "is_leaf": is_leaf}
#             areas.append(area_info)

#             # Fetch associated zones
#             zones.extend(get_associated_zones(socket, area_href))
#             all_child.extend(get_child_areas(socket, area_href))

#             if is_leaf:
#                 # Fetch area scenes for leaf areas
#                 area_scenes.extend(get_area_scenes(socket, area_href))
#             else:
#                 # Recursively get child areas
#                 child_areas, child_zones, new_child_scenes, new_all_child = get_child_areas(socket, area_href)
#                 areas.extend(child_areas)
#                 zones.extend(child_zones)
#                 child_scenes.extend(new_child_scenes)  # Store the retrieved child scenes
#                 all_child.extend(new_all_child)

#     return areas, zones, area_scenes, child_scenes  # Now child_scenes is properly initialized

# def get_associated_zones(socket, area_href):
#     """Fetches associated zones for a given area."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
#     response = _recv_json(socket)

#     if not response:
#         print(f"Error: No response received for {area_href}/associatedzone")
#         return []

#     print(f"Response for {area_href}/associatedzone:\n{json.dumps(response, indent=4)}\n")

#     zones = []
#     if "Body" in response and "Zones" in response["Body"]:
#         for zone in response["Body"]["Zones"]:
#             zone_info = {
#                 "Zone ID": zone.get("href", ""),
#                 "Name": zone.get("Name", "Unknown"),
#                 "ControlType": zone.get("ControlType", "Unknown"),
#                 "IsLight": zone.get("Category", {}).get("IsLight", False),
#                 "Associated Area": zone.get("AssociatedArea", {}).get("href", "")
#             }
#             zones.append(zone_info)

#     return zones

# def get_area_scenes(socket, area_href):
#     """Fetches all scenes associated with a leaf area."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/areascene"}})
#     response = _recv_json(socket)

#     if not response:
#         print(f"Error: No response received for {area_href}/areascene")
#         return []

#     print(f"Response for {area_href}/areascene:\n{json.dumps(response, indent=4)}\n")

#     scenes = []
#     if "Body" in response and "AreaScenes" in response["Body"]:
#         for scene in response["Body"]["AreaScenes"]:
#             scene_info = {
#                 "Scene ID": scene.get("href", ""),
#                 "Name": scene.get("Name", "Unknown"),
#                 "Associated Area": area_href
#             }
#             scenes.append(scene_info)

#     return scenes

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

#     # Recursively discover all areas, zones, and scenes
#     all_areas, all_zones, all_scenes,all_child= get_all_areas(ssock)

#     ssock.close()

#     print("\nAll Areas Found (Leaf and Non-Leaf):")
#     print(json.dumps(all_areas, indent=4))
    
#     print("\nAll Associated Zones Found:")
#     for child in all_child:
#         print(json.dumps(child, indent=4))
        
#     print("\nAll Associated Zones Found:")
#     for zone in all_zones:
#         print(json.dumps(zone, indent=4))

#     print("\nAll Area Scenes Found:")
#     for scene in all_scenes:
#         print(json.dumps(scene, indent=4))

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

def get_scenes(sock, area_href):
    _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/areascene"}})
    response = _recv_json(sock)
    return response.get("Body", {}).get("AreaScenes", [])

def build_area_tree(sock, area, parent_href=None):
    node = {
        "href": area["href"],
        "name": area.get("Name", ""),
        "is_leaf": area.get("IsLeaf", False),
        "parent": parent_href,
        "children": [],
        "zones": [],
        "scenes": []
    }

    if area.get("IsLeaf", False):
        node["zones"] = [{
            "Zone ID": z.get("href", ""),
            "Name": z.get("Name", ""),
            "ControlType": z.get("ControlType", ""),
            "IsLight": z.get("Category", {}).get("IsLight", False),
            "Associated Area": z.get("AssociatedArea", {}).get("href", "")
        } for z in get_zones(sock, area["href"])]

        node["scenes"] = [{
            "Scene ID": s.get("href", ""),
            "Name": s.get("Name", ""),
            "Associated Area": s.get("Parent", {}).get("href", "")
        } for s in get_scenes(sock, area["href"])]
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

    print("\n Final JSON Structure:")
    print(json.dumps(full_tree, indent=4))

if __name__ == "__main__":
    main()


# import os
# import sys
# import json
# import socket
# import ssl
# import logging

# from definitions import *

# def _send_json(socket, json_msg):
#     """Send JSON data over the socket."""
#     send_msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
#     socket.sendall(send_msg)

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# def _recv_json(socket):
#     """Receive JSON data from the socket."""
#     recv_msg = socket.recv(5000)
#     if len(recv_msg) == 0:
#         logging.error("No data received")
#         return None
#     return json.loads(recv_msg.decode("ASCII"))


# def get_all_areas(socket, area_href="/area/rootarea"):
#     """Recursively fetch all areas, both leaf and non-leaf, and find associated zones."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": area_href}})
#     response = _recv_json(socket)

#     if not response:
#         print(f"Error: No response received from {area_href}")
#         return [], [], []

#     print(f"Response for {area_href}:\n{json.dumps(response, indent=4)}\n")

#     areas = []
#     zones = []
#     area_scenes = []  # Store scene information for leaf areas

#     if "Body" in response and "Area" in response["Body"]:
#         area = response["Body"]["Area"]
#         area_href = area.get("href", "")
#         is_leaf = area.get("IsLeaf", False)
#         area_info = {"href": area_href, "name": area.get("Name", "Unknown"), "is_leaf": is_leaf}
#         areas.append(area_info)

#         # Fetch associated zones for this area
#         zones.extend(get_associated_zones(socket, area_href))

#         if is_leaf:
#             # Fetch area scenes for leaf areas
#             area_scenes.extend(get_area_scenes(socket, area_href))
#         else:
#             # Recursively find child areas
#             child_areas, child_zones, child_scenes, _ = get_child_areas(socket, area_href)
#             areas.extend(child_areas)
#             zones.extend(child_zones)
#             area_scenes.extend(child_scenes)

#     return areas, zones, area_scenes

# def get_child_areas(socket, parent_href):
#     """Recursively discovers all child areas under a parent."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{parent_href}/childarea/summary"}})
#     response = _recv_json(socket)

#     if not response:
#         print(f"Error: No response received for {parent_href}/childarea/summary")
#         return [], [], [], []

#     print(f"Response for {parent_href}/childarea/summary:\n{json.dumps(response, indent=4)}\n")

#     areas = []
#     zones = []
#     area_scenes = []
#     child_scenes = []

#     if "Body" in response and "AreaSummaries" in response["Body"]:
#         for area in response["Body"]["AreaSummaries"]:
#             area_href = area.get("href", "")
#             is_leaf = area.get("IsLeaf", False)
#             area_info = {"href": area_href, "name": area.get("Name", "Unknown"), "is_leaf": is_leaf}
#             areas.append(area_info)

#             # Fetch associated zones
#             zones.extend(get_associated_zones(socket, area_href))

#             if is_leaf:
#                 # Fetch area scenes for leaf areas
#                 area_scenes.extend(get_area_scenes(socket, area_href))
#             else:
#                 # Recursively get child areas
#                 child_areas, child_zones, new_child_scenes, _ = get_child_areas(socket, area_href)
#                 areas.extend(child_areas)
#                 zones.extend(child_zones)
#                 child_scenes.extend(new_child_scenes)

#     return areas, zones, area_scenes, child_scenes

# def get_associated_zones(socket, area_href):
#     """Fetch associated zones for a given area."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
#     response = _recv_json(socket)

#     if not response:
#         print(f"Error: No response received for {area_href}/associatedzone")
#         return []

#     print(f"Response for {area_href}/associatedzone:\n{json.dumps(response, indent=4)}\n")

#     zones = []
#     if "Body" in response and "Zones" in response["Body"]:
#         for zone in response["Body"]["Zones"]:
#             zone_info = {
#                 "Zone ID": zone.get("href", ""),
#                 "Name": zone.get("Name", "Unknown"),
#                 "ControlType": zone.get("ControlType", "Unknown"),
#                 "IsLight": zone.get("Category", {}).get("IsLight", False),
#                 "Associated Area": zone.get("AssociatedArea", {}).get("href", "")
#             }
#             zones.append(zone_info)

#     return zones

# def get_area_scenes(socket, area_href):
#     """Fetch all scenes associated with a leaf area."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/areascene"}})
#     response = _recv_json(socket)

#     if not response:
#         print(f"Error: No response received for {area_href}/areascene")
#         return []

#     print(f"Response for {area_href}/areascene:\n{json.dumps(response, indent=4)}\n")

#     scenes = []
#     if "Body" in response and "AreaScenes" in response["Body"]:
#         for scene in response["Body"]["AreaScenes"]:
#             scene_info = {
#                 "Scene ID": scene.get("href", ""),
#                 "Name": scene.get("Name", "Unknown"),
#                 "Associated Area": area_href
#             }
#             scenes.append(scene_info)

#     return scenes

# def main():
#     print("Checking for required certificates...")
#     if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
#         print("Error: Missing certificates. Run lap_sample.py first.")
#         sys.exit()

#     print("Certificates found. Establishing a secure connection to Lutron Processor...")

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

#     # Recursively discover all areas, zones, and scenes
#     all_areas, all_zones, all_scenes = get_all_areas(ssock)

#     ssock.close()

#     print("\nAll Areas Found (Leaf and Non-Leaf):")
#     print(json.dumps(all_areas, indent=4))

#     print("\nAll Associated Zones Found:")
#     print(json.dumps(all_zones, indent=4))

#     print("\nAll Area Scenes Found:")
#     print(json.dumps(all_scenes, indent=4))
    
# logging.info(f"Response for {area_href}:\n{json.dumps(response, indent=4)}\n")


# if __name__ == "__main__":
#     main()


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
#     """Recursively fetches all areas, both leaf and non-leaf, and finds associated zones and scenes."""
#     final_result = {
#         "areas": [],
#         "zones": [],
#         "scenes": []
#     }

#     all_leaf_areas = []

#     def collect_areas(area_href):
#         """Recursively collects all areas."""
#         _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
#         response = _recv_json(socket)
        
#         if "Body" in response and "AreaSummaries" in response["Body"]:
#             for area in response["Body"]["AreaSummaries"]:
#                 final_result["areas"].append({
#                     "href": area["href"],
#                     "name": area.get("Name", ""),
#                     "is_leaf": area.get("IsLeaf", False)
#                 })
#                 if area.get("IsLeaf", False):
#                     all_leaf_areas.append(area["href"])
#                 else:
#                     collect_areas(area["href"])

#     # Discover root area
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
#     response = _recv_json(socket)

#     if "Body" in response and "Area" in response["Body"]:
#         area = response["Body"]["Area"]
#         final_result["areas"].append({
#             "href": area["href"],
#             "name": area.get("Name", ""),
#             "is_leaf": area.get("IsLeaf", False)
#         })
#         if not area.get("IsLeaf", False):
#             collect_areas(area["href"])
#         else:
#             all_leaf_areas.append(area["href"])

#     # Collect zones and scenes
#     for area_href in all_leaf_areas:
#         # Fetch associated zones
#         _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
#         zone_response = _recv_json(socket)
#         if "Body" in zone_response and "Zones" in zone_response["Body"]:
#             for zone in zone_response["Body"]["Zones"]:
#                 final_result["zones"].append({
#                     "Zone ID": zone.get("href", ""),
#                     "Name": zone.get("Name", ""),
#                     "ControlType": zone.get("ControlType", ""),
#                     "IsLight": zone.get("Category", {}).get("IsLight", False),
#                     "Associated Area": zone.get("AssociatedArea", {}).get("href", "")
#                 })

#         # Fetch associated scenes
#         _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/areascene"}})
#         scene_response = _recv_json(socket)
#         if "Body" in scene_response and "AreaScenes" in scene_response["Body"]:
#             for scene in scene_response["Body"]["AreaScenes"]:
#                 final_result["scenes"].append({
#                     "Scene ID": scene.get("href", ""),
#                     "Name": scene.get("Name", ""),
#                     "Associated Area": scene.get("Parent", {}).get("href", "")
#                 })

#     return final_result

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

#     # Fetch all areas, zones, and scenes
#     final_result = get_all_areas(ssock)
#     ssock.close()

#     # Print final consolidated JSON
#     print(json.dumps(final_result, indent=4))

# if __name__ == "__main__":
#     main()
