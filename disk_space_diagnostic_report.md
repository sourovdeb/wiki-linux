# Disk Space Diagnostic Report - CRITICAL STATUS ⚠️

**Generated:** 2026-05-09 01:07 AM
**System:** Linux 6.19
**Total Disk Space:** 216GB
**Used Space:** 196GB (96%)
**Available Space:** 9.5GB (4%)
**Status:** DANGER - Only 4% free space remaining

## 🔍 Major Space Consumers Analysis

### 📁 Directory Breakdown (Top Consumers)

| Directory | Size | Percentage of Total | Description |
|-----------|------|---------------------|-------------|
| `/home/sourov` | 73GB | 33.8% | User home directory |
| `/var/lib` | 51GB | 23.6% | System libraries and data |
| `/home/sourov/wiki` | 28GB | 13.0% | Wiki project directory |
| `/home/sourov/.ollama` | 17GB | 7.9% | Ollama AI models |
| `/home/sourov/.local` | 7.2GB | 3.3% | Local user applications |
| `/home/sourov/.config` | 7.6GB | 3.5% | Configuration files |
| `/home/sourov/Documents` | 11GB | 5.1% | Documents directory |
| `/var/lib/wiki-linux` | 28GB | 13.0% | Wiki Linux system data |
| `/var/lib/ollama` | 8.1GB | 3.8% | System Ollama models |
| `/var/lib/containerd` | 6.7GB | 3.1% | Container runtime |

### 🗃️ Detailed Directory Analysis

#### 1. **Home Directory (`/home/sourov`) - 73GB**
- **`.ollama/models`**: 17GB - AI/ML model files
  - Large model files: 2.1GB, 4.1GB, 3.6GB, 2.2GB, 1.9GB, 4.4GB
- **`wiki`**: 28GB - Wiki project with Git repository
  - `.git/objects`: 14GB - Git version control data
  - `user/my_library`: 5.7GB - Large ZIP archives (1.9GB each × 3)
- **`.local/share/waydroid`**: Significant space (exact size unavailable due to permissions)
- **`.cache`**: 3.1GB - Application cache files
- **`.config`**: 7.6GB - Configuration files
- **`Documents`**: 11GB - Various documents

#### 2. **System Libraries (`/var/lib`) - 51GB**
- **`wiki-linux`**: 28GB - Wiki Linux system data
- **`ollama`**: 8.1GB - System-level Ollama models
- **`containerd`**: 6.7GB - Container runtime data
- **`systemd`**: 3.7GB - System service data

#### 3. **Large Individual Files Found**
| File Path | Size | Type |
|-----------|------|------|
| `/home/sourov/.ollama/models/blobs/sha256-b5374915da534cb93df39f03bd4f2cd5a0c533df0d5e21957dc9556c260be9eb` | 2.1GB | Ollama model |
| `/home/sourov/.ollama/models/blobs/sha256-f5074b1221da0f5a2910d33b642efa5b9eb58cfdddca1c79e16d7ad28aa2b31f` | 4.1GB | Ollama model |
| `/home/sourov/.ollama/models/blobs/sha256-3a43f93b78ec50f7c4e4dc8bd1cb3fff5a900e7d574c51a6f7495e48486e0dac` | 3.6GB | Ollama model |
| `/home/sourov/.ollama/models/blobs/sha256-46bb65206e0e2b00424f33985a5281bd21070617ebcfda9be86eb17e6e00f793-partial` | 2.2GB | Partial Ollama model |
| `/home/sourov/.ollama/models/blobs/sha256-dde5aa3fc5ffc17176b5e8bdc82f587b24b2678c6c66101bf7da77af9f7ccdff` | 1.9GB | Ollama model |
| `/home/sourov/.ollama/models/blobs/sha256-2bada8a7450677000f678be90653b85d364de7db25eb5ea54136ada5f3933730` | 4.4GB | Ollama model |
| `/home/sourov/wiki/user/my_library/KIDS-20260507T165308Z-3-001.zip` | 1.9GB | ZIP archive |
| `/home/sourov/wiki/user/my_library/2026 Trainees' Folder-20260507T165404Z-3-001.zip` | 1.9GB | ZIP archive |
| `/home/sourov/wiki/user/my_library/Resources for the course-20260507T165347Z-3-001.zip` | 1.9GB | ZIP archive |
| `/home/sourov/wiki/.git/objects/pack/pack-1c6856ac91b7184eac0c4ba281678cd82159902b.pack` | 5.5GB | Git pack file |

## 🚨 Critical Issues Identified

1. **Extremely Low Free Space**: Only 9.5GB (4%) available out of 216GB
2. **Large AI Model Files**: Ollama models consuming 17GB in home directory + 8.1GB in system
3. **Git Repository Bloat**: Wiki project Git repository is 14GB (likely contains large files in history)
4. **Large ZIP Archives**: Three 1.9GB ZIP files in wiki library
5. **Duplicate Data**: Potential duplication between `/home/sourov/wiki` and `/var/lib/wiki-linux`

## 💡 Recommendations for Immediate Action

### High Priority (Free up 20-30GB immediately)
1. **Clean up Ollama models**: Remove unused AI models or move to external storage
   ```bash
   # List all Ollama models
   ls -lh /home/sourov/.ollama/models/blobs/

   # Remove specific large models (example)
   rm /home/sourov/.ollama/models/blobs/sha256-46bb65206e0e2b00424f33985a5281bd21070617ebcfda9be86eb17e6e00f793-partial
   ```

2. **Compress or remove large ZIP archives**: The three 1.9GB ZIP files could be compressed further or moved
   ```bash
   # Check if archives can be recompressed
   gzip -9 /home/sourov/wiki/user/my_library/*.zip

   # Or move to external storage
   mv /home/sourov/wiki/user/my_library/*.zip /external-drive/backups/
   ```

3. **Git repository optimization**: Clean up Git history and remove large files
   ```bash
   cd /home/sourov/wiki
   git gc --aggressive
   git prune
   ```

### Medium Priority (Free up additional space)
1. **Clear application caches**: Clean up `.cache` directory (3.1GB)
   ```bash
   rm -rf /home/sourov/.cache/*
   ```

2. **Review Waydroid data**: Check if Android emulator data can be cleaned up

3. **Container cleanup**: Clean up unused container images
   ```bash
   sudo podman system prune -a
   sudo docker system prune -a  # if using Docker
   ```

### Long Term Solutions
1. **Add additional storage**: Consider adding external HDD/SSD
2. **Implement regular cleanup**: Set up automated cleanup scripts
3. **Monitor disk usage**: Install monitoring tools like `ncdu`
4. **Move large data to external storage**: Relocate media, models, and archives

## 📊 Space Recovery Potential

| Action | Potential Space Freed | Difficulty |
|--------|----------------------|------------|
| Remove unused Ollama models | 10-15GB | Easy |
| Compress/remove ZIP archives | 5.7GB | Easy |
| Git repository cleanup | 5-10GB | Medium |
| Clear application cache | 3.1GB | Easy |
| Container cleanup | 2-5GB | Easy |
| **Total Potential** | **25-40GB** | - |

## ⚠️ Warning
**The system is at critical risk of becoming unresponsive or crashing due to lack of free disk space.** Immediate action is required to free up at least 20-30GB of space to restore normal operation and prevent data corruption.

**Recommended immediate action:** Start with removing the partial Ollama model file (2.2GB) and the three large ZIP archives (5.7GB total) to quickly free up ~8GB, then proceed with other cleanup steps.