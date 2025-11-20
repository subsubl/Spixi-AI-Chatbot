# Copilot instructions for QuIXI / Ixian-Core (concise)

This repo contains two cooperating parts:
- `QuIXI/` — application: node, API server, CLI (entry: `QuIXI/QuIXI/Program.cs`).
- `Ixian-Core/` — shared libraries: crypto, network, storage, config, and core constants.

Essentials for an AI coding agent (what to edit and where)
- Start: search `static void Main` → `QuIXI/QuIXI/Program.cs` then follow into `QuIXI/QuIXI/Meta/Node.cs` (`node.start()` / lifecycle).
- Config & CLI: `QuIXI/QuIXI/Meta/Config.cs` (`ixian.cfg` is canonical; use `Config.outputHelp()` to list flags).
- API endpoints: implement/extend in `QuIXI/QuIXI/API/APIServer.cs` and `QuIXI/QuIXI/API/GenericAPIServer.cs`.
- Message queue drivers: see `QuIXI/MQ/Drivers/*` and the `Node.initMessageQueue()` switch for adding drivers.
- Networking primitives: `Ixian-Core/Network/*` (`NetworkClientManager`, `NetworkQueue`, `CoreProtocolMessage`).

Project-specific conventions and gotchas
- One-class-per-file; namespaces: `QuIXI` (app) vs `IXICore` (core). Use PascalCase for types and methods.
- Config parsing is multi-pass in `Config.init(...)` — add CLI flags there to ensure consistent handling.
- Many subsystems rely on `Config.userFolder` (peers, headers, wallet). Tests should set a temp `userFolder`.
- Network code is threaded and stateful. Respect existing `lock(...)` usage when modifying shared state.

Build & run (Windows PowerShell)
- Open `QuIXI/QuIXI.sln` in Visual Studio (recommended) or build from shell:
  - `msbuild .\QuIXI\QuIXI.sln /p:Configuration=Debug`
  - or `dotnet build .\QuIXI\QuIXI.sln`
- Run the built exe from the output folder, e.g.:
  - `& .\QuIXI\QuIXI\bin\Debug\net8.0\QuIXI.exe --config ixian.cfg --apiport 8001`

Testing & safety
- No unit-test project detected. Validate changes manually: run with a small `ixian.cfg` and `--networkType regtest` or `--testnet` for isolated runs.

Common edit patterns (copy-paste examples)
- Add API route: copy pattern from `APIServer.cs` methods and register in `GenericAPIServer` routing.
- Add MQ driver: add driver class under `QuIXI/MQ/Drivers/` and update `Node.initMessageQueue()` switch.
- Wallet/key ops: change logic under `Ixian-Core/Wallet/*` (look for `WalletStorage`, `IxianHandler.getWalletStorage()`).

If something is missing or you want expanded examples (e.g., sample `ixian.cfg` snippets, run/debug steps), ask and I'll extend this file.
