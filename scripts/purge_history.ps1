<#
Script: purge_history.ps1

This helper documents and automates (to an extent) the recommended steps to purge sensitive files
from the repository history. It does NOT automatically run the destructive rewrite without explicit
confirmation from the user.

WARNING: Rewriting history is destructive. You must coordinate with collaborators and be prepared
to force-push and have everyone re-clone or reset their local repositories.

Options covered: `git filter-repo` (recommended) and `BFG Repo-Cleaner`.

Usage: Run this script in PowerShell as an administrator and follow the prompts.
#>

param(
    [switch]$RunNow
)

function Confirm-Purge {
    Write-Host "This operation will permanently remove specified files from ALL commits in the repository." -ForegroundColor Yellow
    Write-Host "Make a backup clone before proceeding. Example:" -ForegroundColor Cyan
    Write-Host "  git clone --mirror <repo_url> backup-repo.git" -ForegroundColor Green
    $ok = Read-Host "Do you want to continue? Type 'YES' to proceed"
    return $ok -eq 'YES'
}

Write-Host "Purge helper for removing sensitive files from git history" -ForegroundColor Green

Write-Host "Recommended tool: git-filter-repo (fast, maintained)." -ForegroundColor Cyan
Write-Host "If you prefer BFG (Java), install it separately and follow its docs." -ForegroundColor Cyan

if (-not $RunNow) {
    Write-Host "Dry-run mode. To perform the purge, re-run with -RunNow" -ForegroundColor Yellow
}

$patterns = @('ixian.wal', '*.wal', '*.wal.*', '*.bak', 'ixian.wal*', '*.wallet', '*.keystore', 'wallet.dat')

Write-Host "Files/patterns to remove:" -ForegroundColor Cyan
$patterns | ForEach-Object { Write-Host " - $_" }

if (-not $RunNow) { return }

if (-not (Confirm-Purge)) { Write-Host "Aborted by user"; exit 1 }

# Ensure git-filter-repo is available
try {
    git filter-repo --version > $null 2>&1
    $hasFilterRepo = $true
} catch {
    $hasFilterRepo = $false
}

if (-not $hasFilterRepo) {
    Write-Host "git-filter-repo not found. Installing via pip..." -ForegroundColor Yellow
    python -m pip install --user git-filter-repo
}

Write-Host "Running git-filter-repo to remove patterns..." -ForegroundColor Green

# Build the --invert-paths args for patterns
$tempArgs = @()
foreach ($p in $patterns) { $tempArgs += "--path-glob"; $tempArgs += $p }

# Example invocation (this is run in the repository root)
Write-Host "Executing: git filter-repo --invert-paths --force --paths-glob <patterns>" -ForegroundColor Cyan

# Note: We run filter-repo in place; we strongly recommend doing this on a mirror clone
try {
    git filter-repo --invert-paths --force @($tempArgs)
    Write-Host "Filter completed. You must now force-push the cleaned refs to the remote." -ForegroundColor Green
    Write-Host "Example: git push --force origin --all; git push --force origin --tags" -ForegroundColor Yellow
} catch {
    Write-Error "git-filter-repo failed: $_"
    exit 1
}

Write-Host "Purge complete. Notify collaborators to re-clone the repository." -ForegroundColor Green
