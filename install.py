import os
import shutil
import sys
import subprocess
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if os.name == "nt":
    OS_TYPE = "Windows"
    
    if not is_admin():
        print("\n⚠ This script requires admin privileges. Restarting as administrator...\n")
        subprocess.run(["powershell", "Start-Process", "python", f'"{__file__}"', "-Verb", "RunAs"])
        sys.exit()
    SYSTEM_PATH = "C:\\Windows\\System32"
    SHORTCUT_CMD = os.path.join(SYSTEM_PATH, "filemg.bat")

elif "ANDROID_ROOT" in os.environ:
    OS_TYPE = "Termux"
    SYSTEM_PATH = os.environ["PREFIX"] + "/bin"
    SHORTCUT_CMD = os.path.join(SYSTEM_PATH, "filemg")

elif sys.platform.startswith("linux"):
    OS_TYPE = "Linux"
    SYSTEM_PATH = "/usr/local/bin"
    SHORTCUT_CMD = os.path.join(SYSTEM_PATH, "filemg")

else:
    print("\n❌ Unsupported OS! Exiting...")
    sys.exit(1)

print(f"\n🖥  Detected OS: {OS_TYPE}")

dest_path = os.path.join(SYSTEM_PATH, "FileMG.py")
print(f"\n🔄 Copying FileMG.py to {SYSTEM_PATH}...")
shutil.copy("FileMG.py", dest_path)
os.chmod(dest_path, 0o755)

print("\n🔗 Creating a Global Shortcut...")

if OS_TYPE == "Windows":
    with open(SHORTCUT_CMD, "w") as f:
        f.write(f'@echo off\npython "{dest_path}" %*\n')

elif OS_TYPE in ["Linux", "Termux"]:
    with open(SHORTCUT_CMD, "w") as f:
        f.write(f'#!/bin/sh\npython3 "{dest_path}" "$@"\n')
    os.chmod(SHORTCUT_CMD, 0o755)

print("\n✅ Installation Completed!")
print("\n💡 Now, you can run the tool globally by typing: filemg")