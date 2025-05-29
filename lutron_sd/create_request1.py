
import asyncio
import ssl
import json
import time
from definitions import *

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

async def toggle_zone(writer, zone_id):
    toggle = True
    while True:
        level = "On" if toggle else "Off"
        print(f"🔁 Sending {level} command to zone {zone_id}")

        msg = {
            "CommuniqueType": "CreateRequest",
            "Header": {
                "Url": f"/zone/{zone_id}/commandprocessor"
            },
            "Body": {
                "Command": {
                    "CommandType": "GoToSwitchedLevel",
                    "SwitchedLevelParameters": {
                        "SwitchedLevel": level
                    }
                }
            }
        }

        await send_json(writer, msg)
        toggle = not toggle
        await asyncio.sleep(5)  # Delay of 5 seconds

async def main():
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

        print("✅ Connected to Lutron.")
        await toggle_zone(writer, zone_id=1116)
        

    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Exiting...")



# import asyncio
# import ssl
# import json
# from definitions import *

# CRLF = "\r\n"

# async def send_json(writer, json_msg):
#     msg = (json.dumps(json_msg) + CRLF).encode("ASCII")
#     writer.write(msg)
#     await writer.drain()

# async def toggle_zone(writer, zone_id):
#     toggle = True
#     while True:
#         level = "On" if toggle else "Off"
#         print(f"🔁 Sending {level} to zone {zone_id}")
#         msg = {
#             "CommuniqueType": "CreateRequest",
#             "Header": {
#                 "Url": f"/zone/{zone_id}/commandprocessor"
#             },
#             "Body": {
#                 "Command": {
#                     "CommandType": "GoToSwitchedLevel",
#                     "SwitchedLevelParameters": {
#                         "SwitchedLevel": level
#                     }
#                 }
#             }
#         }
#         await send_json(writer, msg)
#         toggle = not toggle
#         await asyncio.sleep(10)

# async def main():
#     print("🔐 Connecting to Lutron...")
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

#         print("✅ Connected to Lutron.")

#         # List of all your zone IDs
#         zone_ids = [1035, 1107, 1116,  1125]  # Add more zone IDs as needed

#         # Start toggle tasks for each zone
#         await asyncio.gather(*(toggle_zone(writer, zid) for zid in zone_ids))

#     except Exception as e:
#         print(f"❌ Connection error: {e}")

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("👋 Exiting...")
