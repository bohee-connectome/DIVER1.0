# Server & Environment Guide

Comprehensive guide for working with Lab Server (Connectome), NERSC Perlmutter, and local PowerShell/Git Bash.

---

## 📋 Table of Contents

1. [Lab Server (Connectome)](#1-lab-server-connectome)
2. [NERSC Perlmutter](#2-nersc-perlmutter)
3. [PowerShell / Git Bash](#3-powershell--git-bash)
4. [Common Workflows](#4-common-workflows)

---

## 1. Lab Server (Connectome)

### Connection

```bash
# SSH connection
ssh bohee@147.47.200.154

# SCP file transfer
scp local_file.py bohee@147.47.200.154:/storage/connectome/bohee/path/

# RSYNC (recommended for large files)
rsync -avz --progress local_folder/ bohee@147.47.200.154:/storage/connectome/bohee/
```

### Storage Locations

```bash
# User home
/home/bohee/

# Data storage
/storage/connectome/bohee/

# Shared data
/storage/connectome/DIVER/
```

### Common Commands

**Check disk usage**:
```bash
df -h /storage/connectome/bohee
du -sh /storage/connectome/bohee/*
```

**Check GPU usage**:
```bash
nvidia-smi
watch -n 1 nvidia-smi  # Real-time monitoring
```

**Check running processes**:
```bash
ps aux | grep bohee
top -u bohee
htop -u bohee
```

**Background job management**:
```bash
# Run in background
nohup python script.py > log.txt 2>&1 &

# Check background jobs
jobs
ps aux | grep python

# Kill job
kill PID
pkill -f script_name.py
```

### Environment Management

**Conda environments**:
```bash
# List environments
conda env list

# Create environment
conda create -n myenv python=3.9
conda activate myenv

# Install packages
pip install package_name
conda install package_name
```

---

## 2. NERSC Perlmutter

### 2.1 Connection & Authentication

**Initial connection**:
```bash
ssh boheelee@perlmutter-p1.nersc.gov
```

**Multi-factor authentication**:
- Password + one-time token (e.g., from mobile app)
- Or use SSH keys for convenience

**Internal node navigation**:
```bash
# From perlmutter login node to specific login node
ssh login18

# From any node back to home
exit
```

### 2.2 Storage System

**Storage types**:

| Location | Path | Purpose | Backup | Purge |
|----------|------|---------|--------|-------|
| **HOME** | `/global/homes/b/boheelee/` | Scripts, configs | Yes | No |
| **CFS** | `/global/cfs/cdirs/m4750/` | Raw data, permanent storage | Yes | No |
| **SCRATCH** | `/pscratch/sd/b/boheelee/` | Fast I/O, processing | No | 12 weeks |

**Check quota**:
```bash
# Check all quotas
myquota

# Check specific filesystem
df -h /global/homes/b/boheelee
df -h /pscratch/sd/b/boheelee
```

**Disk usage**:
```bash
# Check usage
du -sh /pscratch/sd/b/boheelee/*
du -sh /global/cfs/cdirs/m4750/DIVER/*

# Find large files
find /pscratch/sd/b/boheelee -type f -size +1G -exec ls -lh {} \;
```

### 2.3 Compute Resources

**SLURM job system**:

**Check allocation**:
```bash
sshare -u boheelee
sacctmgr show associations user=boheelee
```

**Interactive session** (if node hours available):
```bash
# Request compute node
salloc -N 1 -C cpu -q interactive -t 04:00:00

# GPU node
salloc -N 1 -C gpu -q interactive -t 01:00:00 --gpus=1

# Check job queue
squeue -u boheelee

# Cancel job
scancel JOB_ID
```

**Batch job** (if node hours available):
```bash
# Submit batch script
sbatch job_script.sh

# Check status
squeue -u boheelee

# Job history
sacct -u boheelee
```

### 2.4 Login Node Usage (No Node Hours)

**When allocation is depleted**, use login nodes for **lightweight tasks only**:

✅ **Allowed**:
- Compiling code
- Short preprocessing (< 30 min)
- File management
- Testing scripts

❌ **Not allowed**:
- Long-running computations (> 30 min)
- Heavy CPU/memory usage
- Production runs

**Find best login node**:
```bash
# Check all login nodes
for i in {01..20}; do
  printf "login%02d: " $i
  ssh login$(printf "%02d" $i) "cat /proc/loadavg 2>/dev/null | cut -d' ' -f1-3" 2>/dev/null || echo "N/A"
done | grep -v N/A | sort -k2 -n | head -5

# Output example:
# login18: 1.39 1.90 2.13  ← Best (lowest load)
# login13: 1.42 1.66 1.94
# login03: 1.55 1.99 2.68
```

**Connect to specific login node**:
```bash
# Method 1: From another login node
ssh login18

# Method 2: From local (if configured)
ssh boheelee@login18.perlmutter.nersc.gov
```

**Monitor system load**:
```bash
# Current load
uptime
# Example: load average: 1.39, 1.90, 2.13

# Real-time CPU/memory
top
top -u boheelee  # Your processes only

# Memory status
free -h
```

**Load average guidelines**:
- < 5: Excellent
- 5-10: Good
- 10-20: Moderate
- 20+: Busy (avoid if possible)

**Background processing**:
```bash
# Run in background
nohup python script.py > log.txt 2>&1 &
echo $!  # Remember PID

# Monitor log
tail -f log.txt

# Check if still running
ps aux | grep script.py
pgrep -a python | grep script

# Check from anywhere
ps -u boheelee -f | grep python
```

**Process limits**:
```bash
# Check your process count
ps -u boheelee | wc -l

# Check CPU usage
top -u boheelee

# Nice your process (lower priority)
renice +10 -p PID
```

### 2.5 Environment & Modules

**Module system**:
```bash
# List available modules
module avail

# Load conda
module load conda

# List loaded modules
module list

# Unload module
module unload conda
```

**Conda environments**:
```bash
# Location options
# 1. In HOME (limited space but backed up)
conda create -n myenv python=3.9

# 2. In SCRATCH (more space but purged)
conda create -p /pscratch/sd/b/boheelee/DIVER/envs/myenv python=3.9

# List environments
conda env list

# Activate by path
conda activate /pscratch/sd/b/boheelee/DIVER/envs/myenv

# Activate by name (if in default location)
conda activate myenv
```

### 2.6 File Transfer

**To Perlmutter**:
```bash
# SCP (simple)
scp local_file.py boheelee@perlmutter-p1.nersc.gov:/pscratch/sd/b/boheelee/

# RSYNC (recommended - resumable)
rsync -avz --progress local_folder/ \
  boheelee@perlmutter-p1.nersc.gov:/pscratch/sd/b/boheelee/destination/
```

**From Perlmutter**:
```bash
# SCP
scp boheelee@perlmutter-p1.nersc.gov:/pscratch/sd/b/boheelee/file.txt ./

# RSYNC (recommended for large files)
rsync -avz --progress \
  boheelee@perlmutter-p1.nersc.gov:/pscratch/sd/b/boheelee/data/ \
  /d/local_destination/
```

**Globus** (for very large transfers):
```bash
# Setup at nersc.gov/users/data-transfer
# Endpoint: NERSC Perlmutter
# Path: /pscratch/sd/b/boheelee/
```

### 2.7 Troubleshooting

**SSH connection issues**:
```bash
# Check SSH config
cat ~/.ssh/config

# Test connection
ssh -v boheelee@perlmutter-p1.nersc.gov

# Re-authenticate
# Visit: nim.nersc.gov
```

**Storage full**:
```bash
# Find what's using space
du -sh /pscratch/sd/b/boheelee/* | sort -h

# Clean old files
find /pscratch/sd/b/boheelee -type f -mtime +90  # Files older than 90 days

# SCRATCH auto-purge: Files untouched for 12 weeks are deleted
```

**Permission denied**:
```bash
# Check file permissions
ls -l file.txt

# Fix permissions
chmod 644 file.txt  # rw-r--r--
chmod 755 script.py  # rwxr-xr-x
```

**Process killed (OOM)**:
```bash
# Use compute node instead of login node
salloc -N 1 -C cpu -q interactive -t 04:00:00

# Or reduce memory usage
# - Process files in batches
# - Use generators instead of loading all data
# - Clear variables: del large_array
```

---

## 3. PowerShell / Git Bash

### 3.1 Basic Commands

**Navigation**:
```powershell
# Change directory
cd C:\Users\user\DIVER1.0-AD
cd /c/Users/user/DIVER1.0-AD  # Git Bash style

# List files
ls
ls -la  # Detailed
dir  # PowerShell alternative

# Current directory
pwd
```

**File operations**:
```powershell
# Copy
cp source.txt destination.txt
Copy-Item source.txt destination.txt  # PowerShell

# Move
mv old.txt new.txt
Move-Item old.txt new.txt  # PowerShell

# Remove
rm file.txt
Remove-Item file.txt  # PowerShell
```

### 3.2 SSH from PowerShell

**Basic connection**:
```powershell
# To NERSC
ssh boheelee@perlmutter-p1.nersc.gov

# To Lab Server
ssh bohee@147.47.200.154

# With specific port
ssh -p 22 user@server
```

**SSH keys** (avoid typing password):
```powershell
# Generate key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy to server
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh user@server "cat >> ~/.ssh/authorized_keys"

# Or use ssh-copy-id (Git Bash)
ssh-copy-id user@server
```

**SSH config**:
```powershell
# Edit config
notepad $env:USERPROFILE\.ssh\config

# Example config:
Host perlmutter
    HostName perlmutter-p1.nersc.gov
    User boheelee

Host lab
    HostName 147.47.200.154
    User bohee

# Then connect with:
ssh perlmutter
ssh lab
```

### 3.3 File Transfer from PowerShell

**SCP**:
```powershell
# Upload to NERSC
scp C:\Users\user\file.py boheelee@perlmutter-p1.nersc.gov:/pscratch/sd/b/boheelee/

# Download from NERSC
scp boheelee@perlmutter-p1.nersc.gov:/pscratch/sd/b/boheelee/file.txt C:\Users\user\

# Recursive copy
scp -r C:\Users\user\folder boheelee@perlmutter-p1.nersc.gov:/pscratch/sd/b/boheelee/
```

**RSYNC** (Git Bash only):
```bash
# Upload
rsync -avz --progress /c/Users/user/folder/ \
  boheelee@perlmutter-p1.nersc.gov:/pscratch/sd/b/boheelee/folder/

# Download
rsync -avz --progress \
  boheelee@perlmutter-p1.nersc.gov:/pscratch/sd/b/boheelee/data/ \
  /d/local_destination/

# Advantages:
# - Resumable if interrupted
# - Only transfers changed files
# - Progress display
# - Preserves permissions
```

### 3.4 Python Environment (Local)

**Conda**:
```powershell
# List environments
conda env list

# Create environment
conda create -n myenv python=3.9
conda activate myenv

# Install from requirements
pip install -r requirements.txt
```

**Jupyter**:
```powershell
# Install
pip install jupyter notebook

# Start notebook
jupyter notebook

# Start lab
jupyter lab
```

### 3.5 Git Operations

**Basic workflow**:
```powershell
# Clone repository
git clone https://github.com/user/repo.git

# Check status
git status

# Add files
git add file.py
git add .  # All files

# Commit
git commit -m "Update preprocessing script"

# Push
git push origin main

# Pull
git pull origin main
```

**Branch management**:
```powershell
# Create branch
git branch feature-name
git checkout -b feature-name  # Create and switch

# Switch branch
git checkout main

# Merge
git checkout main
git merge feature-name

# Delete branch
git branch -d feature-name
```

### 3.6 Useful Aliases

**PowerShell profile**:
```powershell
# Edit profile
notepad $PROFILE

# Add aliases:
function perm { ssh boheelee@perlmutter-p1.nersc.gov }
function lab { ssh bohee@147.47.200.154 }
function cdproj { cd C:\Users\user\DIVER1.0-AD }

# Reload profile
. $PROFILE
```

**Git Bash aliases**:
```bash
# Edit ~/.bashrc
nano ~/.bashrc

# Add aliases:
alias perm='ssh boheelee@perlmutter-p1.nersc.gov'
alias lab='ssh bohee@147.47.200.154'
alias cdproj='cd /c/Users/user/DIVER1.0-AD'

# Reload
source ~/.bashrc
```

---

## 4. Common Workflows

### 4.1 Data Processing Workflow

**1. Local development**:
```powershell
# Edit scripts locally
code C:\Users\user\DIVER1.0-AD\scripts\preprocessing.py

# Test with small sample
python preprocessing.py --test
```

**2. Upload to Perlmutter**:
```powershell
scp C:\Users\user\DIVER1.0-AD\scripts\preprocessing.py \
  boheelee@perlmutter-p1.nersc.gov:/pscratch/sd/b/boheelee/scripts/
```

**3. Run on Perlmutter**:
```bash
ssh boheelee@perlmutter-p1.nersc.gov
ssh login18  # Find low-load node first

conda activate myenv
cd /pscratch/sd/b/boheelee/
nohup python scripts/preprocessing.py > logs/run.log 2>&1 &
```

**4. Monitor progress**:
```bash
tail -f logs/run.log

# Or from local (Git Bash):
ssh boheelee@perlmutter-p1.nersc.gov "tail -f /pscratch/sd/b/boheelee/logs/run.log"
```

**5. Download results**:
```bash
# From local
rsync -avz --progress \
  boheelee@perlmutter-p1.nersc.gov:/pscratch/sd/b/boheelee/output/ \
  /d/results/
```

### 4.2 Conda Environment Sync

**Export from Perlmutter**:
```bash
conda activate myenv
conda env export > environment.yml

# Or just requirements
pip list --format=freeze > requirements.txt
```

**Download and recreate locally**:
```powershell
scp boheelee@perlmutter-p1.nersc.gov:~/environment.yml .

conda env create -f environment.yml
# Or
pip install -r requirements.txt
```

### 4.3 Code-Data Separation

**Best practice**:
- **Code**: Version controlled (Git), in HOME
- **Data**: In CFS (permanent) or SCRATCH (processing)
- **Results**: In SCRATCH, then download important results

```bash
# Directory structure
/global/homes/b/boheelee/
  ├── scripts/           # Code (Git repo)
  └── configs/           # Config files

/global/cfs/cdirs/m4750/DIVER/
  └── raw_data/          # Raw datasets (permanent)

/pscratch/sd/b/boheelee/DIVER/
  ├── preprocessing/     # Processing workspace
  ├── lmdb_output/       # Processed data
  └── logs/              # Log files
```

### 4.4 Long-Running Jobs

**Start**:
```bash
# With nohup
nohup python script.py > log.txt 2>&1 &
PID=$!
echo $PID > script.pid

# Or with screen (if available)
screen -S job_name
python script.py
# Ctrl+A, D to detach

# Or with tmux
tmux new -s job_name
python script.py
# Ctrl+B, D to detach
```

**Monitor**:
```bash
# Check if running
ps -p $(cat script.pid)

# Reconnect to screen
screen -r job_name

# Reconnect to tmux
tmux attach -t job_name

# Check log
tail -f log.txt
```

**Stop**:
```bash
# Graceful stop (Ctrl+C simulation)
kill -INT $(cat script.pid)

# Force kill
kill -9 $(cat script.pid)
```

---

## 📚 Quick Reference

### Most Used Commands

**NERSC Login Node Selection**:
```bash
for i in {01..20}; do printf "login%02d: " $i; ssh login$(printf "%02d" $i) "cat /proc/loadavg | cut -d' ' -f1" 2>/dev/null; done | sort -k2 -n | head -5
```

**Background Job**:
```bash
nohup python script.py > log.txt 2>&1 &
```

**File Transfer**:
```bash
rsync -avz --progress local/ user@server:remote/
```

**Disk Usage**:
```bash
du -sh * | sort -h
```

**Process Monitoring**:
```bash
ps aux | grep user
top -u user
```

---

**Last Updated**: 2025-11-19
**Maintained by**: Bohee Lee
