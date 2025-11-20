# Decentralized AI Chatbot (Ixian + Local LLM)

This workspace contains a minimal scaffold to build a decentralized AI chatbot using QuIXI (Ixian gateway), a local LLM runner (LM Studio or Ollama), and an MQTT broker for internal message routing.

Files added:
- `ai_chatbot.py` — minimal scaffold that checks connectivity to LM Studio and QuIXI.
- `requirements.txt` — Python dependencies for the example.

Quick start (Windows PowerShell):

```powershell
# 1) Create a Python virtual environment (optional)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Install required packages
python -m pip install -r requirements.txt

# 3) Start LM Studio and download a model; enable Local Server (note the base URL)
# 4) Build/run QuIXI and configure ixian.cfg to bind APIs to localhost
# 5) Start an MQTT broker (mosquitto) or another broker accessible at localhost:1883

# 6) Run the scaffold (it performs connectivity checks and exits if services are missing)
python ai_chatbot.py
```

Next steps:
- Extend `ai_chatbot.py` to subscribe to MQTT `Chat/#` and `RequestAdd2/#` topics.
- Implement message handling, local LLM calls (OpenAI-compatible client pointing to LM Studio), and `sendChatMessage` requests to the QuIXI API.
- Add persistent memory (SQLite), RAG embedding support, and systemd/service files for production.

See the Ixian docs guide: https://ixian-platform.github.io/Ixian-Docs/docs/developers/howto/decentralized-ai-chatbot
