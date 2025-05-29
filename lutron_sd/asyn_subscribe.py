# import os
# import sys
# import json
# import asyncio
# import socket
# import ssl
# from definitions import *  # Contains certs and host config

# CRLF = "\r\n"

# async def send_json(writer, json_msg):
#     msg = (json.dumps(json_msg) + CRLF).encode("ASCII")
#     writer.write(msg)
#     await writer.drain()

# async def recv_json(reader):
#     buffer = await reader.read(5000)
#     if not buffer:
#         return None

#     messages = buffer.decode("ASCII").split(CRLF)
#     results = []
#     for msg in messages:
#         if msg.strip():
#             try:
#                 results.append(json.loads(msg))
#             except json.JSONDecodeError as e:
#                 print(f"⚠️ JSON decoding error: {e}")
#     return results if results else None


# async def get_root_area(reader, writer):
#     await send_json(writer, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
#     responses = await recv_json(reader)

#     if not responses:
#         print(" No response received for root area.")
#         return None

#     # Look for a message with "Body" containing "Area"
#     for response in responses:
#         if "Body" in response and "Area" in response["Body"]:
#             return response["Body"]["Area"]

#     print("'Area' not found in any response.")
#     return None


# async def get_child_areas(reader, writer, area_href):
#     await send_json(writer, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
#     responses = await recv_json(reader)
#     for response in responses or []:
#         if "Body" in response and "AreaSummaries" in response["Body"]:
#             return response["Body"]["AreaSummaries"]
#     return []


# async def check_zone_status_async(zone_status_msg):
#     zone_status = zone_status_msg.get("ZoneStatus", {})
    
#     if not zone_status:
#         print("⚠️ Empty zone status received.")
#         return

#     zone_name = zone_status.get("Name", "Unknown Zone")
#     level = zone_status.get("Level")
#     status_str = f"💡 Zone Update - {zone_name}: "

#     if level is not None:
#         status_str += f"Level = {level}"
#     else:
#         status_str += "No Level information available."

#     print(status_str)

# async def get_zones(reader, writer, area_href):
#     await send_json(writer, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
#     responses = await recv_json(reader)
#     for response in responses or []:
#         if "Body" in response and "Zones" in response["Body"]:
#             return response["Body"]["Zones"]
#     return []


# async def build_area_tree(reader, writer, area, parent_href=None):
#     node = {
#         "href": area["href"],
#         "name": area.get("Name", ""),
#         "is_leaf": area.get("IsLeaf", False),
#         "parent": parent_href,
#         "children": [],
#         "zones": []
#     }

#     if node["is_leaf"]:
#         zones = await get_zones(reader, writer, node["href"])
#         for z in zones:
#             node["zones"].append({"href": z.get("href"), "name": z.get("Name", "")})
#     else:
#         children = await get_child_areas(reader, writer, node["href"])
#         for child in children:
#             node["children"].append(await build_area_tree(reader, writer, child, parent_href=node["href"]))

#     return node

# def collect_status_hrefs(area_node, area_hrefs, zone_hrefs):
#     area_hrefs.append(f"{area_node['href']}/status")
#     for zone in area_node.get("zones", []):
#         zone_hrefs.append(f"{zone['href']}/status")
#     for child in area_node.get("children", []):
#         collect_status_hrefs(child, area_hrefs, zone_hrefs)

# async def subscribe(writer, url):
#     await send_json(writer, {
#         "CommuniqueType": "SubscribeRequest",
#         "Header": {"Url": url}
#     })

# def check_area_occupancy(area_status_msg):
#     area_status = area_status_msg.get("AreaStatus", {})
#     occupancy = area_status.get("OccupancyStatus")
#     if occupancy:
#         status = occupancy.lower()
#         if status == "occupied":
#             print("🏢 Area is currently OCCUPIED.")
#         elif status == "unoccupied":
#             print("🏢 Area is currently UNOCCUPIED.")
#         else:
#             print(f"🏢 Area Occupancy Status: {occupancy}")

# async def listen_for_updates(reader):
#     print("\n🔔 Listening for real-time Area/Zone updates...\n(Press Ctrl+C to stop)")
#     try:
#         while True:
#             msgs = await recv_json(reader)
#             if msgs:
#                 for msg in msgs:
#                     url = msg.get("Header", {}).get("Url", "")
#                     print(f"\n🔔 Update: {url}")
#                     print(json.dumps(msg.get("Body", {}), indent=4))

#                     if url.endswith("/status") and "/area/" in url:
#                         check_area_occupancy(msg.get("Body", {}))
#                     elif url.endswith("/status") and "/zone/" in url:
#                         await check_zone_status_async(msg.get("Body", {}))
#     except asyncio.CancelledError:
#         print("🛑 Listener stopped.")



# async def main_async():
#     if not (os.path.isfile(LEAP_SIGNED_CSR_FILE) and os.path.isfile(LEAP_PRIVATE_KEY_FILE)):
#         print("❌ Missing certificates. Run provisioning first.")
#         return

#     print("🔐 Connecting securely to Lutron...")
#     try:
#         context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
#         context.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
#         context.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
#         context.check_hostname = False

#         loop = asyncio.get_event_loop()
#         reader, writer = await asyncio.open_connection(
#             host=LUTRON_PROC_ADDRESS,
#             port=8081,
#             ssl=context,
#             server_hostname=LUTRON_PROC_HOSTNAME
#         )

#     except Exception as e:
#         print(f"❌ Connection error: {e}")
#         return

#     print("✅ Connected to Lutron.")

#     root_area = await get_root_area(reader, writer)
#     if not root_area:
#         print("❌ Could not fetch root area.")
#         return

#     print("🌳 Building full area tree...")
#     area_tree = await build_area_tree(reader, writer, root_area)

#     area_status_hrefs, zone_status_hrefs = [], []
#     collect_status_hrefs(area_tree, area_status_hrefs, zone_status_hrefs)

#     print("\n📡 Subscribing to all Area & Zone statuses...")

#     for href in area_status_hrefs:
#         await subscribe(writer, href)
#         print(f"✅ Subscribed to Area: {href}")

#     for href in zone_status_hrefs:
#         await subscribe(writer, href)
#         print(f"✅ Subscribed to Zone: {href}")

#     await listen_for_updates(reader)

# if __name__ == "__main__":
#     try:
#         asyncio.run(main_async())
#     except KeyboardInterrupt:
#         print("👋 Exiting...")



# import os
# import json
# import asyncio
# import ssl
# from definitions import *  # your certs, host config, etc.

# CRLF = "\r\n"

# async def send_json(writer, json_msg):
#     msg = (json.dumps(json_msg) + CRLF).encode("ASCII")
#     writer.write(msg)
#     await writer.drain()

# async def recv_json(reader):
#     buffer = await reader.read(5000)
#     if not buffer:
#         return None
#     messages = buffer.decode("ASCII").split(CRLF)
#     results = []
#     for msg in messages:
#         if msg.strip():
#             try:
#                 results.append(json.loads(msg))
#             except json.JSONDecodeError as e:
#                 print(f"⚠️ JSON decoding error: {e}")
#     return results if results else None

# async def get_root_area(reader, writer):
#     await send_json(writer, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
#     responses = await recv_json(reader)
#     if not responses:
#         print(" No response received for root area.")
#         return None
#     for response in responses:
#         if "Body" in response and "Area" in response["Body"]:
#             return response["Body"]["Area"]
#     print("'Area' not found in any response.")
#     return None

# async def get_child_areas(reader, writer, area_href):
#     await send_json(writer, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
#     responses = await recv_json(reader)
#     for response in responses or []:
#         if "Body" in response and "AreaSummaries" in response["Body"]:
#             return response["Body"]["AreaSummaries"]
#     return []

# async def get_zones(reader, writer, area_href):
#     await send_json(writer, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
#     responses = await recv_json(reader)
#     for response in responses or []:
#         if "Body" in response and "Zones" in response["Body"]:
#             zones = response["Body"]["Zones"]
#             # Return only the status URLs for zones
#             return [f"{zone['href']}/status" for zone in zones]
#     return []


# async def build_area_tree(reader, writer, area, parent_href=None):
#     node = {
#         "href": area["href"],
#         "name": area.get("Name", ""),
#         "is_leaf": area.get("IsLeaf", False),
#         "parent": parent_href,
#         "children": [],
#         "zones": []
#     }
#     if node["is_leaf"]:
#         zones = await get_zones(reader, writer, node["href"])
#         for z in zones:
#             node["zones"].append({"href": z.get("href"), "name": z.get("Name", "")})
#     else:
#         children = await get_child_areas(reader, writer, node["href"])
#         for child in children:
#             node["children"].append(await build_area_tree(reader, writer, child, parent_href=node["href"]))
#     return node

# def collect_status_hrefs(area_node, area_hrefs, zone_hrefs):
#     # Add area status url
#     area_hrefs.append(f"{area_node['href']}/status")
#     # Add all zones' status url under this area
#     for zone in area_node.get("zones", []):
#         zone_hrefs.append(f"{zone['href']}/status")
#     # Recurse into children areas
#     for child in area_node.get("children", []):
#         collect_status_hrefs(child, area_hrefs, zone_hrefs)

# async def subscribe(writer, url):
#     await send_json(writer, {
#         "CommuniqueType": "SubscribeRequest",
#         "Header": {"Url": url}
#     })

# def check_area_occupancy(area_status_msg):
#     area_status = area_status_msg.get("AreaStatus", {})
#     occupancy = area_status.get("OccupancyStatus")
#     if occupancy:
#         status = occupancy.lower()
#         if status == "occupied":
#             print(f"🏢 Area is currently OCCUPIED.")
#         elif status == "unoccupied":
#             print(f"🏢 Area is currently UNOCCUPIED.")
#         else:
#             print(f"🏢 Area Occupancy Status: {occupancy}")

# async def check_zone_status_async(zone_status_msg):
#     zone_status = zone_status_msg.get("ZoneStatus", {})
#     if not zone_status:
#         print("⚠️ Empty zone status received.")
#         return
#     zone_name = zone_status.get("Name", "Unknown Zone")
#     level = zone_status.get("Level")
#     status_str = f"💡 Zone Update - {zone_name}: "
#     if level is not None:
#         status_str += f"Level = {level}"
#     else:
#         status_str += "No Level information available."
#     print(status_str)

# async def listen_for_updates(reader):
#     print("\n🔔 Listening for real-time Area & Zone updates...\n(Press Ctrl+C to stop)")
#     try:
#         while True:
#             msgs = await recv_json(reader)
#             if msgs:
#                 for msg in msgs:
#                     url = msg.get("Header", {}).get("Url", "")
#                     print(f"\n🔔 Update: {url}")
#                     print(json.dumps(msg.get("Body", {}), indent=4))

#                     if url.endswith("/status") and "/area/" in url:
#                         check_area_occupancy(msg.get("Body", {}))
#                     elif url.endswith("/status") and "/zone/" in url:
#                         await check_zone_status_async(msg.get("Body", {}))
#     except asyncio.CancelledError:
#         print("🛑 Listener stopped.")
#     except Exception as e:
#         print(f"⚠️ Error while listening: {e}")

# async def main_async():
#     if not (os.path.isfile(LEAP_SIGNED_CSR_FILE) and os.path.isfile(LEAP_PRIVATE_KEY_FILE)):
#         print("❌ Missing certificates. Run provisioning first.")
#         return

#     print("🔐 Connecting securely to Lutron...")
#     try:
#         context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
#         context.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
#         context.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
#         context.check_hostname = False

#         reader, writer = await asyncio.open_connection(
#             host=LUTRON_PROC_ADDRESS,
#             port=8081,
#             ssl=context,
#             server_hostname=LUTRON_PROC_HOSTNAME
#         )
#     except Exception as e:
#         print(f"❌ Connection error: {e}")
#         return

#     print("✅ Connected to Lutron.")

#     root_area = await get_root_area(reader, writer)
#     if not root_area:
#         print("❌ Could not fetch root area.")
#         return

#     print("🌳 Building full area tree...")
#     area_tree = await build_area_tree(reader, writer, root_area)

#     area_status_hrefs, zone_status_hrefs = [], []
#     collect_status_hrefs(area_tree, area_status_hrefs, zone_status_hrefs)

#     print("\n📡 Subscribing to all Area & Zone statuses...")

#     for href in area_status_hrefs:
#         await subscribe(writer, href)
#         print(f"✅ Subscribed to Area status: {href}")

#     for href in zone_status_hrefs:
#         await subscribe(writer, href)
#         print(f"✅ Subscribed to Zone status: {href}")

#     await listen_for_updates(reader)

# if __name__ == "__main__":
#     try:
#         asyncio.run(main_async())
#     except KeyboardInterrupt:
#         print("👋 Exiting...")



import os
import json
import asyncio
import ssl
import datetime
from definitions import *  # your certs, host config, etc.

CRLF = "\r\n"

async def send_json(writer, json_msg):
    msg = (json.dumps(json_msg) + CRLF).encode("ASCII")
    writer.write(msg)
    await writer.drain()

async def recv_json(reader):
    buffer = await reader.read(5000)
    if not buffer:
        return None
    messages = buffer.decode("ASCII").split(CRLF)
    results = []
    for msg in messages:
        if msg.strip():
            try:
                results.append(json.loads(msg))
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON decoding error: {e}")
    return results if results else None

async def get_root_area(reader, writer):
    await send_json(writer, {"CommuniqueType": "ReadRequest", "Header": {"Url": "/area/rootarea"}})
    responses = await recv_json(reader)
    if not responses:
        print("❌ No response received for root area.")
        return None
    for response in responses:
        if "Body" in response and "Area" in response["Body"]:
            return response["Body"]["Area"]
    print("❌ 'Area' not found in any response.")
    return None

async def get_child_areas(reader, writer, area_href):
    await send_json(writer, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/childarea/summary"}})
    responses = await recv_json(reader)
    for response in responses or []:
        if "Body" in response and "AreaSummaries" in response["Body"]:
            return response["Body"]["AreaSummaries"]
    return []

async def get_zones(reader, writer, area_href):
    await send_json(writer, {"CommuniqueType": "ReadRequest", "Header": {"Url": f"{area_href}/associatedzone"}})
    responses = await recv_json(reader)
    for response in responses or []:
        if "Body" in response and "Zones" in response["Body"]:
            zones = response["Body"]["Zones"]
            return zones
    return []

async def build_area_tree(reader, writer, area, parent_href=None):
    try:
        area_href = area.get("href")
        area_name = area.get("Name", "")
        is_leaf = area.get("IsLeaf", False)

        if not area_href:
            print("⚠️ Skipping area due to missing 'href'.")
            return None

        node = {
            "href": area_href,
            "name": area_name,
            "is_leaf": is_leaf,
            "parent": parent_href,
            "children": [],
            "zones": []
        }

        if is_leaf:
            zones = await get_zones(reader, writer, area_href)
            for zone in zones:
                node["zones"].append({
                    "href": zone.get("href", ""),
                    "name": zone.get("Name", "")
                })
        else:
            children = await get_child_areas(reader, writer, area_href)
            for child in children:
                child_node = await build_area_tree(reader, writer, child, parent_href=area_href)
                if child_node:
                    node["children"].append(child_node)
        return node
    except Exception as e:
        print(f"⚠️ Error building area tree node: {e}")
        return None

def collect_status_hrefs(area_node, area_hrefs, zone_hrefs):
    if not area_node:
        return
    area_hrefs.append(f"{area_node['href']}/status")
    for zone in area_node.get("zones", []):
        zone_href = zone.get("href")
        if zone_href:
            zone_hrefs.append(f"{zone_href}/status")
    for child in area_node.get("children", []):
        collect_status_hrefs(child, area_hrefs, zone_hrefs)

async def subscribe(writer, url):
    await send_json(writer, {
        "CommuniqueType": "SubscribeRequest",
        "Header": {"Url": url}
    })

async def check_area_occupancy(area_status_msg):
    area_status = area_status_msg.get("AreaStatus", {})
    occupancy = area_status.get("OccupancyStatus")
    if occupancy:
        status = occupancy.lower()
        if status == "occupied":
            print(f"🏢 Area is currently OCCUPIED.")
        elif status == "unoccupied":
            print(f"🏢 Area is currently UNOCCUPIED.")
        else:
            print(f"🏢 Area Occupancy Status: {occupancy}")

# async def check_zone_status_async(zone_status_msg):
#     zone_status = zone_status_msg.get("ZoneStatus", {})
#     if not zone_status:
#         print("⚠️ Empty zone status received.")
#         return
#     zone_name = zone_status.get("Name", "Unknown Zone")
#     level = zone_status.get("Level")
#     status_str = f"💡 Zone Update - {zone_name}: "
#     if level is not None:
#         status_str += f"Level = {level}"
#     else:
#         status_str += "No Level information available."
#     print(status_str)

async def check_zone_status_async(zone_status_msg):
    # Check if it's a valid zone status
    if "ZoneStatus" not in zone_status_msg:
        # Handle unsupported message formats
        msg = zone_status_msg.get("Message")
        if msg:
            print(f"⚠️ Zone status not supported: {msg}")
        else:
            print("⚠️ Unknown or malformed zone status message.")
        return

    zone_status = zone_status_msg["ZoneStatus"]
    zone_name = zone_status.get("Name", "Unknown Zone")
    level = zone_status.get("Level")

    status_str = f"💡 Zone Update - {zone_name}: "
    if level is not None:
        status_str += f"Level = {level}"
    else:
        status_str += "No Level information available."
    print(status_str)

async def listen_for_updates(reader):
    print("\n🔔 Listening for real-time Area & Zone updates...\n(Press Ctrl+C to stop)")
    zone_state_cache = {}

    try:
        while True:
            msgs = await recv_json(reader)
            if msgs:
                for msg in msgs:
                    url = msg.get("Header", {}).get("Url", "")
                    body = msg.get("Body", {})

                    print(f"\n🔔 Update: {url}")
                    print(json.dumps(body, indent=4))

                    if url.endswith("/status") and "/area/" in url:
                        check_area_occupancy(body)
                    elif url.endswith("/status") and "/zone/" in url:
                        await check_zone_status_async(body)

                        zone_status = body.get("ZoneStatus", {})
                        zone_href = zone_status.get("Zone", {}).get("href", "unknown")
                        zone_id = zone_href.split("/")[-1] if zone_href else "unknown"
                        level = zone_status.get("Level")
                        state = zone_status.get("SwitchedLevel")

                        prev = zone_state_cache.get(zone_id)
                        if prev != (level, state):
                            zone_state_cache[zone_id] = (level, state)
                            if level == 0:
                                print(f"💡 Zone {zone_id} is OFF")
                            else:
                                print(f"💡 Zone {zone_id} is ON (Level={level}, State={state})")

                            with open("zone_log.txt", "a") as f:
                                f.write(f"{datetime.datetime.now()} - Zone {zone_id}: Level={level}, State={state}\n")

    except asyncio.CancelledError:
        print("🛑 Listener stopped.")
    except Exception as e:
        print(f"⚠️ Error while listening: {e}")


# async def listen_for_updates(reader):
#     print("\n🔔 Listening for real-time Area & Zone updates...\n(Press Ctrl+C to stop)")
#     zone_state_cache = {}

#     try:
#         while True:
#             msgs = await recv_json(reader)
#             if msgs:
#                 for msg in msgs:
#                     # Extract relevant data
#                     url = msg.get("Header", {}).get("Url", "")
#                     body = msg.get("Body", {})

#                     # ✅ Log every raw message
#                     print(f"\n📨 RAW MESSAGE from {url}:\n{json.dumps(msg, indent=4)}")

#                     # ✅ Also print simplified view
#                     print(f"\n🔔 Update: {url}")
#                     print(json.dumps(body, indent=4))

#                     # ✅ Area occupancy check
#                     if url.endswith("/status") and "/area/" in url:
#                         check_area_occupancy(body)

#                     # ✅ Zone status check
#                     elif url.endswith("/status") and "/zone/" in url:
#                         await check_zone_status_async(body)

#                         zone_status = body.get("ZoneStatus", {})
#                         zone_href = zone_status.get("Zone", {}).get("href", "unknown")
#                         zone_id = zone_href.split("/")[-1] if zone_href else "unknown"
#                         level = zone_status.get("Level")
#                         state = zone_status.get("SwitchedLevel")

#                         prev = zone_state_cache.get(zone_id)
#                         if prev != (level, state):
#                             zone_state_cache[zone_id] = (level, state)
#                             if level == 0:
#                                 print(f"💡 Zone {zone_id} is OFF")
#                             else:
#                                 print(f"💡 Zone {zone_id} is ON (Level={level}, State={state})")

#                             # ✅ Log to file
#                             with open("zone_log.txt", "a") as f:
#                                 f.write(f"{datetime.datetime.now()} - Zone {zone_id}: Level={level}, State={state}\n")

#                     # ✅ Log everything to file (optional)
#                     with open("all_messages_log.txt", "a") as log_file:
#                         log_file.write(f"{datetime.datetime.now()}\n")
#                         log_file.write(json.dumps(msg, indent=4) + "\n\n")

#     except asyncio.CancelledError:
#         print("🛑 Listener stopped.")
#     except Exception as e:
#         print(f"⚠️ Error while listening: {e}")

async def main_async():
    if not (os.path.isfile(LEAP_SIGNED_CSR_FILE) and os.path.isfile(LEAP_PRIVATE_KEY_FILE)):
        print("❌ Missing certificates. Run provisioning first.")
        return

    print("🔐 Connecting securely to Lutron...")
    try:
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
        context.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
        context.check_hostname = False

        reader, writer = await asyncio.open_connection(
            host=LUTRON_PROC_ADDRESS,
            port=8081,
            ssl=context,
            server_hostname=LUTRON_PROC_HOSTNAME
        )
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return

    print("✅ Connected to Lutron.")

    root_area = await get_root_area(reader, writer)
    if not root_area:
        print("❌ Could not fetch root area.")
        return

    print("🌳 Building full area tree...")
    area_tree = await build_area_tree(reader, writer, root_area)
    if not area_tree:
        print("❌ Failed to build area tree.")
        return

    area_status_hrefs, zone_status_hrefs = [], []
    collect_status_hrefs(area_tree, area_status_hrefs, zone_status_hrefs)

    print("\n📡 Subscribing to all Area & Zone statuses...")
    for href in area_status_hrefs:
        await subscribe(writer, href)
        print(f"✅ Subscribed to Area status: {href}")
    for href in zone_status_hrefs:
        await subscribe(writer, href)
        print(f"✅ Subscribed to Zone status: {href}")

    await listen_for_updates(reader)

if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("👋 Exiting...")
