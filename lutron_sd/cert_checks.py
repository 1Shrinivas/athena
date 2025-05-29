# # This runs a few validations on your keys and certs which is valuable for debugging.
# # This file is not to be used in shipping software. It does not run exhaustive security validations on your certs and keys.
# # Run pip install pycryptodome for Crypto.PublicKey
# # (c) Lutron Electronics Co. Inc. 2023. All rights reserved
# #
# import sys
# from cryptography import x509
# from cryptography.x509.oid import NameOID
# from cryptography.hazmat.primitives.asymmetric import rsa
# from datetime import datetime
# from Crypto.PublicKey import RSA

# # Import the definitions and make sure all the certs you need exist
# from definitions import *

# # Step 1: Check validity of all certs
# #
# print ("Check if certs have expired")
# certs = [LAP_SIGNED_CSR_FILE, LAP_LUTRON_ROOT_FILE, LAP_LUTRON_INTERMEDIATE_FILE, LEAP_SIGNED_CSR_FILE, LEAP_LUTRON_PROC_ROOT_FILE, LEAP_LUTRON_PROC_INTERMEDIATE_FILE]
# now = datetime.now()
# for certname in certs:
#     try:
#         with open(certname, "r") as cert_file:
#             cert_bytes = cert_file.read()
#             not_valid_after = x509.load_pem_x509_certificate(cert_bytes.encode()).not_valid_after
#             not_valid_before = x509.load_pem_x509_certificate(cert_bytes.encode()).not_valid_before
#             if now < not_valid_before or now > not_valid_after:
#                 print(f"  Fail: {certname} ({not_valid_before} to {not_valid_after})")
#             else:
#                 print(f"  Success: {certname}")
#     except Exception as e:
#         print (f"  Error: {e}")

# # Step 2: Check that the signed crs and private key correspond
# #
# print ("Check the private key generated the associated public key")
# certs = [{LAP_PRIVATE_KEY_FILE, LAP_SIGNED_CSR_FILE}, {LEAP_PRIVATE_KEY_FILE, LEAP_SIGNED_CSR_FILE}]
# for keyname, certname in certs:
#     try:
#         with open(certname, "r") as cert_file:
#             cert_bytes = cert_file.read()
#             certmodulus = RSA.import_key(cert_bytes).n
#         with open(keyname, "r") as key_file:
#             key_bytes = key_file.read()
#             keymodulus = RSA.import_key(key_bytes).n
#         if (certmodulus != keymodulus):
#             print(f"  Fail: keypair {keyname} {certname}")
#         else:
#             print(f"  Success: keypair {keyname}, {certname}")
#     except Exception as e:
#         print (f"  Error: {e}")

# # Step 3: Retrieve PROCESSOR_HOSTNAME from the LEAP_LUTRON_PROC_ROOT_FILE
# #
# print ("Retrieve the hostname from the processor's CA file")
# try:
#     with open(LEAP_LUTRON_PROC_ROOT_FILE, "r") as cert_file:
#         cert_bytes = cert_file.read()
#         PROCESSOR_HOSTNAME = x509.load_pem_x509_certificate(cert_bytes.encode()).issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
# except Exception as e:
#     print (f"  Error: {e}")
#     sys.exit()
# print(f"  Success: hostname is {PROCESSOR_HOSTNAME}")


import os, sys
import json
import socket
import ssl
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime
from Crypto.PublicKey import RSA

# Import the definitions and make sure all the certs you need exist
from app_sample import _recv_json, _send_json
from definitions import *

# Step 1: Check validity of all certs
print("Check if certs have expired")
certs = [LAP_SIGNED_CSR_FILE, LAP_LUTRON_ROOT_FILE, LAP_LUTRON_INTERMEDIATE_FILE, LEAP_SIGNED_CSR_FILE, LEAP_LUTRON_PROC_ROOT_FILE, LEAP_LUTRON_PROC_INTERMEDIATE_FILE]
now = datetime.now()
for certname in certs:
    try:
        with open(certname, "r") as cert_file:
            cert_bytes = cert_file.read()
            cert = x509.load_pem_x509_certificate(cert_bytes.encode())
            not_valid_after = cert.not_valid_after
            not_valid_before = cert.not_valid_before
            if now < not_valid_before or now > not_valid_after:
                print(f"  Fail: {certname} ({not_valid_before} to {not_valid_after})")
            else:
                print(f"  Success: {certname}")
    except Exception as e:
        print(f"  Error: {e}")

# Step 2: Check that the signed csr and private key correspond
print("Check the private key generated the associated public key")
certs = [{LAP_PRIVATE_KEY_FILE, LAP_SIGNED_CSR_FILE}, {LEAP_PRIVATE_KEY_FILE, LEAP_SIGNED_CSR_FILE}]
for keyname, certname in certs:
    try:
        with open(certname, "r") as cert_file:
            cert_bytes = cert_file.read()
            certmodulus = RSA.import_key(cert_bytes).n
        with open(keyname, "r") as key_file:
            key_bytes = key_file.read()
            keymodulus = RSA.import_key(key_bytes).n
        if (certmodulus != keymodulus):
            print(f"  Fail: keypair {keyname} {certname}")
        else:
            print(f"  Success: keypair {keyname}, {certname}")
    except Exception as e:
        print(f"  Error: {e}")

# Step 3: Retrieve PROCESSOR_HOSTNAME from the LEAP_LUTRON_PROC_ROOT_FILE
print("Retrieve the hostname from the processor's CA file")
try:
    with open(LEAP_LUTRON_PROC_ROOT_FILE, "r") as cert_file:
        cert_bytes = cert_file.read()
        cert = x509.load_pem_x509_certificate(cert_bytes.encode())
        PROCESSOR_HOSTNAME = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
except Exception as e:
    print(f"  Error: {e}")
    sys.exit()
print(f"  Success: hostname is {PROCESSOR_HOSTNAME}")

# Step 4: Setup a connection with the LEAP API integration service (8081)
print(f"Establishing a password-less secure connection to Lutron Processor {LUTRON_PROC_HOSTNAME} at {LUTRON_PROC_ADDRESS}")

try:
    leap_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    leap_context.verify_mode = ssl.CERT_REQUIRED
    leap_context.load_verify_locations(cafile=LAP_LUTRON_ROOT_FILE)
    leap_context.load_cert_chain(certfile=LEAP_SIGNED_CSR_FILE, keyfile=LEAP_PRIVATE_KEY_FILE)
    leap_context.check_hostname = True
    sock = socket.create_connection((LUTRON_PROC_ADDRESS, 8081))
    ssock = leap_context.wrap_socket(sock, server_hostname=LUTRON_PROC_HOSTNAME)
    print("  Success: Authenticated connection established")
except Exception as e:
    print(f"  Error: {e}")
    sys.exit()

# Step 5: Test the API by requesting the root area
print("Test the API by requesting the root area")

# Check if the URL format is correct (use a different endpoint to test)
url_path = "/area/rootarea"  # You can test with another URL like '/system'
print(f"  Sending request to URL: {url_path}")

_send_json(ssock, {
    "CommuniqueType": "ReadRequest",
    "Header": {
        "Url": url_path
    }
})

recv_msg = _recv_json(ssock)

# Log the raw response for debugging purposes
print("Raw response from processor:", recv_msg)

# Check the status code of the response
if recv_msg is not None:
    status_code = recv_msg.get("Header", {}).get("StatusCode")
    if status_code == "200 OK":  # response is 200 OK for success
        print(f"  Success. Found {recv_msg['Body']}")
    else:
        print(f"  Error: Received a {status_code} response from the processor. Message: {recv_msg.get('Body')}")
else:
    print("  Error: No response received from the processor")

ssock.close()


