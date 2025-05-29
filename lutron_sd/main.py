# FastAPI entrypoint
from fastapi import FastAPI
from leap_client import send_leap_command

app = FastAPI()

@app.get('/')
def root():
    return {'message': 'Lutron LEAP backend'}

@app.get("/test-connection")
def test_connection():
    print("🔌 Attempting to send LEAP command...")
    command = {
        "CommuniqueType": "ReadRequest",
        "Header": {
            "Url": "/area/rootarea"
        }
    }
    try:
        response = send_leap_command(command)
        print("✅ LEAP Response:", response)
        return response
    except Exception as e:
        print("❌ ERROR:", str(e))
        return {"error": str(e)}

