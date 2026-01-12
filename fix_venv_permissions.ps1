# Script to fix .venv permissions and unlock files
Write-Host "Fixing .venv permissions..." -ForegroundColor Yellow

# Stop any Python processes using the venv
Get-Process python*,pip* -ErrorAction SilentlyContinue | 
    Where-Object {$_.Path -like "*my_first_project*"} | 
    Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

# Take ownership of the directory
Write-Host "Taking ownership of .venv directory..." -ForegroundColor Cyan
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
cmd /c "takeown /f .venv /r /d y >nul 2>&1"

# Grant full control to current user
Write-Host "Granting permissions..." -ForegroundColor Cyan
$acl = Get-Acl .venv
$permission = $currentUser, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
$acl.SetAccessRule($accessRule)
Set-Acl .venv $acl

# Try to remove read-only attributes
Write-Host "Removing read-only attributes..." -ForegroundColor Cyan
Get-ChildItem .venv -Recurse -Force -ErrorAction SilentlyContinue | 
    ForEach-Object { $_.Attributes = $_.Attributes -band (-bnot [System.IO.FileAttributes]::ReadOnly) }

Write-Host "`nDone! You can now try:" -ForegroundColor Green
Write-Host "  1. Delete .venv: Remove-Item -Recurse -Force .venv" -ForegroundColor White
Write-Host "  2. Or retry package installation" -ForegroundColor White
