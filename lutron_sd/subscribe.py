import asyncio
import ssl
import json
import datetime
import os

from definitions import *  # Certs and Lutron processor details

# Async send JSON via StreamWriter
async def send_json(writer: asyncio.StreamWriter, json_msg: dict):
    msg = json.dumps(json_msg) + "\r\n"
    writer.write(msg.encode("ASCII"))
    await writer.drain()

# Async receive JSON via StreamReader (assume messages end with newline)
async def recv_json(reader: asyncio.StreamReader):
    try:
        line = await reader.readline()
        if not line:
            return None
        return json.loads(line.decode("ASCII"))
    except Exception as e:
        print(f"⚠️ JSON decode error: {e}")
        return None

# Async functions to send ReadRequest (or SubscribeRequest) and receive response
async def async_read_request(writer, reader, url):
    await send_json(writer, {"CommuniqueType": "ReadRequest", "Header": {"Url": url}})
    response = await recv_json(reader)
    return response

# Async version of building the area tree with subscribes
async def build_area_tree(writer, reader, area, parent_href=None):
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

    # Fetch area status
    response = await async_read_request(writer, reader, f"{area['href']}/status")
    node["area_status"] = response.get("Body", {}).get("AreaStatus", {}) if response else {}

    if area.get("IsLeaf", False):
        # Fetch zones
        response = await async_read_request(writer, reader, f"{area['href']}/associatedzone")
        zones = response.get("Body", {}).get("Zones", []) if response else []
        for z in zones:
            resp_status = await async_read_request(writer, reader, f"{z['href']}/status")
            zone_status = resp_status.get("Body", {}).get("ZoneStatus", {}) if resp_status else {}
            node["zones"].append({
                "Zone ID": z.get("href", ""),
                "Name": z.get("Name", ""),
                "ControlType": z.get("ControlType", ""),
                "IsLight": z.get("Category", {}).get("IsLight", False),
                "Associated Area": z.get("AssociatedArea", {}).get("href", ""),
                "Status": zone_status
            })

        # Fetch scenes
        response = await async_read_request(writer, reader, f"{area['href']}/areascene")
        scenes = response.get("Body", {}).get("AreaScenes", []) if response else []
        node["scenes"] = [{
            "Scene ID": s.get("href", ""),
            "Name": s.get("Name", ""),
            "Associated Area": s.get("Parent", {}).get("href", "")
        } for s in scenes]

        # Fetch control stations and buttons
        response = await async_read_request(writer, reader, f"{area['href']}/associatedcontrolstation")
        control_stations = response.get("Body", {}).get("ControlStations", []) if response else []
        for cs in control_stations:
            buttons = []
            for dev in cs.get("AssociatedGangedDevices", []):
                dev_href = dev.get("Device", {}).get("href", "")
                if dev_href:
                    resp_buttons = await async_read_request(writer, reader, f"{dev_href}/buttongroup/expanded")
                    button_groups = resp_buttons.get("Body", {}).get("ButtonGroupsExpanded", []) if resp_buttons else []
                    for group in button_groups:
                        buttons.extend(group.get("Buttons", []))
            node["control_stations"].append({
                "ControlStation ID": cs.get("href", ""),
                "Name": cs.get("Name", ""),
                "DeviceType": cs.get("AssociatedGangedDevices", [{}])[0].get("Device", {}).get("DeviceType", ""),
                "Buttons": buttons
            })
    else:
        # Recursively fetch child areas
        response = await async_read_request(writer, reader, f"{area['href']}/childarea/summary")
        children = response.get("Body", {}).get("AreaSummaries", []) if response else []
        for child in children:
            child_node = await build_area_tree(writer, reader, child, parent_href=area["href"])
            node["children"].append(child_node)

    return node

# Listener for real-time subscription updates
async def listen_for_updates(reader):
    print("\n🔔 Listening for real-time updates... (Press Ctrl+C to stop)\n")
    zone_state_cache = {}

    try:
        while True:
            msgs = await recv_json(reader)
            if not msgs:
                continue

            for msg in msgs if isinstance(msgs, list) else [msgs]:
                url = msg.get("Header", {}).get("Url", "")
                body = msg.get("Body", {})

                print(f"\n🔔 Update: {url}")
                print(json.dumps(body, indent=4))

                if url.endswith("/status") and "/area/" in url:
                    # Handle area status update (custom function)
                    pass
                elif url.endswith("/status") and "/zone/" in url:
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

# Main async entrypoint
async def main():
    print("Checking for required certificates...")
    if not (os.path.isfile(LEAP_PRIVATE_KEY_FILE) and os.path.isfile(LEAP_SIGNED_CSR_FILE)):
        print("Error: Missing certificates. Run lap_sample.py first.")
        return

    print("Certificates found.")
    print("Establishing a secure connection to Lutron Processor...")

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
    ssl_context.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
    ssl_context.check_hostname = False

    try:
        reader, writer = await asyncio.open_connection(LUTRON_PROC_ADDRESS, 8081, ssl=ssl_context, server_hostname=LUTRON_PROC_HOSTNAME)
        print("Authenticated connection established.")
    except Exception as e:
        print(f"Error connecting: {e}")
        return

    # Read root area
    response = await async_read_request(writer, reader, "/area/rootarea")
    root_area = response.get("Body", {}).get("Area") if response else None
    if not root_area:
        print("Failed to fetch root area.")
        writer.close()
        await writer.wait_closed()
        return

    # Build full area tree
    print("Building area tree...")
    full_tree = await build_area_tree(writer, reader, root_area)
    print("\nFinal JSON Structure with All ReadRequest Data:")
    print(json.dumps(full_tree, indent=4))

    # Optionally, send SubscribeRequest here if your device supports it:
    # For example:
    # await send_json(writer, {"CommuniqueType": "SubscribeRequest", "Header": {"Url": "/area/rootarea/subscribe"}})

    # Listen for real-time updates indefinitely
    await listen_for_updates(reader)

    writer.close()
    await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
