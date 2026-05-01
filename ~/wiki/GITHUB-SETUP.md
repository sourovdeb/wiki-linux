# 🔑 GitHub Integration Setup Guide

## 🎯 Objective
Connect your local wiki to a GitHub repository for version control, backup, and collaboration.

## 📋 Prerequisites
- GitHub account
- SSH keys set up (or willingness to set them up)

## 🔧 Step 1: Set Up SSH Keys (if not already done)

### Check for existing SSH keys
```bash
ls -al ~/.ssh/
# Look for id_rsa and id_rsa.pub files
```

### Generate new SSH keys (if needed)
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter to accept default file location
# Enter a secure passphrase (optional but recommended)
```

### Add SSH key to SSH agent
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### Copy SSH public key
```bash
cat ~/.ssh/id_ed25519.pub
# Copy the output (starts with ssh-ed25519...)
```

### Add SSH key to GitHub
1. Go to GitHub → Settings → SSH and GPG keys
2. Click "New SSH key"
3. Paste your public key
4. Give it a title (e.g., "Wiki-Linux Laptop")
5. Click "Add SSH key"

## 🌐 Step 2: Create GitHub Repository

### Option A: Create new repository
1. Go to GitHub and click "+" → "New repository"
2. Name it: `wiki-arch` (or any name you prefer)
3. Description: "My personal wiki knowledge base"
4. Choose: **Private** (recommended) or Public
5. **Do NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

### Option B: Use existing repository
If you already have a repository, just note its SSH URL.

## 🔗 Step 3: Connect Local Wiki to GitHub

### Add remote to your local wiki
```bash
cd ~/wiki
git remote add origin git@github.com:yourusername/wiki-arch.git
# Replace "yourusername" with your GitHub username
```

### Verify the remote
```bash
git remote -v
# Should show:
# origin  git@github.com:yourusername/wiki-arch.git (fetch)
# origin  git@github.com:yourusername/wiki-arch.git (push)
```

## 📤 Step 4: Initial Push

### Set your git identity (if not already set)
```bash
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

### Push your wiki to GitHub
```bash
# Add all files
git add .

# Commit with initial message
git commit -m "Initial wiki setup"

# Push to GitHub
git push -u origin main
```

## 🔄 Step 5: Daily Workflow

### Pull latest changes (morning)
```bash
cd ~/wiki
git pull origin main
```

### Commit changes (evening)
```bash
git add .
git commit -m "Daily updates $(date +%Y-%m-%d)"
git push origin main
```

## 🛠️ Troubleshooting

### Permission denied (publickey)
```bash
# Test SSH connection to GitHub
ssh -T git@github.com

# If you get "Permission denied", your SSH key isn't set up correctly
# Go back to Step 1
```

### Remote already exists
```bash
# If you get an error about remote already existing
git remote remove origin
# Then add the correct remote
git remote add origin git@github.com:yourusername/wiki-arch.git
```

### Branch issues
```bash
# If you need to create main branch
git branch -M main

# If you need to switch to main
git checkout main
```

## 🎯 Best Practices

1. **Commit Often**: Small, frequent commits are better than large infrequent ones
2. **Meaningful Messages**: Write descriptive commit messages
3. **Pull Before Push**: Always pull latest changes before pushing
4. **Use Branches**: Create feature branches for major changes
5. **Ignore Sensitive Files**: Add patterns to `.gitignore` as needed

## 🔄 Advanced: Multiple Branches

### Create a development branch
```bash
git checkout -b development
# Make changes, commit them
git add .
git commit -m "New feature in development"
git push origin development
```

### Merge branches
```bash
git checkout main
git merge development
git push origin main
```

## ✅ Completion Checklist

- [ ] SSH keys generated and added to GitHub
- [ ] GitHub repository created (`wiki-arch`)
- [ ] Local wiki connected to GitHub remote
- [ ] Initial push completed
- [ ] Daily workflow tested (pull/commit/push)

Once complete, your wiki will be safely backed up to GitHub and accessible from anywhere!