<#
Delete *local-backup/ directories under the repository (non-destructive prompt)
#>
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Scanning for *local-backup directories under $repoRoot"
$dirs = Get-ChildItem -Path $repoRoot -Recurse -Directory -Filter '*local-backup' -ErrorAction SilentlyContinue
if (-not $dirs) { Write-Host "No local-backup directories found."; exit 0 }

foreach ($d in $dirs) {
    Write-Host "Found: $($d.FullName)"
}

$confirm = Read-Host "Type 'DELETE' to remove these directories permanently"
if ($confirm -ne 'DELETE') { Write-Host "Aborted by user."; exit 1 }

foreach ($d in $dirs) {
    Write-Host "Removing: $($d.FullName)"
    Remove-Item -LiteralPath $d.FullName -Recurse -Force
}

Write-Host "Done. Remember to commit the deletion if desired." 
