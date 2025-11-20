#!/usr/bin/env python3
"""
Decentralized AI Chatbot using QuIXI + Local LLM
"""

import os
import json
import time
import requests
from openai import OpenAI
import paho.mqtt.client as mqtt

# Configuration
QUIXI_API = "http://localhost:8001"
LM_STUDIO_API = "http://localhost:1234/v1"  # LM Studio local server
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

# Bot personality
SYSTEM_PROMPT = """You are a helpful AI assistant running on a decentralized network. 
You are privacy-focused and run locally, not on cloud servers. Be friendly, concise, 
and knowledgeable. You can discuss technology, answer questions, and have conversations."""

# Initialize OpenAI client pointing to local LM Studio
client = OpenAI(base_url=LM_STUDIO_API, api_key="not-needed")

# Conversation memory (address -> message history)
conversation_history = {}

def send_message(address, message):
    """Send a message back to a user via QuIXI"""
    try:
        response = requests.get(f"{QUIXI_API}/sendChatMessage", params={
            "address": address,
            "message": message,
            "channel": 0
        })
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def get_ai_response(user_address, user_message):
    """Get response from local LLM with conversation history"""
    
    # Initialize conversation history for new users
    if user_address not in conversation_history:
        conversation_history[user_address] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    
    # Add user message to history
    conversation_history[user_address].append({
        "role": "user",
        "content": user_message
    })
    
    # Keep only last 10 messages to manage memory
    if len(conversation_history[user_address]) > 21:  # 1 system + 20 messages
        conversation_history[user_address] = [
            conversation_history[user_address][0]  # Keep system prompt
        ] + conversation_history[user_address][-20:]  # Keep last 20
    
    try:
        # Call local LLM
        completion = client.chat.completions.create(
            model="local-model",  # Model name doesn't matter for LM Studio
            messages=conversation_history[user_address],
            temperature=0.7,
            max_tokens=500
        )
        
        ai_response = completion.choices[0].message.content
        
        # Add AI response to history
        conversation_history[user_address].append({
            "role": "assistant",
            "content": ai_response
        })
        
        return ai_response
    
    except Exception as e:
        print(f"Error getting AI response: {e}")
        return "Sorry, I encountered an error processing your request. Please try again."

def handle_command(address, message):
    """Handle special commands"""
    cmd = message.lower().strip()
    
    if cmd == "/reset":
        if address in conversation_history:
            conversation_history[address] = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
        return "🔄 Conversation reset. Let's start fresh!"
    
    elif cmd == "/help":
        return """🤖 AI Assistant Commands:
• Chat normally for AI responses
• /reset - Clear conversation history
• /help - Show this message
• /stats - Bot statistics

I'm running locally with full privacy - your messages never leave this device!"""
    
    elif cmd == "/stats":
        msg_count = len(conversation_history.get(address, [])) - 1  # Exclude system prompt
        total_users = len(conversation_history)
        return f"""📊 Bot Statistics:
• Messages in this conversation: {msg_count}
• Total users served: {total_users}
• Model: Llama 3 (local)
• Privacy: 100% (all local processing)"""
    
    return None  # Not a command, process as normal message

def on_connect(mqtt_client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print(f"✓ Connected to MQTT broker successfully")
    else:
        print(f"❌ Connection failed with code {rc}")
        return
    
    # Subscribe to chat messages and contact requests
    print("📡 Subscribing to MQTT topics...")
    # Subscribe to both the exact topic and wildcard variants to be robust
    mqtt_client.subscribe("Chat")
    mqtt_client.subscribe("Chat/#")
    mqtt_client.subscribe("RequestAdd2")
    mqtt_client.subscribe("RequestAdd2/#")
    # Also subscribe to all QuIXI topics so we don't miss types like FriendStatusUpdate
    mqtt_client.subscribe("#")
    print("   ✓ Subscribed to Chat/# and RequestAdd2/# and # (all topics)")
    
    print("\n🤖 AI Chatbot is ready!")
    print("Add your bot as a contact in Spixi and start chatting!")
    print("Waiting for messages...\n")

def on_message(mqtt_client, userdata, msg):
    """Callback when a message is received"""
    # Debug: Show all messages received
    print(f"📨 MQTT message received on topic: {msg.topic}")

    try:
        # Parse incoming message (tolerant decoding)
        payload = None
        try:
            payload = msg.payload.decode()
        except Exception:
            payload = str(msg.payload)

        print(f"📦 Payload: {payload[:200]}...")  # Show first 200 chars
        data = None
        try:
            data = json.loads(payload)
        except Exception:
            # Not JSON — wrap raw payload for handlers
            data = {"sender": None, "data": {"data": payload}}

        # Determine root topic (handles both 'Chat' and 'Chat/..' forms)
        root_topic = msg.topic.split('/', 1)[0]

        # Handle contact requests (auto-accept)
        if root_topic == "RequestAdd2":
            # Accept multiple sender formats
            sender = None
            if isinstance(data.get("sender"), dict):
                sender = data.get("sender", {}).get("base58Address")
            elif isinstance(data.get("sender"), str):
                sender = data.get("sender")

            if sender:
                print(f"📥 Auto-accepting contact: {sender}")
                resp = requests.get(f"{QUIXI_API}/acceptContact", params={"address": sender})
                print(f"   Accept response: {resp.status_code}")
                time.sleep(1)  # Wait for contact to be added
                send_message(sender, "👋 Hi! I'm your local AI assistant. Ask me anything!\n\nI run on your hardware with full privacy. Type /help for commands.")

        # Handle chat messages
        elif root_topic == "Chat":
            # Accept multiple sender formats
            sender = None
            s = data.get("sender")
            if isinstance(s, dict):
                sender = s.get("base58Address") or s.get("address")
            elif isinstance(s, str):
                sender = s

            # Message payload may be nested under data.data or be raw text
            message = None
            if isinstance(data.get("data"), dict):
                inner = data.get("data")
                # support both nested forms
                message = inner.get("data") or inner.get("text")
            if message is None:
                # fallback to raw payload (when not JSON)
                if isinstance(payload, str):
                    message = payload

            if not sender or not message:
                print(f"⚠️  Missing sender or message in payload (sender={sender}, message={message})")
                return

            message = message.strip()
            print(f"💬 Message from {sender[:8]}...: {message}")
            
            # Check for commands first
            command_response = handle_command(sender, message)
            if command_response:
                send_message(sender, command_response)
                return
            
            # Show typing indicator (optional)
            print(f"🤔 Processing with AI...")
            
            # Get AI response
            ai_response = get_ai_response(sender, message)
            
            # Send response
            print(f"🤖 Response: {ai_response[:100]}...")
            send_message(sender, ai_response)
        else:
            print(f"ℹ️  Unhandled topic: {msg.topic}")
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print(f"   Raw payload: {msg.payload}")
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main bot loop"""
    print("🚀 Starting Decentralized AI Chatbot...")
    print(f"📡 QuIXI API: {QUIXI_API}")
    print(f"🧠 LM Studio: {LM_STUDIO_API}")
    
    # Test LM Studio connection
    try:
        response = requests.get(f"{LM_STUDIO_API}/models")
        print(f"✓ LM Studio connected")
    except:
        print(f"⚠️  Warning: Cannot connect to LM Studio. Make sure it's running!")
        return
    
    # Test QuIXI connection
    try:
        response = requests.get(f"{QUIXI_API}/myWallet")
        if response.status_code == 200:
            wallet_map = response.json().get("result", {})
            if isinstance(wallet_map, dict) and wallet_map:
                print("✓ QuIXI connected")
                addresses = list(wallet_map.keys())
                primary = addresses[0]
                print(f"📍 Primary bot address: {primary}")
                if len(addresses) > 1:
                    print(f"📍 Additional addresses ({len(addresses)-1}):")
                    for addr in addresses[1:]:
                        print(f"   - {addr}")
                print("\n💰 Wallet balances:")
                for addr, balance in wallet_map.items():
                    print(f"   {addr}: {balance} IXI")
                print("\n🎯 Add one of these addresses as a contact in Spixi to start chatting!")
            else:
                print("⚠️  Warning: QuIXI returned empty wallet data.")
        else:
            print(f"⚠️  Warning: QuIXI returned status {response.status_code}")
    except Exception as e:
        print(f"⚠️  Warning: Cannot connect to QuIXI. Make sure it's running! ({e})")
        return
    
    # Connect to MQTT broker
    try:
        # Compatible with both paho-mqtt v1.x and v2.x
        from paho.mqtt import client as mqtt_module
        if hasattr(mqtt_module, 'CallbackAPIVersion'):
            # paho-mqtt v2.0+
            mqtt_client = mqtt.Client(mqtt_module.CallbackAPIVersion.VERSION1)
        else:
            # paho-mqtt v1.x
            mqtt_client = mqtt.Client()
    except:
        # Fallback
        mqtt_client = mqtt.Client()
    
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    # Add optional debug handlers
    def on_subscribe(client, userdata, mid, granted_qos):
        print(f"Subscribed (mid={mid}, granted_qos={granted_qos})")

    def on_log(client, userdata, level, buf):
        # keep logs light; uncomment to debug
        # print(f"MQTT log: level={level}, buf={buf}")
        pass

    mqtt_client.on_subscribe = on_subscribe
    mqtt_client.on_log = on_log
    
    print(f"🔌 Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print("✓ Connected to MQTT broker")
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down bot...")
        mqtt_client.disconnect()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
