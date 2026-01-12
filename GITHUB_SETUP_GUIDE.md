# Step-by-Step Guide: Push Your Project to GitHub

## Prerequisites

### Step 1: Install Git (if not already installed)

1. **Download Git for Windows:**
   - Visit: https://git-scm.com/download/win
   - Download the installer
   - Run the installer and follow the installation wizard
   - **Important:** During installation, choose "Git from the command line and also from 3rd-party software" when prompted

2. **Verify Installation:**
   - Open a new PowerShell or Command Prompt window
   - Run: `git --version`
   - You should see something like: `git version 2.x.x`

### Step 2: Configure Git (First Time Setup)

Open PowerShell or Command Prompt and run:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Replace with your actual name and email address.

---

## Push Your Project to GitHub

### Step 3: Initialize Git Repository

1. Open PowerShell or Command Prompt
2. Navigate to your project directory:
   ```powershell
   cd c:\Users\vnjau\my_first_project
   ```

3. Initialize Git:
   ```powershell
   git init
   ```

### Step 4: Create a GitHub Repository

1. **Go to GitHub:**
   - Visit: https://github.com
   - Sign in (or create an account if you don't have one)

2. **Create a New Repository:**
   - Click the "+" icon in the top right corner
   - Select "New repository"
   - Enter a repository name (e.g., "my_first_project")
   - Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (since you already have files)
   - Click "Create repository"

3. **Copy the repository URL:**
   - After creating, GitHub will show you a page with instructions
   - Copy the HTTPS URL (looks like: `https://github.com/yourusername/my_first_project.git`)

### Step 5: Add Files to Git

1. **Add all files:**
   ```powershell
   git add .
   ```

2. **Check what will be committed:**
   ```powershell
   git status
   ```

### Step 6: Create Your First Commit

```powershell
git commit -m "Initial commit"
```

### Step 7: Connect to GitHub and Push

1. **Add the remote repository:**
   ```powershell
   git remote add origin https://github.com/yourusername/my_first_project.git
   ```
   *(Replace with your actual repository URL)*

2. **Rename the default branch to main (if needed):**
   ```powershell
   git branch -M main
   ```

3. **Push your code:**
   ```powershell
   git push -u origin main
   ```

4. **Enter your credentials:**
   - Username: Your GitHub username
   - Password: You'll need a **Personal Access Token** (not your GitHub password)
   
   **To create a Personal Access Token:**
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Give it a name (e.g., "My Project")
   - Select scopes: Check "repo" (this gives full control of private repositories)
   - Click "Generate token"
   - **Copy the token immediately** (you won't see it again!)
   - Use this token as your password when pushing

---

## Quick Reference Commands

```powershell
# Navigate to project
cd c:\Users\vnjau\my_first_project

# Initialize Git
git init

# Add all files
git add .

# Commit changes
git commit -m "Your commit message"

# Add remote (first time only)
git remote add origin https://github.com/yourusername/repo-name.git

# Push to GitHub
git push -u origin main
```

---

## Future Updates

After the initial push, to update your GitHub repository:

```powershell
git add .
git commit -m "Description of changes"
git push
```

---

## Troubleshooting

### If you get "fatal: not a git repository"
- Make sure you're in the project directory
- Run `git init` first

### If you get authentication errors
- Make sure you're using a Personal Access Token, not your password
- Check that the token has "repo" permissions

### If you need to change the remote URL
```powershell
git remote set-url origin https://github.com/yourusername/new-repo-name.git
```

### If you want to see your remote
```powershell
git remote -v
```

---

## Notes

- Your `.gitignore` file is already set up to exclude sensitive files like `config.json` and virtual environments
- Make sure `config.json` contains no sensitive data before pushing (it's already in `.gitignore`)
- The `venv/` folder will not be pushed (it's in `.gitignore`)
