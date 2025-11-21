#!/usr/bin/env python3
"""
Decentralized AI Chatbot using QuIXI + Local LLM
"""

import os
import json
import time
import threading
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from openai import OpenAI
import paho.mqtt.client as mqtt

# Configuration (environment-overridable)
QUIXI_API = os.getenv("QUIXI_API", "http://localhost:8001")
LM_STUDIO_API = os.getenv("LM_STUDIO_API", "http://localhost:1234/v1")  # LM Studio local server
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO), format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ai_chatbot")

# HTTP session with retries
session = requests.Session()
retries = Retry(total=3, backoff_factor=0.5, status_forcelist=(500, 502, 503, 504))
adapter = HTTPAdapter(max_retries=retries)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Bot personality
SYSTEM_PROMPT = """You are a helpful AI assistant running on a decentralized network. 
You are privacy-focused and run locally, not on cloud servers. Be friendly, concise, 
and knowledgeable. You can discuss technology, answer questions, and have conversations."""

# Initialize OpenAI client pointing to local LM Studio
client = OpenAI(base_url=LM_STUDIO_API, api_key=os.getenv("LM_API_KEY", "not-needed"))

# Conversation memory (address -> message history) with lock for thread safety
conversation_history = {}
history_lock = threading.Lock()

def send_message(address, message):
    """Send a message back to a user via QuIXI"""
    try:
        resp = session.get(f"{QUIXI_API}/sendChatMessage", params={
            "address": address,
            "message": message,
            "channel": 0
        }, timeout=REQUEST_TIMEOUT)
        return resp.status_code == 200
    except Exception as e:
        logger.exception("Error sending message to %s", address)
        return False

def get_ai_response(user_address, user_message):
    """Get response from local LLM with conversation history"""
    # Thread-safe history update
    with history_lock:
        if user_address not in conversation_history:
            conversation_history[user_address] = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
        # Add user message to history
        conversation_history[user_address].append({
            "role": "user",
            "content": user_message
        })
        # Keep only last 20 user/assistant messages + system prompt
        if len(conversation_history[user_address]) > 21:  # 1 system + 20 messages
            conversation_history[user_address] = [
                conversation_history[user_address][0]
            ] + conversation_history[user_address][-20:]
    
    try:
        # Call local LLM
        completion = client.chat.completions.create(
            model=os.getenv("LM_MODEL", "local-model"),
            messages=conversation_history[user_address],
            temperature=float(os.getenv("LM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LM_MAX_TOKENS", "500"))
        )
        ai_response = completion.choices[0].message.content
        # Add AI response to history (thread-safe)
        with history_lock:
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
        with history_lock:
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
        with history_lock:
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
        logger.info("Connected to MQTT broker successfully")
    else:
        logger.error("Connection failed with code %s", rc)
        return

    # Subscribe to chat messages and contact requests
    logger.info("Subscribing to MQTT topics...")
    mqtt_client.subscribe("Chat")
    mqtt_client.subscribe("Chat/#")
    mqtt_client.subscribe("RequestAdd2")
    mqtt_client.subscribe("RequestAdd2/#")
    mqtt_client.subscribe("#")
    logger.info("Subscribed to Chat/# and RequestAdd2/# and # (all topics)")

    logger.info("AI Chatbot is ready — add a bot address as a contact in Spixi and start chatting.")

def on_message(mqtt_client, userdata, msg):
    """Callback when a message is received"""
    logger.debug("MQTT message received on topic: %s", msg.topic)

    try:
        # Parse incoming message (tolerant decoding)
        payload = None
        try:
            payload = msg.payload.decode()
        except Exception:
            payload = str(msg.payload)

        logger.debug("Payload (first 200 chars): %s", payload[:200])
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
                logger.info("Auto-accepting contact: %s", sender)
                try:
                    resp = session.get(f"{QUIXI_API}/acceptContact", params={"address": sender}, timeout=REQUEST_TIMEOUT)
                    logger.info("Accept response: %s", resp.status_code)
                except Exception:
                    logger.exception("Error calling acceptContact for %s", sender)
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
                logger.warning("Missing sender or message in payload (sender=%s, message=%s)", sender, str(message)[:80])
                return

            message = message.strip()
            logger.info("Message from %s: %s", sender[:12], message[:160])
            
            # Check for commands first
            command_response = handle_command(sender, message)
            if command_response:
                send_message(sender, command_response)
                return
            
            # Show typing indicator (optional)
            logger.debug("Processing with AI...")
            
            # Get AI response
            ai_response = get_ai_response(sender, message)
            
            # Send response
            logger.info("Responding to %s (len=%d)", sender[:12], len(ai_response))
            send_message(sender, ai_response)
        else:
            logger.debug("Unhandled topic: %s", msg.topic)
    
    except json.JSONDecodeError as e:
        logger.error("JSON decode error: %s", e)
        logger.debug("Raw payload: %s", msg.payload)
    except Exception as e:
        logger.exception("Error processing message: %s", e)

def main():
    """Main bot loop"""
    logger.info("Starting Decentralized AI Chatbot")
    logger.info("QuIXI API: %s", QUIXI_API)
    logger.info("LM Studio: %s", LM_STUDIO_API)
    
    # Test LM Studio connection
    try:
        response = session.get(f"{LM_STUDIO_API}/models", timeout=REQUEST_TIMEOUT)
        logger.info("LM Studio connected")
    except Exception:
        logger.error("Cannot connect to LM Studio at %s. Make sure it's running!", LM_STUDIO_API)
        return
    
    # Test QuIXI connection
    try:
        response = session.get(f"{QUIXI_API}/myWallet", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            wallet_map = response.json().get("result", {})
            if isinstance(wallet_map, dict) and wallet_map:
                logger.info("QuIXI connected")
                addresses = list(wallet_map.keys())
                primary = addresses[0]
                logger.info("Primary bot address: %s", primary)
                if len(addresses) > 1:
                    logger.info("Additional addresses: %s", ", ".join(addresses[1:]))
                logger.info("Wallet balances:")
                for addr, balance in wallet_map.items():
                    logger.info("   %s: %s IXI", addr, balance)
                logger.info("Add one of these addresses as a contact in Spixi to start chatting!")
            else:
                logger.warning("QuIXI returned empty wallet data.")
        else:
            logger.warning("QuIXI returned status %s", response.status_code)
    except Exception as e:
        logger.error("Cannot connect to QuIXI (%s). Make sure it's running!", e)
        return
    
    # Connect to MQTT broker
    try:
        # Compatible with both paho-mqtt v1.x and v2.x
        from paho.mqtt import client as mqtt_module
        if hasattr(mqtt_module, 'CallbackAPIVersion'):
            mqtt_client = mqtt.Client(mqtt_module.CallbackAPIVersion.VERSION1)
        else:
            mqtt_client = mqtt.Client()
    except Exception:
        logger.warning("Could not detect MQTT client version; using default client")
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
    
    logger.info("Connecting to MQTT broker at %s:%s", MQTT_BROKER, MQTT_PORT)
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        logger.info("Connected to MQTT broker")
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down bot...")
        mqtt_client.disconnect()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
