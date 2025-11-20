# Decentralized AI Chatbot (Ixian + Local LLM)
# QuIXI + Ixian Workspace — README

This repository contains the QuIXI application (QuIXI/) and the Ixian-Core libraries (Ixian-Core/), plus example scaffolding for a decentralized AI chatbot that integrates QuIXI with a local LLM and MQTT for message routing.

This README is a concise GitHub-facing entry explaining how to build, run, and develop with this workspace. A more detailed developer guide is in `GUIDE.md`.

Highlights
- QuIXI: node, API server, CLI — entry point: `QuIXI/QuIXI/Program.cs`.
- Ixian-Core: shared crypto, networking, storage, and streaming primitives.
- Example chatbot scaffold: `ai_chatbot.py` (connects to LM Studio and QuIXI), `requirements.txt`.
- Minimal web GUI served at `/gui` (files in `html/gui/`).

Quick start (Windows PowerShell)

1) Build QuIXI (Visual Studio recommended) or use dotnet/msbuild from shell:

```powershell
msbuild .\QuIXI\QuIXI.sln /p:Configuration=Debug
# or
dotnet build .\QuIXI\QuIXI.sln
```

2) Run the QuIXI executable (adjust the path/TFM):

```powershell
& .\QuIXI\QuIXI\bin\Debug\net8.0\QuIXI.exe --config ixian.cfg --apiport 8001
```

3) Open the GUI in your browser (served by the same API server):

	http://localhost:8001/gui

4) (Optional) Start the example chatbot scaffolding:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python ai_chatbot.py
```

Security & notes
- The workspace contains wallet files (`ixian.wal` and backups). Do NOT push wallet files or secrets to public repositories. Add them to `.gitignore` before committing.
- `Ixian-Core/` and `QuIXI/` are separate repositories in many setups; treating them as submodules is recommended if you want to track them as dependencies.
- The GUI is lightweight and calls the API via JSON-RPC POSTs to `/` (methods: `contacts`, `addContact`, `sendChatMessage`, `getLastMessages`, `status`). If your API uses authentication, the GUI must be updated to send auth headers.

Where to look next
- Entry point: search `static void Main` → `QuIXI/QuIXI/Program.cs`.
- Node orchestration: `QuIXI/QuIXI/Meta/Node.cs`.
- CLI & config: `QuIXI/QuIXI/Meta/Config.cs` (`Config.outputHelp()` shows flags).
- API endpoints: `QuIXI/QuIXI/API/APIServer.cs` and `Ixian-Core/API/GenericAPIServer.cs` (I added `/gui` support to serve `html/gui/`).

For detailed developer instructions (build, run, test, security hardening, .gitignore suggestions, and contribution rules) see `GUIDE.md`.
