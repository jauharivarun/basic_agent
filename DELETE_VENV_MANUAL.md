# How to Delete .venv Directory

The `.venv` directory is locked because Cursor or Python processes are using it. Here are solutions:

## Solution 1: Close Cursor and Delete Manually (Easiest)

1. **Close Cursor completely** (not just the window - check Task Manager)
2. **Open File Explorer** and navigate to: `C:\Users\vnjau\my_first_project`
3. **Right-click** on the `.venv` folder
4. **Select "Delete"**
5. If Windows asks to close processes, click "Yes"

## Solution 2: Use Task Manager

1. Press `Ctrl + Shift + Esc` to open Task Manager
2. Look for any **Python** processes
3. **End Task** for all Python processes
4. Try deleting `.venv` again

## Solution 3: Delete on Reboot

1. Run the `delete_venv.bat` script (as Administrator)
2. Restart your computer
3. The `.venv` folder will be deleted automatically on startup

## Solution 4: Use Command Prompt as Administrator

1. Close Cursor completely
2. Open **Command Prompt as Administrator**
3. Navigate to your project: `cd C:\Users\vnjau\my_first_project`
4. Run: `rmdir /s /q .venv`

## Solution 5: Use PowerShell (Run as Administrator)

```powershell
cd C:\Users\vnjau\my_first_project
Get-Process python* | Stop-Process -Force
Start-Sleep -Seconds 2
Remove-Item -Recurse -Force .venv
```

**Note:** The easiest method is Solution 1 - just close Cursor completely and delete via File Explorer.
