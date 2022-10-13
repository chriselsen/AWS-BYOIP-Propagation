"""
Subscribe to a RIS Live stream and output data about updates (announce, withdraw) from a certain AWS BYOIP range.
This AWS BYOIP range is announced every even hour (UTC) and withdrawn every uneven hour (UTC). 
Information about last action and exact timestamp for this action:
https://www.edge-cloud.net/byoip-propagation/us-east-1.html

IMPORTANT: this example requires 'websocket-client' for Python 2 or 3.

If you use the 'websockets' package instead (Python 3 only) you will need to change the code because it has a somewhat different API.
"""
import json
import websocket

ws = websocket.WebSocket()
ws.connect("wss://ris-live.ripe.net/v1/ws/?client=aws-byoip-propagation-client-1")
params = {
    "prefix":"2602:fb2a:00c0::/46",
                    }
ws.send(json.dumps({
    "type": "ris_subscribe",
    "data": params
}))
print("Timestamp RIPE-RIS-Host Peer-ASN")
for data in ws:
    parsed = json.loads(data)
    try:
        print(parsed["data"]["timestamp"], parsed["data"]["host"], parsed["data"]["peer_asn"])
    except:
        pass
