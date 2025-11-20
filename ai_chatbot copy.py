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
import segno

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


def select_address_from_list(wallets):
    """Select a sensible address from the `wallets` list returned by QuIXI.

    Handles cases where the list contains plain strings or dictionaries.
    Returns the first valid Base58-like string found or None.
    """
    if not wallets:
        return None

    # If API returned a dict-like value (older/newer variants), handle it
    for w in wallets:
        # plain string address
        if isinstance(w, str) and w.strip():
            return w.strip()

        # dict-like wallet object, try common fields
        if isinstance(w, dict):
            for key in ("address", "base58Address", "wallet", "addr"):
                val = w.get(key) if key in w else None
                if isinstance(val, str) and val.strip():
                    return val.strip()

    # Fallback: try stringifying first item
    try:
        return str(wallets[0])
    except Exception:
        return None


def print_and_save_qr(address, filename="quixi_address.png"):
    """Print an ASCII QR to terminal and save a PNG file for the address."""
    if not address:
        print("⚠️  No address provided for QR generation.")
        return

    try:
        qr = segno.make(address)
        # Print compact ASCII/terminal QR
        try:
            terminal_qr = qr.terminal(compact=True)
            print("\nQR code (terminal):\n")
            print(terminal_qr)
        except Exception:
            # If terminal rendering fails, fall back to notice
            print("(QR terminal rendering not available)")

        # Save PNG file
        qr.save(filename, scale=6)
        print(f"Saved QR image to: {filename}")
    except Exception as e:
        print(f"Error generating QR code: {e}")

def on_connect(mqtt_client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    print(f"Connected to MQTT broker with result code {rc}")
    
    # Subscribe to chat messages and contact requests
    mqtt_client.subscribe("Chat/#")
    mqtt_client.subscribe("RequestAdd2/#")
    
    print("🤖 AI Chatbot is ready!")
    print("Add your bot as a contact in Spixi and start chatting!")

def on_message(mqtt_client, userdata, msg):
    """Callback when a message is received"""
    try:
        # Parse incoming message
        data = json.loads(msg.payload.decode())
        
        # Handle contact requests (auto-accept)
        if msg.topic.startswith("RequestAdd2/"):
            sender = data.get("sender", {}).get("base58Address")
            if sender:
                print(f"📥 Auto-accepting contact: {sender}")
                requests.get(f"{QUIXI_API}/acceptContact", params={"address": sender})
                time.sleep(1)  # Wait for contact to be added
                send_message(sender, "👋 Hi! I'm your local AI assistant. Ask me anything!\n\nI run on your hardware with full privacy. Type /help for commands.")
        
        # Handle chat messages
        elif msg.topic.startswith("Chat/"):
            sender = data.get("sender", {}).get("base58Address")
            message = data.get("data", {}).get("data", "").strip()
            
            if not sender or not message:
                return
            
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
    
    except Exception as e:
        print(f"❌ Error processing message: {e}")

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
        response = requests.get(f"{QUIXI_API}/listWallets")
        if response.status_code == 200:
            wallets = response.json().get("result", [])
            if isinstance(wallets, list) and wallets:
                print(f"✓ QuIXI connected")
                # Choose a primary address to display (robust handling)
                primary = select_address_from_list(wallets)
                if primary:
                    print(f"📍 Bot address: {primary}")
                    # Print and save QR code for convenience
                    print_and_save_qr(primary, filename="quixi_address.png")
                else:
                    print(f"📍 Bot wallets ({len(wallets)}):")
                    for w in wallets:
                        print(f"   - {w}")
                    print(f"\n🎯 Add one of these addresses as a contact in Spixi to start chatting!")
            else:
                print(f"⚠️  Warning: QuIXI returned no wallets.")
        else:
            print(f"⚠️  Warning: QuIXI returned status {response.status_code}")
    except Exception as e:
        print(f"⚠️  Warning: Cannot connect to QuIXI. Make sure it's running! ({e})")
        return
    
    # Connect to MQTT broker
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down bot...")
        mqtt_client.disconnect()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
