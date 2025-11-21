# GUIDE: Next actions and safe defaults

This file lists immediate, safe, non-destructive changes applied and recommended next steps.

Changes applied in this pass:
- Added `ixian.cfg.example` with regtest-safe defaults.
- Expanded `.gitignore` to include more wallet and env patterns.
- Added `scripts/pin_submodules.md` documenting current submodule SHAs.
- Added `scripts/update-submodules.ps1` to help pin/update submodules.
- Added `scripts/purge_history.ps1` to guide safe removal of secrets from git history.

Recommended next steps (priority order):
1. Review `scripts/purge_history.ps1`, make a mirror backup, and run the purge if you want to remove wallets from history.
2. Add `ixian.cfg.example` to CI and tests so they use a safe config in automated runs.
3. Consider enabling dependabot and secret scanning in repository settings.
