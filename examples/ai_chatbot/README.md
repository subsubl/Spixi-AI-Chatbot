# Example: Decentralized AI Chatbot

This example shows a small Python-based chatbot that integrates with QuIXI (HTTP API), an MQTT broker (for Spixi messages), and a local LLM-compatible API (e.g. LM Studio using OpenAI-compatible endpoints).

Quick start (local, development):

Prerequisites:
- QuIXI running with API enabled on port `8001` (default in this repo's examples)
- An MQTT broker reachable at `localhost:1883` (e.g. mosquitto)
- A local LLM service compatible with the OpenAI Python client (LM Studio or similar) running at `http://localhost:1234`

Run locally with Python:

```powershell
# Create a virtualenv and install deps
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r examples/ai_chatbot/requirements.txt

# Start the bot
python examples/ai_chatbot/ai_chatbot.py
```

Run with Docker Compose (recommended for quick local integration):

```powershell
# from repository root
docker compose up --build
```

Notes:
- The bot uses a local OpenAI-compatible client; set `LM_STUDIO_API` in `ai_chatbot.py` if your model API is exposed on a different URL.
- The example will auto-accept contact requests and reply to messages. Use `/help` for built-in bot commands.
- For production usage, secure your MQTT broker and QuIXI API, and do not expose local LLM endpoints publicly.

If you want, I can add an environment-variable-driven config and a small test harness next.