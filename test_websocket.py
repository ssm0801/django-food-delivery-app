#!/usr/bin/env python3
"""
Simple WebSocket test script to verify real-time chat functionality
"""

import asyncio
import websockets
import json
import sys

async def test_websocket():
    """Test WebSocket connection to chat endpoint"""
    
    # Test connection to a sample booking (you'll need to adjust the booking_id)
    booking_id = 1
    uri = f"ws://127.0.0.1:8000/ws/chat/{booking_id}/"
    
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Send a test message
            test_message = {
                "message": "Hello from WebSocket test!"
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 Sent test message")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"📥 Received: {data}")
                print("✅ WebSocket communication working!")
                
            except asyncio.TimeoutError:
                print("⏰ No response received within 5 seconds")
                
    except websockets.exceptions.ConnectionClosed:
        print("❌ Connection closed by server (likely authentication required)")
    except ConnectionRefusedError:
        print("❌ Connection refused. Make sure Django server is running.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing WebSocket Chat Functionality")
    print("Note: This test requires authentication, so it may fail.")
    print("Use browser developer tools to test with authenticated session.\n")
    
    asyncio.run(test_websocket())