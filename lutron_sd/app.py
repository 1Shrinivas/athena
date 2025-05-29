# # # # import os
# # # # import json
# # # # import socket
# # # # import ssl
# # # # from flask import Flask, jsonify, render_template

# # # # from definitions import *  # Ensure this file is available

# # # # app = Flask(__name__)

# # # # def _send_json(sock, json_msg):
# # # #     """Sends a JSON message through the socket."""
# # # #     try:
# # # #         send_msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
# # # #         sock.sendall(send_msg)
# # # #     except Exception as e:
# # # #         return {"error": f"Error sending JSON: {str(e)}"}

# # # # def _recv_json(sock):
# # # #     """Receives a JSON response from the socket."""
# # # #     try:
# # # #         recv_msg = sock.recv(5000)
# # # #         if not recv_msg:
# # # #             return None
# # # #         return json.loads(recv_msg.decode("ASCII"))
# # # #     except json.JSONDecodeError:
# # # #         return {"error": "Invalid JSON response"}
# # # #     except Exception as e:
# # # #         return {"error": f"Error receiving JSON: {str(e)}"}

# # # # def get_all_areas(sock):
# # # #     """Fetches all areas from the root."""
# # # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
# # # #     response = _recv_json(sock)

# # # #     if not response or "error" in response:
# # # #         return {"error": "No response received from /area/rootarea"}

# # # #     areas = []
# # # #     if "Body" in response and "Area" in response["Body"]:
# # # #         root_area = response["Body"]["Area"]
# # # #         areas.append(root_area.get("href", ""))

# # # #     return areas

# # # # def get_child_areas(sock, area_href):
# # # #     """Fetches all child areas recursively where IsLeaf = True."""
# # # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
# # # #     response = _recv_json(sock)

# # # #     if not response or "error" in response:
# # # #         return {"error": f"No response received for {area_href}/childarea/summary"}

# # # #     leaf_areas = []
# # # #     if "Body" in response and "AreaSummaries" in response["Body"]:
# # # #         for area in response["Body"]["AreaSummaries"]:
# # # #             area_href = area.get("href", "")
# # # #             if area.get("IsLeaf", False):
# # # #                 leaf_areas.append(area_href)
# # # #             else:
# # # #                 leaf_areas.extend(get_child_areas(sock, area_href))

# # # #     return leaf_areas

# # # # def get_associated_zones(sock, area_href):
# # # #     """Fetches associated zones for a given area."""
# # # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
# # # #     response = _recv_json(sock)

# # # #     if not response or "error" in response:
# # # #         return {"error": f"No response received for {area_href}/associatedzone"}

# # # #     zones = []
# # # #     if "Body" in response and "Zones" in response["Body"]:
# # # #         for zone in response["Body"]["Zones"]:
# # # #             zones.append({
# # # #                 "Zone ID": zone.get("href", ""),
# # # #                 "Name": zone.get("Name", "Unknown"),
# # # #                 "ControlType": zone.get("ControlType", "Unknown"),
# # # #                 "IsLight": zone.get("Category", {}).get("IsLight", False),
# # # #                 "Associated Area": zone.get("AssociatedArea", {}).get("href", "")
# # # #             })
# # # #     return zones

# # # # def establish_connection():
# # # #     """Establishes a secure connection to the Lutron Processor."""
# # # #     if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
# # # #         return None, "Error: Missing certificates. Run lap_sample.py first."

# # # #     try:
# # # #         leap_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# # # #         leap_context.verify_mode = ssl.CERT_REQUIRED
# # # #         leap_context.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
# # # #         leap_context.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
# # # #         leap_context.check_hostname = False
# # # #         sock = socket.create_connection((LUTRON_PROC_ADDRESS, 8081))
# # # #         ssock = leap_context.wrap_socket(sock, server_hostname=LUTRON_PROC_HOSTNAME)
# # # #         sock.close()
# # # #         return ssock, None
# # # #     except Exception as e:
# # # #         return None, str(e)

# # # # @app.route('/')
# # # # def index():
# # # #     return render_template('index.html')

# # # # @app.route('/fetch_data', methods=['GET'])
# # # # def fetch_data():
# # # #     """Fetches areas, leaf areas, and associated zones dynamically."""
# # # #     ssock, error = establish_connection()
# # # #     if error:
# # # #         return jsonify({"success": False, "error": error}), 500  # Return 500 if connection fails

# # # #     try:
# # # #         discovered_areas = get_all_areas(ssock)

# # # #         all_leaf_areas = []
# # # #         for area in discovered_areas:
# # # #             all_leaf_areas.extend(get_child_areas(ssock, area))

# # # #         all_associated_zones = []
# # # #         for area in discovered_areas:
# # # #             all_associated_zones.extend(get_associated_zones(ssock, area))

# # # #         ssock.close()

# # # #         return jsonify({
# # # #             "success": True,
# # # #             "all_areas": discovered_areas,
# # # #             "leaf_areas": all_leaf_areas,
# # # #             "associated_zones": all_associated_zones
# # # #         })

# # # #     except Exception as e:
# # # #         return jsonify({"success": False, "error": str(e)}), 500


# # # # @app.route('/discover_areas', methods=['GET'])
# # # # def discover_areas():
# # # #     """Fetches and returns all discovered areas with leaf areas and associated zones."""
# # # #     ssock, error = establish_connection()
# # # #     if error:
# # # #         return jsonify({"success": False, "error": error}), 500

# # # #     try:
# # # #         discovered_areas = get_all_areas(ssock)

# # # #         all_leaf_areas = []
# # # #         all_associated_zones = []
# # # #         for area in discovered_areas:
# # # #             all_leaf_areas.extend(get_child_areas(ssock, area))
# # # #             all_associated_zones.extend(get_associated_zones(ssock, area))

# # # #         ssock.close()
        
# # # #         return jsonify({
# # # #             "success": True,
# # # #             "all_areas": discovered_areas,
# # # #             "leaf_areas": all_leaf_areas,
# # # #             "associated_zones": all_associated_zones
# # # #         })

# # # #     except Exception as e:
# # # #         return jsonify({"success": False, "error": str(e)}), 500
    
    

# # # # if __name__ == '__main__':
# # # #     app.run(debug=True, host="0.0.0.0", port=5000)



# # # # import os
# # # # import json
# # # # import socket
# # # # import ssl
# # # # from flask import Flask, jsonify, render_template

# # # # from definitions import *  # Ensure this file is available

# # # # app = Flask(__name__)

# # # # def _send_json(sock, json_msg):
# # # #     """Sends a JSON message through the socket."""
# # # #     try:
# # # #         send_msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
# # # #         sock.sendall(send_msg)
# # # #     except Exception as e:
# # # #         return {"error": f"Error sending JSON: {str(e)}"}

# # # # def _recv_json(sock):
# # # #     """Receives a JSON response from the socket."""
# # # #     try:
# # # #         recv_msg = sock.recv(5000)
# # # #         if not recv_msg:
# # # #             return None
# # # #         return json.loads(recv_msg.decode("ASCII"))
# # # #     except json.JSONDecodeError:
# # # #         return {"error": "Invalid JSON response"}
# # # #     except Exception as e:
# # # #         return {"error": f"Error receiving JSON: {str(e)}"}

# # # # def get_all_areas(sock):
# # # #     """Fetches all areas from the root."""
# # # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
# # # #     response = _recv_json(sock)

# # # #     if not response or "error" in response:
# # # #         return {"error": "No response received from /area/rootarea"}

# # # #     areas = []
# # # #     if "Body" in response and "Area" in response["Body"]:
# # # #         root_area = response["Body"]["Area"]
# # # #         areas.append(root_area.get("href", ""))

# # # #     return areas

# # # # def get_child_areas(sock, area_href):
# # # #     """Fetches all child areas recursively where IsLeaf = True."""
# # # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
# # # #     response = _recv_json(sock)

# # # #     if not response or "error" in response:
# # # #         return {"error": f"No response received for {area_href}/childarea/summary"}

# # # #     leaf_areas = []
# # # #     if "Body" in response and "AreaSummaries" in response["Body"]:
# # # #         for area in response["Body"]["AreaSummaries"]:
# # # #             area_href = area.get("href", "")
# # # #             if area.get("IsLeaf", False):
# # # #                 leaf_areas.append(area_href)
# # # #             else:
# # # #                 leaf_areas.extend(get_child_areas(sock, area_href))

# # # #     return leaf_areas

# # # # def get_associated_zones(sock, area_href):
# # # #     """Fetches associated zones for a given area."""
# # # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
# # # #     response = _recv_json(sock)

# # # #     if not response or "error" in response:
# # # #         return {"error": f"No response received for {area_href}/associatedzone"}

# # # #     zones = []
# # # #     if "Body" in response and "Zones" in response["Body"]:
# # # #         for zone in response["Body"]["Zones"]:
# # # #             zones.append({
# # # #                 "Zone ID": zone.get("href", ""),
# # # #                 "Name": zone.get("Name", "Unknown"),
# # # #                 "ControlType": zone.get("ControlType", "Unknown"),
# # # #                 "IsLight": zone.get("Category", {}).get("IsLight", False),
# # # #                 "Associated Area": zone.get("AssociatedArea", {}).get("href", "")
# # # #             })
# # # #     return zones

# # # # def establish_connection():
# # # #     """Establishes a secure connection to the Lutron Processor."""
# # # #     if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
# # # #         return None, "Error: Missing certificates. Run lap_sample.py first."

# # # #     try:
# # # #         leap_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# # # #         leap_context.verify_mode = ssl.CERT_REQUIRED
# # # #         leap_context.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
# # # #         leap_context.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
# # # #         leap_context.check_hostname = False
# # # #         sock = socket.create_connection((LUTRON_PROC_ADDRESS, 8081))
# # # #         ssock = leap_context.wrap_socket(sock, server_hostname=LUTRON_PROC_HOSTNAME)
# # # #         sock.close()
# # # #         return ssock, None
# # # #     except Exception as e:
# # # #         return None, str(e)

# # # # @app.route('/')
# # # # def index():
# # # #     return render_template('index.html')

# # # # @app.route('/discover_areas', methods=['GET'])
# # # # def discover_areas():
# # # #     """Fetches and returns all discovered areas with leaf areas and associated zones."""
# # # #     ssock, error = establish_connection()
# # # #     if error:
# # # #         return jsonify({"success": False, "error": error}), 500

# # # #     try:
# # # #         discovered_areas = get_all_areas(ssock)

# # # #         all_leaf_areas = []
# # # #         all_associated_zones = []
# # # #         for area in discovered_areas:
# # # #             all_leaf_areas.extend(get_child_areas(ssock, area))
# # # #             all_associated_zones.extend(get_associated_zones(ssock, area))

# # # #         ssock.close()
        
# # # #         return jsonify({
# # # #             "success": True,
# # # #             "all_areas": discovered_areas,
# # # #             "leaf_areas": all_leaf_areas,
# # # #             "associated_zones": all_associated_zones
# # # #         })

# # # #     except Exception as e:
# # # #         return jsonify({"success": False, "error": str(e)}), 500
    
# # # # if __name__ == '__main__':
# # # #     app.run(debug=True, host="0.0.0.0", port=5000)



# # # # from flask import Flask, jsonify, render_template, request
# # # # import os
# # # # import sys
# # # # import json
# # # # import socket
# # # # import ssl

# # # # from definitions import *  # Contains LEAP_PRIVATE_KEY_FILE, etc.

# # # # app = Flask(__name__)

# # # # @app.route('/')
# # # # def home():
# # # #     return render_template('index.html')

# # # # @app.route('/read_request', methods=['GET'])
# # # # def read_request():
# # # #     try:
# # # #         ssock = establish_lutron_connection()
# # # #         root_area = get_root_area(ssock)
# # # #         if not root_area:
# # # #             return jsonify({"error": "Failed to fetch root area"}), 500

# # # #         full_tree = build_area_tree(ssock, root_area)
# # # #         ssock.close()
# # # #         return jsonify(full_tree)
# # # #     except Exception as e:
# # # #         return jsonify({"error": str(e)}), 500

# # # # # --- Helper Functions ---

# # # # def establish_lutron_connection():
# # # #     if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
# # # #         raise FileNotFoundError("Missing certificates. Run lap_sample.py first.")

# # # #     leap_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# # # #     leap_context.verify_mode = ssl.CERT_REQUIRED
# # # #     leap_context.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
# # # #     leap_context.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
# # # #     leap_context.check_hostname = False

# # # #     sock = socket.create_connection((LUTRON_PROC_ADDRESS, 8081))
# # # #     ssock = leap_context.wrap_socket(sock, server_hostname=LUTRON_PROC_HOSTNAME)
# # # #     sock.close()
# # # #     return ssock

# # # # def _send_json(sock, json_msg):
# # # #     send_msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
# # # #     sock.sendall(send_msg)

# # # # def _recv_json(sock):
# # # #     recv_msg = sock.recv(5000)
# # # #     if len(recv_msg) == 0:
# # # #         return None
# # # #     return json.loads(recv_msg.decode("ASCII"))

# # # # def get_root_area(sock):
# # # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
# # # #     response = _recv_json(sock)
# # # #     return response.get("Body", {}).get("Area")

# # # # def get_child_areas(sock, area_href):
# # # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
# # # #     response = _recv_json(sock)
# # # #     return response.get("Body", {}).get("AreaSummaries", [])

# # # # def get_zones(sock, area_href):
# # # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
# # # #     response = _recv_json(sock)
# # # #     return response.get("Body", {}).get("Zones", [])

# # # # def get_zone_status(sock, zone_href):
# # # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{zone_href}/status"}})
# # # #     response = _recv_json(sock)
# # # #     return response.get("Body", {}).get("ZoneStatus", {})

# # # # def get_area_status(sock, area_href):
# # # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/status"}})
# # # #     response = _recv_json(sock)
# # # #     return response.get("Body", {}).get("AreaStatus", {})

# # # # def get_scenes(sock, area_href):
# # # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/areascene"}})
# # # #     response = _recv_json(sock)
# # # #     return response.get("Body", {}).get("AreaScenes", [])

# # # # def get_control_stations(sock, area_href):
# # # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedcontrolstation"}})
# # # #     response = _recv_json(sock)
# # # #     return response.get("Body", {}).get("ControlStations", [])

# # # # def get_buttons(sock, device_href):
# # # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{device_href}/buttongroup/expanded"}})
# # # #     response = _recv_json(sock)
# # # #     button_groups = response.get("Body", {}).get("ButtonGroupsExpanded", [])
# # # #     buttons = []
# # # #     for group in button_groups:
# # # #         buttons.extend(group.get("Buttons", []))
# # # #     return buttons

# # # # def build_area_tree(sock, area, parent_href=None):
# # # #     node = {
# # # #         "href": area["href"],
# # # #         "name": area.get("Name", ""),
# # # #         "is_leaf": area.get("IsLeaf", False),
# # # #         "parent": parent_href,
# # # #         "children": [],
# # # #         "zones": [],
# # # #         "scenes": [],
# # # #         "control_stations": [],
# # # #         "area_status": {}
# # # #     }

# # # #     node["area_status"] = get_area_status(sock, area["href"])

# # # #     if area.get("IsLeaf", False):
# # # #         zones = get_zones(sock, area["href"])
# # # #         for z in zones:
# # # #             zone_status = get_zone_status(sock, z["href"])
# # # #             node["zones"].append({
# # # #                 "Zone ID": z.get("href", ""),
# # # #                 "Name": z.get("Name", ""),
# # # #                 "ControlType": z.get("ControlType", ""),
# # # #                 "IsLight": z.get("Category", {}).get("IsLight", False),
# # # #                 "Associated Area": z.get("AssociatedArea", {}).get("href", ""),
# # # #                 "Status": zone_status
# # # #             })

# # # #         node["scenes"] = [{
# # # #             "Scene ID": s.get("href", ""),
# # # #             "Name": s.get("Name", ""),
# # # #             "Associated Area": s.get("Parent", {}).get("href", "")
# # # #         } for s in get_scenes(sock, area["href"])]

# # # #         control_stations = get_control_stations(sock, area["href"])
# # # #         for cs in control_stations:
# # # #             buttons = []
# # # #             for dev in cs.get("AssociatedGangedDevices", []):
# # # #                 dev_href = dev.get("Device", {}).get("href", "")
# # # #                 if dev_href:
# # # #                     buttons.extend(get_buttons(sock, dev_href))
# # # #             node["control_stations"].append({
# # # #                 "ControlStation ID": cs.get("href", ""),
# # # #                 "Name": cs.get("Name", ""),
# # # #                 "DeviceType": cs.get("AssociatedGangedDevices", [{}])[0].get("Device", {}).get("DeviceType", ""),
# # # #                 "Buttons": buttons
# # # #             })
# # # #     else:
# # # #         for child in get_child_areas(sock, area["href"]):
# # # #             child_node = build_area_tree(sock, child, parent_href=area["href"])
# # # #             node["children"].append(child_node)

# # # #     return node


# # # # if __name__ == '__main__':
# # # #     app.run(debug=True, host="0.0.0.0", port=5000)




# # # import os
# # # import sys
# # # import json
# # # import socket
# # # import ssl
# # # import asyncio
# # # import threading
# # # from flask import Flask, jsonify, render_template

# # # from definitions import *  # Contains LEAP_PRIVATE_KEY_FILE, etc.

# # # app = Flask(__name__)

# # # # --- Synchronous Lutron connection for read requests ---

# # # @app.route('/')
# # # def home():
# # #     return render_template('index.html')

# # # @app.route('/read_request', methods=['GET'])
# # # def read_request():
# # #     try:
# # #         ssock = establish_lutron_connection()
# # #         root_area = get_root_area(ssock)
# # #         if not root_area:
# # #             return jsonify({"error": "Failed to fetch root area"}), 500

# # #         full_tree = build_area_tree(ssock, root_area)
# # #         ssock.close()
# # #         return jsonify(full_tree)
# # #     except Exception as e:
# # #         return jsonify({"error": str(e)}), 500

# # # def establish_lutron_connection():
# # #     if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
# # #         raise FileNotFoundError("Missing certificates. Run lap_sample.py first.")

# # #     leap_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# # #     leap_context.verify_mode = ssl.CERT_REQUIRED
# # #     leap_context.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
# # #     leap_context.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
# # #     leap_context.check_hostname = False

# # #     sock = socket.create_connection((LUTRON_PROC_ADDRESS, 8081))
# # #     ssock = leap_context.wrap_socket(sock, server_hostname=LUTRON_PROC_HOSTNAME)
# # #     sock.close()
# # #     return ssock

# # # def _send_json(sock, json_msg):
# # #     send_msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
# # #     sock.sendall(send_msg)

# # # def _recv_json(sock):
# # #     recv_msg = sock.recv(5000)
# # #     if len(recv_msg) == 0:
# # #         return None
# # #     # The device may send multiple JSON messages separated by CRLF
# # #     messages = recv_msg.decode("ASCII").split("\r\n")
# # #     results = []
# # #     for msg in messages:
# # #         if msg.strip():
# # #             try:
# # #                 results.append(json.loads(msg))
# # #             except json.JSONDecodeError:
# # #                 pass
# # #     if len(results) == 1:
# # #         return results[0]
# # #     return results

# # # def get_root_area(sock):
# # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
# # #     response = _recv_json(sock)
# # #     if not response:
# # #         return None
# # #     return response.get("Body", {}).get("Area")

# # # def get_child_areas(sock, area_href):
# # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
# # #     response = _recv_json(sock)
# # #     if not response:
# # #         return []
# # #     return response.get("Body", {}).get("AreaSummaries", [])

# # # def get_zones(sock, area_href):
# # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
# # #     response = _recv_json(sock)
# # #     if not response:
# # #         return []
# # #     return response.get("Body", {}).get("Zones", [])

# # # def get_zone_status(sock, zone_href):
# # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{zone_href}/status"}})
# # #     response = _recv_json(sock)
# # #     if not response:
# # #         return {}
# # #     return response.get("Body", {}).get("ZoneStatus", {})

# # # def get_area_status(sock, area_href):
# # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/status"}})
# # #     response = _recv_json(sock)
# # #     if not response:
# # #         return {}
# # #     return response.get("Body", {}).get("AreaStatus", {})

# # # def get_scenes(sock, area_href):
# # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/areascene"}})
# # #     response = _recv_json(sock)
# # #     if not response:
# # #         return []
# # #     return response.get("Body", {}).get("AreaScenes", [])

# # # def get_control_stations(sock, area_href):
# # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedcontrolstation"}})
# # #     response = _recv_json(sock)
# # #     if not response:
# # #         return []
# # #     return response.get("Body", {}).get("ControlStations", [])

# # # def get_buttons(sock, device_href):
# # #     _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{device_href}/buttongroup/expanded"}})
# # #     response = _recv_json(sock)
# # #     if not response:
# # #         return []
# # #     button_groups = response.get("Body", {}).get("ButtonGroupsExpanded", [])
# # #     buttons = []
# # #     for group in button_groups:
# # #         buttons.extend(group.get("Buttons", []))
# # #     return buttons

# # # def build_area_tree(sock, area, parent_href=None):
# # #     node = {
# # #         "href": area["href"],
# # #         "name": area.get("Name", ""),
# # #         "is_leaf": area.get("IsLeaf", False),
# # #         "parent": parent_href,
# # #         "children": [],
# # #         "zones": [],
# # #         "scenes": [],
# # #         "control_stations": [],
# # #         "area_status": {}
# # #     }

# # #     node["area_status"] = get_area_status(sock, area["href"])

# # #     if node["is_leaf"]:
# # #         zones = get_zones(sock, area["href"])
# # #         for z in zones:
# # #             zone_status = get_zone_status(sock, z["href"])
# # #             node["zones"].append({
# # #                 "Zone ID": z.get("href", ""),
# # #                 "Name": z.get("Name", ""),
# # #                 "ControlType": z.get("ControlType", ""),
# # #                 "IsLight": z.get("Category", {}).get("IsLight", False),
# # #                 "Associated Area": z.get("AssociatedArea", {}).get("href", ""),
# # #                 "Status": zone_status
# # #             })

# # #         node["scenes"] = [ {
# # #             "Scene ID": s.get("href", ""),
# # #             "Name": s.get("Name", ""),
# # #             "Associated Area": s.get("Parent", {}).get("href", "")
# # #         } for s in get_scenes(sock, area["href"])]

# # #         control_stations = get_control_stations(sock, area["href"])
# # #         for cs in control_stations:
# # #             buttons = []
# # #             for dev in cs.get("AssociatedGangedDevices", []):
# # #                 dev_href = dev.get("Device", {}).get("href", "")
# # #                 if dev_href:
# # #                     buttons.extend(get_buttons(sock, dev_href))
# # #             node["control_stations"].append({
# # #                 "ControlStation ID": cs.get("href", ""),
# # #                 "Name": cs.get("Name", ""),
# # #                 "DeviceType": cs.get("AssociatedGangedDevices", [{}])[0].get("Device", {}).get("DeviceType", ""),
# # #                 "Buttons": buttons
# # #             })
# # #     else:
# # #         for child in get_child_areas(sock, area["href"]):
# # #             node["children"].append(build_area_tree(sock, child, parent_href=area["href"]))

# # #     return node

# # # # --- Async subscription logic for realtime updates ---

# # # CRLF = "\r\n"

# # # async def send_json(writer, json_msg):
# # #     msg = (json.dumps(json_msg) + CRLF).encode("ASCII")
# # #     writer.write(msg)
# # #     await writer.drain()

# # # async def recv_json(reader):
# # #     buffer = await reader.read(5000)
# # #     if not buffer:
# # #         return None
# # #     messages = buffer.decode("ASCII").split(CRLF)
# # #     results = []
# # #     for msg in messages:
# # #         if msg.strip():
# # #             try:
# # #                 results.append(json.loads(msg))
# # #             except json.JSONDecodeError:
# # #                 pass
# # #     return results if results else None

# # # async def get_root_area_async(reader, writer):
# # #     await send_json(writer, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
# # #     responses = await recv_json(reader)
# # #     if not responses:
# # #         return None
# # #     for response in responses:
# # #         if "Body" in response and "Area" in response["Body"]:
# # #             return response["Body"]["Area"]
# # #     return None

# # # async def get_child_areas_async(reader, writer, area_href):
# # #     await send_json(writer, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
# # #     responses = await recv_json(reader)
# # #     for response in responses or []:
# # #         if "Body" in response and "AreaSummaries" in response["Body"]:
# # #             return response["Body"]["AreaSummaries"]
# # #     return []

# # # async def get_zones_async(reader, writer, area_href):
# # #     await send_json(writer, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
# # #     responses = await recv_json(reader)
# # #     for response in responses or []:
# # #         if "Body" in response and "Zones" in response["Body"]:
# # #             return response["Body"]["Zones"]
# # #     return []

# # # async def build_area_tree_async(reader, writer, area, parent_href=None):
# # #     node = {
# # #         "href": area["href"],
# # #         "name": area.get("Name", ""),
# # #         "is_leaf": area.get("IsLeaf", False),
# # #         "parent": parent_href,
# # #         "children": [],
# # #         "zones": [],
# # #         "scenes": [],
# # #         "control_stations": [],
# # #         "area_status": {}
# # #     }

# # #     # For brevity, you can add async versions of status and scenes requests similarly
# # #     # Here, just build the tree structure (zones, children) to demo

# # #     if node["is_leaf"]:
# # #         zones = await get_zones_async(reader, writer, area["href"])
# # #         node["zones"] = zones
# # #         # You can add more async fetches for zone status, scenes, control stations here
# # #     else:
# # #         children = await get_child_areas_async(reader, writer, area["href"])
# # #         for child in children:
# # #             node["children"].append(await build_area_tree_async(reader, writer, child, parent_href=area["href"]))

# # #     return node

# # # async def subscribe(reader, writer, path):
# # #     await send_json(writer, {"CommuniqueType": "SubscribeRequest", "Header": {"Url": path}})
# # #     response = await recv_json(reader)
# # #     return response

# # # async def listen_for_updates(reader):
# # #     print("Listening for updates...")
# # #     while True:
# # #         try:
# # #             buffer = await reader.read(4096)
# # #             if not buffer:
# # #                 print("Connection closed.")
# # #                 break
# # #             messages = buffer.decode("ASCII").split(CRLF)
# # #             for msg in messages:
# # #                 if msg.strip():
# # #                     try:
# # #                         data = json.loads(msg)
# # #                         print("Update received:", data)
# # #                         # Here you can update a shared cache or state variable if needed
# # #                     except Exception:
# # #                         pass
# # #         except asyncio.CancelledError:
# # #             print("Listener task cancelled.")
# # #             break
# # #         except Exception as e:
# # #             print("Error in listen_for_updates:", e)
# # #             break

# # # async def main_async():
# # #     if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
# # #         print("Certificates missing. Run lap_sample.py first.")
# # #         return

# # #     leap_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=LAP_LUTRON_ROOT_FILE)
# # #     leap_context.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
# # #     leap_context.check_hostname = False

# # #     reader, writer = await asyncio.open_connection(LUTRON_PROC_ADDRESS, 8081, ssl=leap_context)

# # #     root_area = await get_root_area_async(reader, writer)
# # #     if root_area is None:
# # #         print("Failed to get root area")
# # #         writer.close()
# # #         await writer.wait_closed()
# # #         return

# # #     print("Subscribing to root area updates...")
# # #     await subscribe(reader, writer, root_area["href"])

# # #     # Start listening for updates indefinitely
# # #     await listen_for_updates(reader)

# # # # --- Run async subscription in background thread ---

# # # def run_async_loop():
# # #     asyncio.run(main_async())

# # # if __name__ == '__main__':
# # #     # Start async subscription listener in a background thread
# # #     thread = threading.Thread(target=run_async_loop, daemon=True)
# # #     thread.start()

# # #     # Start Flask app
# # #     app.run(host="0.0.0.0", port=5000)


# # import json
# # import time
# # from flask import Flask, render_template, jsonify, Response, stream_with_context
# # import threading
# # import read_request
# # from definitions import *  # your certificates and Lutron constants

# # app = Flask(__name__)

# # latest_read_data = {}

# # def blocking_read_request():
# #     """
# #     This function will create a socket connection, read data synchronously,
# #     and build the area tree using read_request.py functions.
# #     """
# #     import socket
# #     import ssl

# #     try:
# #         leap_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# #         leap_context.verify_mode = ssl.CERT_REQUIRED
# #         leap_context.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
# #         leap_context.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
# #         leap_context.check_hostname = False

# #         sock = socket.create_connection((LUTRON_PROC_ADDRESS, 8081))
# #         ssock = leap_context.wrap_socket(sock, server_hostname=LUTRON_PROC_HOSTNAME)
# #     except Exception as e:
# #         return {"error": str(e)}

# #     root_area = read_request.get_root_area(ssock)
# #     if not root_area:
# #         ssock.close()
# #         return {"error": "Failed to get root area"}

# #     full_tree = read_request.build_area_tree(ssock, root_area)
# #     ssock.close()
# #     return full_tree


# # @app.route('/')
# # def index():
# #     return render_template('index.html')


# # @app.route('/read_request')
# # def read_request_route():
# #     global latest_read_data

# #     # Run the blocking code in a separate thread to avoid blocking Flask
# #     result_container = {}

# #     def target():
# #         result_container["data"] = blocking_read_request()

# #     thread = threading.Thread(target=target)
# #     thread.start()
# #     thread.join()  # Wait for thread to finish

# #     latest_read_data = result_container.get("data", {})
# #     return jsonify(latest_read_data)


# # @app.route('/subscribe_request')
# # def subscribe_request_route():
# #     def event_stream():
# #         while True:
# #             yield f"data: {json.dumps(latest_read_data)}\n\n"
# #             time.sleep(1)

# #     return Response(stream_with_context(event_stream()), mimetype='text/event-stream')


# # if __name__ == '__main__':
# #     app.run(debug=True, port=5000)




# # from flask import Flask, render_template, jsonify
# # import os
# # import json
# # import socket
# # import ssl
# # from definitions import *

# # app = Flask(__name__)

# # def _send_json(socket, json_msg):
# #     """Sends a JSON message to the Lutron system."""
# #     send_msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
# #     socket.sendall(send_msg)

# # def _recv_json(socket):
# #     """Receives and decodes a JSON message from the Lutron system."""
# #     recv_msg = socket.recv(5000)
# #     if len(recv_msg) == 0:
# #         return None
# #     else:
# #         return json.loads(recv_msg.decode("ASCII"))

# # def get_child_areas(socket, area_href, child_summaries, area_summaries):
# #     """Fetches child areas of a given area and returns leaf areas."""
# #     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
# #     response = _recv_json(socket)
# #     if not response:
# #         return []
    
# #     body = response.get("Body", {})
# #     leaf_areas = []
    
# #     if "AreaSummaries" in body:
# #         for area in body["AreaSummaries"]:
# #             area_summaries.append(area)
# #             if area.get("IsLeaf", False):
# #                 leaf_areas.append(area)
# #             else:
# #                 child_summaries.append(area)
# #                 leaf_areas.extend(get_child_areas(socket, area.get("href", ""), child_summaries, area_summaries))
    
# #     return leaf_areas

# # def get_associated_zone(socket, area_href, zones_list):
# #     """Fetches zones associated with a specific area."""
# #     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
# #     response = _recv_json(socket)
# #     if not response:
# #         return None
    
# #     body = response.get("Body", {})
    
# #     if "Zones" in body:
# #         for zone in body["Zones"]:
# #             zones_list.append(zone)

# # def get_root_areas(socket):
# #     """Fetches root areas from the system."""
# #     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
# #     response = _recv_json(socket)
    
# #     if not response:
# #         return []
    
# #     return response.get("Body", {}).get("AreaSummaries", [])

# # def discover_data():
# #     """Establishes connection to the Lutron system and retrieves areas/zones."""
# #     if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
# #         return {"error": "Missing required certificates."}
    
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
# #         return {"error": str(e)}
    
# #     all_leaf_areas = []
# #     all_zones = []
# #     child_summaries = []
# #     area_summaries = []
    
# #     # Fetch root areas
# #     root_areas = get_root_areas(ssock)

# #     # URLs to query for more data
# #     urls_to_query = [
# #         "/area/3/childarea/summary",
# #         "/area/114/childarea/summary",
# #         "/area/127/childarea/summary",
# #         "/area/983/associatedzone",
# #         "/area/1009/associatedzone"
# #     ]
    
# #     for url in urls_to_query:
# #         if "childarea/summary" in url:
# #             all_leaf_areas.extend(get_child_areas(ssock, url.replace("/childarea/summary", ""), child_summaries, area_summaries))
# #         elif "associatedzone" in url:
# #             get_associated_zone(ssock, url.replace("/associatedzone", ""), all_zones)

# #     ssock.close()
    
# #     return {
# #         "RootAreas": root_areas,
# #         "LeafAreas": all_leaf_areas,
# #         "Zones": all_zones,
# #         "ChildSummaries": child_summaries,
# #         "AreaSummaries": area_summaries
# #     }

# # @app.route('/')
# # def index():
# #     return render_template('index.html')

# # @app.route('/discover', methods=['GET'])
# # def discover():
# #     data = discover_data()
# #     return jsonify(data)

# # @app.route('/root-areas', methods=['GET'])
# # def root_areas():
# #     data = discover_data()
# #     return jsonify(data.get("RootAreas", []))

# # @app.route('/leaf-areas', methods=['GET'])
# # def leaf_areas():
# #     data = discover_data()
# #     return jsonify(data.get("LeafAreas", []))

# # @app.route('/child-areas', methods=['GET'])
# # def child_areas():
# #     data = discover_data()
# #     return jsonify(data.get("ChildSummaries", []))

# # @app.route('/zones', methods=['GET'])
# # def zones():
# #     data = discover_data()
# #     return jsonify(data.get("Zones", []))

# # if __name__ == '__main__':
# #     app.run(debug=True)


# from flask import Flask, render_template, jsonify
# import os
# import json
# import socket
# import ssl
# import subprocess
# from definitions import *


# app = Flask(__name__)

# def _send_json(socket, json_msg):
#     """Sends a JSON message to the Lutron system."""
#     send_msg = (json.dumps(json_msg) + "\r\n").encode("ASCII")
#     socket.sendall(send_msg)

# def _recv_json(socket):
#     """Receives and decodes a JSON message from the Lutron system."""
#     recv_msg = socket.recv(5000)
#     if len(recv_msg) == 0:
#         return None
#     else:
#         return json.loads(recv_msg.decode("ASCII"))

# def get_child_areas(socket, area_href, child_summaries, area_summaries):
#     """Fetches child areas of a given area and returns leaf areas."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
#     response = _recv_json(socket)
#     if not response:
#         return []
    
#     body = response.get("Body", {})
#     leaf_areas = []
    
#     if "AreaSummaries" in body:
#         for area in body["AreaSummaries"]:
#             area_summaries.append(area)
#             if area.get("IsLeaf", False):
#                 leaf_areas.append(area)
#             else:
#                 child_summaries.append(area)
#                 leaf_areas.extend(get_child_areas(socket, area.get("href", ""), child_summaries, area_summaries))
    
#     return leaf_areas

# def get_associated_zone(socket, area_href, zones_list):
#     """Fetches zones associated with a specific area."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
#     response = _recv_json(socket)
#     if not response:
#         return None
    
#     body = response.get("Body", {})
    
#     if "Zones" in body:
#         for zone in body["Zones"]:
#             zones_list.append(zone)

# def get_root_areas(socket):
#     """Fetches root areas from the system."""
#     _send_json(socket, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
#     response = _recv_json(socket)
    
#     if not response:
#         return []
    
#     return response.get("Body", {}).get("AreaSummaries", [])

# def discover_data():
#     """Establishes connection to the Lutron system and retrieves areas/zones."""
#     if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
#         return {"error": "Missing required certificates."}
    
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
#         return {"error": str(e)}
    
#     all_leaf_areas = []
#     all_zones = []
#     child_summaries = []
#     area_summaries = []
    
#     # Fetch root areas
#     root_areas = get_root_areas(ssock)
#     print('root:',root_areas)

#     # URLs to query for more data
#     urls_to_query = [
#         "/area/3/childarea/summary",
#         "/area/114/childarea/summary",
#         "/area/127/childarea/summary",
#         "/area/983/associatedzone",
#         "/area/1009/associatedzone"
#     ]
    
#     for url in urls_to_query:
#         if "childarea/summary" in url:
#             all_leaf_areas.extend(get_child_areas(ssock, url.replace("/childarea/summary", ""), child_summaries, area_summaries))
#         elif "associatedzone" in url:
#             get_associated_zone(ssock, url.replace("/associatedzone", ""), all_zones)

#     ssock.close()
    
#     return {
#         "RootAreas": root_areas,
#         "LeafAreas": all_leaf_areas,
#         "Zones": all_zones,
#         "ChildSummaries": child_summaries,
#         "AreaSummaries": area_summaries
#     }

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/discover', methods=['GET'])
# def discover():
#     data = discover_data()
#     return jsonify(data)

# @app.route('/root-areas', methods=['GET'])
# def root_areas():
#     data = discover_data()
#     return jsonify(data.get("RootAreas", []))

# @app.route('/leaf-areas', methods=['GET'])
# def leaf_areas():
#     data = discover_data()
#     return jsonify(data.get("LeafAreas", []))

# @app.route('/child-areas', methods=['GET'])
# def child_areas():
#     data = discover_data()
#     return jsonify(data.get("ChildSummaries", []))

# @app.route('/zones', methods=['GET'])
# def zones():
#     data = discover_data()
#     return jsonify(data.get("Zones", []))

# @app.route('/scene', methods=['GET'])
# def discover_scene():
#     return jsonify({"message": "Feature coming soon!"})


# if __name__ == '__main__':
#     app.run(debug=True)



import os
import json
import socket
import ssl
import asyncio
import threading
import queue

from flask import Flask, Response, render_template, jsonify
from definitions import *

app = Flask(__name__)

event_queue = queue.Queue()

# -----------------------------
# Synchronous Communication Helpers
# -----------------------------
def push_event(data):
    event_queue.put(data)

def _send_json(sock, msg):
    send_msg = (json.dumps(msg) + "\r\n").encode("ascii")
    sock.sendall(send_msg)

def _recv_json(sock):
    recv_msg = sock.recv(5000)
    if not recv_msg:
        return None
    return json.loads(recv_msg.decode("ascii"))

def get_root_areas(sock):
    _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
    response = _recv_json(sock)
    return response.get("Body", {}).get("AreaSummaries", []) if response else []

def get_child_areas(sock, area_href, child_summaries, area_summaries):
    _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
    response = _recv_json(sock)
    if not response:
        return []

    leaf_areas = []
    for area in response.get("Body", {}).get("AreaSummaries", []):
        area_summaries.append(area)
        if area.get("IsLeaf", False):
            leaf_areas.append(area)
        else:
            child_summaries.append(area)
            leaf_areas.extend(get_child_areas(sock, area.get("href", ""), child_summaries, area_summaries))

    return leaf_areas

def get_associated_zone(sock, area_href, zones_list):
    _send_json(sock, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
    response = _recv_json(sock)
    if not response:
        return
    for zone in response.get("Body", {}).get("Zones", []):
        zones_list.append(zone)

def discover_data():
    if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
        return {"error": "Missing certificates."}

    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
        ctx.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
        ctx.check_hostname = False

        # Use plain socket here (not asyncio)
        sock = socket.create_connection((LUTRON_PROC_ADDRESS, 8081))
        ssock = ctx.wrap_socket(sock, server_hostname=LUTRON_PROC_HOSTNAME)
        sock.close()
    except Exception as e:
        return {"error": str(e)}

    root_areas = get_root_areas(ssock)
    child_summaries, area_summaries, all_leaf_areas, all_zones = [], [], [], []

    urls = [
        "/zone/status"
        "/area/status"
        "/area/3/childarea/summary",
        "/area/114/childarea/summary",
        "/area/127/childarea/summary",
        "/area/983/associatedzone",
        "/area/1009/associatedzone",
        "/area/1022/associatedzone",
        "/area/1519/associatedzone",
        "/area/1533/associatedzone",
        "/area/rootarea"
        "/area/983/status",
        "/area/1009/status",
        "/area/1022/status",
        "/area/1519/status",
        "/area/1533/status",
        
    
    ]

    for url in urls:
        if "childarea/summary" in url:
            base = url.replace("/childarea/summary", "")
            all_leaf_areas.extend(get_child_areas(ssock, base, child_summaries, area_summaries))
        elif "associatedzone" in url:
            base = url.replace("/associatedzone", "")
            get_associated_zone(ssock, base, all_zones)
        
    ssock.close()

    return {
        "RootAreas": root_areas,
        "LeafAreas": all_leaf_areas,
        "Zones": all_zones,
        "ChildSummaries": child_summaries,
        "AreaSummaries": area_summaries,
    }

# -----------------------------
# Async Background Listener
# -----------------------------

async def send_json(writer, msg):
    writer.write((json.dumps(msg) + '\r\n').encode('ascii'))
    await writer.drain()

async def recv_json(reader):
    data = await reader.readline()
    if not data:
        return []
    return [json.loads(data.decode('ascii'))]

async def subscribe(writer, url):
    await send_json(writer, {
        "CommuniqueType": "SubscribeRequest",
        "Header": {"Url": url}
    })

def check_area_occupancy(area_status_msg):
    occupancy = area_status_msg.get("AreaStatus", {}).get("OccupancyStatus", "").lower()
    if occupancy == "occupied":
        print("🏢 Area is currently OCCUPIED.")
    elif occupancy == "unoccupied":
        print("🏢 Area is currently UNOCCUPIED.")
    else:
        print(f"🏢 Area Occupancy Status: {occupancy}")

async def check_zone_status_async(msg_body):
    print("🛠️ Zone status update:", msg_body)

async def listen_for_updates(reader):
    print("\n🔔 Listening for Area/Zone updates...")
    try:
        while True:
            msgs = await recv_json(reader)
            for msg in msgs:
                url = msg.get("Header", {}).get("Url", "")
                print(f"\n🔔 Update received from: {url}")
                print(json.dumps(msg.get("Body", {}), indent=4))

                # Push data to SSE queue so clients get it in real time
                push_event({"message": f"Update from {url}"})
                push_event({"message": json.dumps(msg.get("Body", {}), indent=2)})

                if "/area/" in url and url.endswith("/status"):
                    check_area_occupancy(msg.get("Body", {}))
                elif "/zone/" in url and url.endswith("/status"):
                    await check_zone_status_async(msg.get("Body", {}))
    except asyncio.CancelledError:
        print("🛑 Listener stopped.")


async def subscription_worker():
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.verify_mode = ssl.CERT_REQUIRED
        ctx.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
        ctx.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
        ctx.check_hostname = False

        # ✅ Correct way to open SSL connection with asyncio
        reader, writer = await asyncio.open_connection(
            host=LUTRON_PROC_ADDRESS,
            port=8081,
            ssl=ctx,
            server_hostname=LUTRON_PROC_HOSTNAME
        )

        await subscribe(writer, "/zone/status")
        await subscribe(writer, "/area/status")
        await subscribe(writer, "/led/1888/status")
        await subscribe(writer, "/device/1143/status")

        await listen_for_updates(reader)

    except Exception as e:
        print("❌ Subscription error:", str(e))

def start_listener_thread():
    def thread_target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(subscription_worker())
    threading.Thread(target=thread_target, daemon=True).start()

# -----------------------------
# Flask Routes
# -----------------------------
@app.route('/stream')
def stream():
    def event_stream():
        while True:
            data = event_queue.get()
            yield f"data: {json.dumps(data)}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/discover')
def discover():
    return jsonify(discover_data())

@app.route('/root-areas')
def root_areas():
    return jsonify(discover_data().get("RootAreas", []))

@app.route('/leaf-areas')
def leaf_areas():
    return jsonify(discover_data().get("LeafAreas", []))

@app.route('/child-areas')
def child_areas():
    return jsonify(discover_data().get("ChildSummaries", []))

@app.route('/zones')
def zones():
    return jsonify(discover_data().get("Zones", []))

# -----------------------------
# Run Server
# -----------------------------

if __name__ == '__main__':
    start_listener_thread()
    app.run(debug=True)
