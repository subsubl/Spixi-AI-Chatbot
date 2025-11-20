GUIDE — QuIXI + Ixian Workspace

This guide provides step-by-step instructions for developers and integrators using this workspace. It covers building, running, the UI, common development tasks, and security considerations.

1) Quick links
- Entry point: `QuIXI/QuIXI/Program.cs`
- Node orchestration: `QuIXI/QuIXI/Meta/Node.cs`
- Config / CLI: `QuIXI/QuIXI/Meta/Config.cs` (use `Config.outputHelp()` at runtime to see flags)
- API: `QuIXI/QuIXI/API/APIServer.cs` and `Ixian-Core/API/GenericAPIServer.cs`
- Frontend: `html/gui/index.html`, `html/gui/main.js`, `html/gui/styles.css`

2) Build & run (Windows PowerShell)
- Build (Visual Studio recommended):

```powershell
msbuild .\QuIXI\QuIXI.sln /p:Configuration=Debug
# or
dotnet build .\QuIXI\QuIXI.sln
```

- Run QuIXI (adjust the path/TFM):

```powershell
& .\QuIXI\QuIXI\bin\Debug\net8.0\QuIXI.exe --config ixian.cfg --apiport 8001
```

- The API will listen on the configured port (default from `ixian.cfg`). The simple web GUI is available at `/gui` on the same host and port.

3) Frontend notes
- Location: `html/gui/`
- The GUI is a minimal SPA that uses JSON-RPC POSTs to `/` (root). It expects the API to accept POST bodies with `{ "method": "contacts", "params": { ... } }` and return the standard `{ result, error }` JSON shape.
- If you enable authentication (basic auth), update `html/gui/main.js` to send credentials or use a token proxy.

4) Development patterns & examples
- Add API route: follow existing patterns in `APIServer.cs` and register behavior in `GenericAPIServer` if the endpoint is generic.
- Add message queue driver: implement under `QuIXI/MQ/Drivers/*` and extend `Node.initMessageQueue()` switch.
- Wallet or crypto changes: the wallet code lives in `Ixian-Core/Wallet/*` and is used from `Node`.

5) Tests & manual verification
- No unit test suite exists in the repository. Use small, isolated manual tests:
  - Run QuIXI locally with `--networkType regtest` or `--testnet`.
  - Use `curl` or Postman to exercise API endpoints.
  - Open the GUI at `http://localhost:<apiport>/gui` to validate UI flows.

6) Security & repository housekeeping (important)
- Do NOT commit wallet files or private keys. These files are present in this workspace as examples/runtimes but must be excluded from source control.
- Add a `.gitignore` with at least the following lines and remove sensitive files from the repo history before publishing:

```
# wallet files
ixian.wal
*.wal
*.bak

# headers and runtime artifacts
headers/
__pycache__/
*.pyc

# local environment
.venv/
.env
```

- If `Ixian-Core/` and `QuIXI/` are full repositories, consider adding them as git submodules instead of committing their `.git` metadata into this repo. Example:

```powershell
# from repo root
git submodule add <Ixian-Core repo url> Ixian-Core
git submodule add <QuIXI repo url> QuIXI
```

7) Committing and pushing
- We keep a remote called `deploy` configured in this workspace. To commit and push a safe change manually:

```powershell
# stage only intended files
git add src/changed_file.cs html/gui/* .github/copilot-instructions.md
git commit -m "Short descriptive message"
git push deploy HEAD:master
```

- Avoid running `git add -A` or committing whole workspace without checking `.gitignore` first.

8) Common troubleshooting
- API server "Cannot initialize API server": check that the configured `apiport` isn't already in use and that the process can bind to the interface.
- Missing HTML resources: `GenericAPIServer` serves `html/` files. Ensure `html/gui/index.html` and assets exist and are readable by the running user.

9) Contributing
- Preferred flow: fork -> feature branch -> PR to `master` on this repo.
- Keep commits focused and avoid adding secrets. If you must add a configuration example, add `ixian.cfg.example` instead of real keys.

10) Need help?
- If you want, I can:
  - Add a `.gitignore` and remove sensitive files from history.
  - Convert `Ixian-Core` and `QuIXI` to submodules.
  - Expand the GUI (settings, better chat UI, auth support).


---
Guide created automatically by the workspace assistant. If you'd like adjustments (more examples, diagrams, or a troubleshooting checklist), tell me which sections to expand.
