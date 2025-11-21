<#
Update submodules to pinned SHAs recorded in scripts/pin_submodules.md.

This script is idempotent and intended for maintainers. It will:
- read the pinned SHAs from `scripts/pin_submodules.md` (simple parsing)
- update each submodule to the pinned SHA and commit the change in the superproject

WARNING: this script performs git operations and creates commits in the superproject.
Ensure you have a clean working tree and push changes after reviewing.
#>

Set-StrictMode -Version Latest

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$pinfile = Join-Path $root 'pin_submodules.md'

if (-not (Test-Path $pinfile)) {
    Write-Error "Pinned SHAs file not found: $pinfile"
    exit 1
}

$lines = Get-Content $pinfile | Where-Object { $_ -match 'Ixian-Core|QuIXI' }

foreach ($line in $lines) {
    if ($line -match 'Ixian-Core') {
        $sha = ($line -split ':')[1].Trim()
        Write-Host "Updating Ixian-Core -> $sha"
        Set-Location (Join-Path $root '..\Ixian-Core')
        git fetch
        git checkout $sha
        Set-Location $root
        git add Ixian-Core
    } elseif ($line -match 'QuIXI') {
        $sha = ($line -split ':')[1].Trim()
        Write-Host "Updating QuIXI -> $sha"
        Set-Location (Join-Path $root '..\QuIXI')
        git fetch
        git checkout $sha
        Set-Location $root
        git add QuIXI
    }
}

git commit -m "Pin submodules to recorded SHAs in scripts/pin_submodules.md" || Write-Host "No changes to commit"

Write-Host "Done. Review and push the commit if appropriate."
