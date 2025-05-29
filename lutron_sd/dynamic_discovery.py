# # import os
# # import sys
# # import json
# # import socket
# # import ssl

# # from definitions import *

# # def _send_json(socket, json_msg):
# #     send_msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
# #     socket.sendall(send_msg)

# # def _recv_json(socket):
# #     recv_msg = socket.recv(5000)
# #     if len(recv_msg) == 0:
# #         return None
# #     return json.loads(recv_msg.decode("ASCII"))

# # def get_all_areas(socket):
# #     """Fetches all areas from the root area and returns their IDs."""
# #     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
# #     response = _recv_json(socket)

# #     if not response:
# #         print("Error: No response received from /area/rootarea")
# #         return []

# #     print(f"Root area response:\n{json.dumps(response, indent=4)}\n")
    
# #     areas = []
# #     if "Body" in response and "Area" in response["Body"]:
# #         root_area = response["Body"]["Area"]
# #         areas.append(root_area.get("href", ""))

# #     return areas

# # def get_child_areas(socket, area_href):
# #     """Recursively fetches all child areas and returns only the ones where IsLeaf = True."""
# #     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
# #     response = _recv_json(socket)

# #     if not response:
# #         print(f"Error: No response received for {area_href}/childarea/summary")
# #         return []

# #     print(f"Response for {area_href}/childarea/summary:\n{json.dumps(response, indent=4)}\n")

# #     leaf_areas = []
# #     if "Body" in response and "AreaSummaries" in response["Body"]:
# #         for area in response["Body"]["AreaSummaries"]:
# #             area_href = area.get("href", "")
# #             if area.get("IsLeaf", False):
# #                 leaf_areas.append(area_href)
# #             else:
# #                 leaf_areas.extend(get_child_areas(socket, area_href))

# #     return leaf_areas

# # def get_associated_zone(socket, area_href):
# #     """Fetches associated zone information for a given area."""
# #     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
# #     response = _recv_json(socket)

# #     if not response:
# #         print(f"Error: No response received for {area_href}/associatedzone")
# #         return None

# #     print(f"Response for {area_href}/associatedzone:\n{json.dumps(response, indent=4)}\n")
# #     return response

# # def main():
# #     print("Checking for required certificates...")
# #     if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
# #         print("Error: Missing certificates. Run lap_sample.py first.")
# #         sys.exit()
# #     print("Certificates found.")

# #     print("Establishing a secure connection to Lutron Processor...")
# #     try:
# #         leap_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# #         leap_context.verify_mode = ssl.CERT_REQUIRED
# #         leap_context.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
# #         leap_context.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
# #         leap_context.check_hostname = False
# #         sock = socket.create_connection((LUTRON_PROC_ADDRESS, 8081))
# #         ssock = leap_context.wrap_socket(sock, server_hostname=LUTRON_PROC_HOSTNAME)
# #         sock.close()
# #     except Exception as e:
# #         print(f"Error: {e}")
# #         sys.exit()
    
# #     print("Authenticated connection established.")

# #     # Discover all areas
# #     discovered_areas = get_all_areas(ssock)
    
# #     # Discover all leaf areas dynamically
# #     all_leaf_areas = []
# #     for area in discovered_areas:
# #         all_leaf_areas.extend(get_child_areas(ssock, area))

# #     # Discover all associated zones dynamically
# #     all_associated_zones = []
# #     for area in discovered_areas:
# #         zone_info = get_associated_zone(ssock, area)
# #         if zone_info:
# #             all_associated_zones.append(zone_info)

# #     ssock.close()

# #     print("\nAll Leaf Areas Found:")
# #     print(json.dumps(all_leaf_areas, indent=4))

# #     print("\nAll Associated Zones Found:")
# #     print(json.dumps(all_associated_zones, indent=4))

# # if __name__ == "__main__":
# #     main()


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

def get_all_areas(socket, area_href="/area/rootarea"):
    """Recursively fetches all areas, both leaf and non-leaf, and finds associated zones."""
    _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": area_href}})
    response = _recv_json(socket)

    if not response:
        print(f"Error: No response received from {area_href}")
        return [], []

    print(f"Response for {area_href}:\n{json.dumps(response, indent=4)}\n")

    areas = []
    zones = []

    if "Body" in response and "Area" in response["Body"]:
        area = response["Body"]["Area"]
        area_href = area.get("href", "")
        is_leaf = area.get("IsLeaf", False)
        areas.append({"href": area_href, "name": area.get("Name", "Unknown"), "is_leaf": is_leaf})

        # Fetch associated zones for this area
        zones.extend(get_associated_zones(socket, area_href))

        # Recursively find child areas if not a leaf
        if not is_leaf:
            child_areas, child_zones = get_child_areas(socket, area_href)
            areas.extend(child_areas)
            zones.extend(child_zones)

    return areas, zones

def get_child_areas(socket, parent_href):
    """Recursively discovers all child areas under a parent."""
    _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{parent_href}/childarea/summary"}})
    response = _recv_json(socket)

    if not response:
        print(f"Error: No response received for {parent_href}/childarea/summary")
        return [], []

    print(f"Response for {parent_href}/childarea/summary:\n{json.dumps(response, indent=4)}\n")

    areas = []
    zones = []

    if "Body" in response and "AreaSummaries" in response["Body"]:
        for area in response["Body"]["AreaSummaries"]:
            area_href = area.get("href", "")
            is_leaf = area.get("IsLeaf", False)
            areas.append({"href": area_href, "name": area.get("Name", "Unknown"), "is_leaf": is_leaf})

            # Fetch associated zones
            zones.extend(get_associated_zones(socket, area_href))

            # Recursively get child areas if not a leaf
            if not is_leaf:
                child_areas, child_zones = get_child_areas(socket, area_href)
                areas.extend(child_areas)
                zones.extend(child_zones)

    return areas, zones

def get_associated_zones(socket, area_href):
    """Fetches associated zones for a given area."""
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

    # Recursively discover all areas and zones
    all_areas, all_zones = get_all_areas(ssock)

    ssock.close()

    print("\nAll Areas Found (Leaf and Non-Leaf):")
    print(json.dumps(all_areas, indent=4))

    print("\nAll Associated Zones Found:")
    for zone in all_zones:
        print(json.dumps(zone, indent=4))

if __name__ == "__main__":
    main()


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
#     """Fetches all areas from the root and returns their IDs."""
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

# def get_associated_zones(socket, area_href):
#     """Fetches associated zones for a given area and handles multiple zones."""
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

#     # Discover all areas
#     discovered_areas = get_all_areas(ssock)
    
#     # Discover all leaf areas dynamically
#     all_leaf_areas = []
#     for area in discovered_areas:
#         all_leaf_areas.extend(get_child_areas(ssock, area))

#     # Discover all associated zones dynamically
#     all_associated_zones = []
#     for area in discovered_areas:
#         zones = get_associated_zones(ssock, area)
#         all_associated_zones.extend(zones)

#     ssock.close()

#     print("\nAll Leaf Areas Found:")
#     print(json.dumps(all_leaf_areas, indent=4))

#     print("\nAll Associated Zones Found:")
#     for zone in all_associated_zones:
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
#     else:
#         return json.loads(recv_msg.decode("ASCII"))

# def discover_areas(socket, area_href="/area/rootarea"):
#     """
#     Recursively discovers areas starting from the given area_href.
#     """
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": area_href}})
#     response = _recv_json(socket)

#     if not response or "Body" not in response:
#         print(f"Error: Invalid response for {area_href}")
#         return

#     # Check if the response contains an area with child areas
#     body = response["Body"]
    
#     if "Area" in body:
#         area = body["Area"]
#         print(f"Found Area: {area['Name']} (Leaf: {area.get('IsLeaf', False)})")

#         # If it's a leaf area, stop here
#         if area.get("IsLeaf", False):
#             return
        
#         # Otherwise, check child areas
#         area_id = area['href'].split('/')[-1]
#         child_url = f"/area/{area_id}/childarea/summary"
#         discover_areas(socket, child_url)

#     elif "AreaSummaries" in body:
#         for child_area in body["AreaSummaries"]:
#             print(f"Exploring: {child_area['Name']} (Leaf: {child_area.get('IsLeaf', False)})")
#             if child_area.get("IsLeaf", False):
#                 continue
#             child_href = child_area["href"]
#             discover_areas(socket, child_href)

# def main():
#     print("Look for certs")
#     if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
#         print("Error: You need to run lap_sample.py first to generate the keys needed for the API connection")
#         sys.exit()
#     print("Success")

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

#     print("Success: Authenticated connection established")

#     # Start discovery from root area
#     print("Starting area discovery...")
#     discover_areas(ssock, "/area/rootarea")

#     ssock.close()
#     print("Discovery complete.")

# if __name__ == "__main__":
#     main()


# import os
# import sys
# import json
# import socket
# import ssl

# from definitions import *

# URLS_TO_CHECK = [
#     "/area/rootarea",
#     "/area/3/childarea/summary",
#     "/area/114/childarea/summary",
#     "/area/127/childarea/summary",
#     "/area/983/associatedzone",
#     "/area/983/associatedzone"
# ]

# def _send_json(socket, json_msg):
#     send_msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
#     socket.sendall(send_msg)

# def _recv_json(socket):
#     recv_msg = socket.recv(5000)
#     if len(recv_msg) == 0:
#         return None
#     else:
#         return json.loads(recv_msg.decode("ASCII"))

# def check_leaf_status(socket, area_href):
#     """
#     Checks the 'IsLeaf' status of a given area and prints the full response.
#     """
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": area_href}})
#     response = _recv_json(socket)

#     if not response:
#         print(f"Error: No response received for {area_href}\n")
#         return None

#     print(f"Response for {area_href}:\n{json.dumps(response, indent=4)}\n")

#     body = response.get("Body", {})

#     if "Area" in body:
#         area = body["Area"]
#         is_leaf = area.get("IsLeaf", False)
#         print(f"Checked Area: {area['Name']} (Leaf: {is_leaf})\n")
#         return is_leaf

#     print(f"No 'Area' key found in response for {area_href}\n")
#     return None

# def main():
#     print("Look for certs")
#     if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
#         print("Error: You need to run lap_sample.py first to generate the keys needed for the API connection")
#         sys.exit()
#     print("Success")

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

#     print("Success: Authenticated connection established")

#     # Check leaf status for the given URLs and print full responses
#     print("Checking IsLeaf status for specified areas...\n")
#     leaf_status = {}
#     for url in URLS_TO_CHECK:
#         leaf_status[url] = check_leaf_status(ssock, url)

#     ssock.close()
#     print("\nCheck complete.\n")
#     print("Final IsLeaf Status for all areas:")
#     print(json.dumps(leaf_status, indent=4))

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
#     else:
#         return json.loads(recv_msg.decode("ASCII"))

# def get_child_areas(socket, area_href):
#     """
#     Recursively fetches all child areas under the given area_href 
#     and returns only the areas where IsLeaf = True.
#     """
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
#     response = _recv_json(socket)

#     if not response:
#         print(f"Error: No response received for {area_href}\n")
#         return []

#     print(f"Response for {area_href}:\n{json.dumps(response, indent=4)}\n")

#     leaf_areas = []
#     body = response.get("Body", {})

#     if "AreaSummaries" in body:
#         for area in body["AreaSummaries"]:
#             area_name = area.get("Name", "Unknown")
#             area_href = area.get("href", "")

#             if area.get("IsLeaf", False):
#                 print(f"Found Leaf Area: {area_name} ({area_href})\n")
#                 leaf_areas.append(area)
#             else:
#                 print(f"Exploring non-leaf area: {area_name} ({area_href})\n")
#                 leaf_areas.extend(get_child_areas(socket, area_href))

#     return leaf_areas

# def get_associated_zone(socket, area_href):
#     """
#     Fetches associated zone information for a given area.
#     """
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
#     response = _recv_json(socket)

#     if not response:
#         print(f"Error: No response received for {area_href}/associatedzone\n")
#         return None

#     print(f"Response for {area_href}/associatedzone:\n{json.dumps(response, indent=4)}\n")
#     return response

# def main():
#     print("Look for certs")
#     if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
#         print("Error: You need to run lap_sample.py first to generate the keys needed for the API connection")
#         sys.exit()
#     print("Success")

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

#     print("Success: Authenticated connection established")

#     # List of predefined URLs to query
#     urls_to_query = [
#         "/area/rootarea",
#         "/area/3/childarea/summary",
#         "/area/114/childarea/summary",
#         "/area/127/childarea/summary",
#         "/area/983/associatedzone",
#         "/area/1009/associatedzone"
#     ]

#     all_leaf_areas = []

#     for url in urls_to_query:
#         if "childarea/summary" in url:
#             all_leaf_areas.extend(get_child_areas(ssock, url.replace("/childarea/summary", "")))
#         elif "associatedzone" in url:
#             get_associated_zone(ssock, url.replace("/associatedzone", ""))

#     ssock.close()

#     # Print final result
#     print("\nAll Leaf Areas Found:")
#     print(json.dumps(all_leaf_areas, indent=4))

# if __name__ == "__main__":
#     main()
