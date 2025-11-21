# Example: Decentralized AI Chatbot

This example shows a small Python-based chatbot that integrates with QuIXI (HTTP API), an MQTT broker (for Spixi messages), and a local LLM-compatible API (e.g. LM Studio using OpenAI-compatible endpoints).

Quick start (local, development):

Prerequisites:
- QuIXI running with API enabled on port `8001` (default in this repo's examples)
- An MQTT broker reachable at `localhost:1883` (e.g. mosquitto)
- A local LLM service compatible with the OpenAI Python client (LM Studio or similar) running at `http://localhost:1234`

Configuration (environment variables)
------------------------------------
The example is configurable via environment variables. Copy `examples/ai_chatbot/.env.example` to `.env` or export the variables in your shell. Important variables:

- `QUIXI_API`: QuIXI HTTP API base URL (default: `http://localhost:8001`)
- `LM_STUDIO_API`: Local LLM base URL (default: `http://localhost:1234/v1`)
- `MQTT_BROKER` / `MQTT_PORT`: MQTT broker host and port (defaults: `localhost:1883`)
- `REQUEST_TIMEOUT`: HTTP request timeout in seconds (default: `10`)
- `LOG_LEVEL`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- `LM_API_KEY`, `LM_MODEL`, `LM_TEMPERATURE`, `LM_MAX_TOKENS`: Local LLM parameters
- `AUTO_ACCEPT_CONTACTS`: `true` or `false` (default: `true` in the example)

Run locally with Python:

```powershell
# Create a virtualenv and install deps
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r examples/ai_chatbot/requirements.txt

# Copy example env and start the bot
copy examples\ai_chatbot\.env.example .env
python examples/ai_chatbot/ai_chatbot.py
```

Run with Docker Compose (recommended for quick local integration):

```powershell
# from repository root
docker compose up --build
```

Notes and safety
----------------
- The bot can auto-accept incoming contact requests. For production, set `AUTO_ACCEPT_CONTACTS=false` or implement a whitelist. Auto-accepting contacts may expose the bot to unsolicited messages.
- The example uses environment variables to avoid hard-coded endpoints and secrets. Do not commit real API keys or wallet files.
- For debugging, set `LOG_LEVEL=DEBUG` to get more verbose logs.

If you want, I can add a small test harness (pytest) for message parsing and command handling, or add a Docker `HEALTHCHECK` for the chatbot container.