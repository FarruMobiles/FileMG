import os
import subprocess
import platform
import sys
import shutil

def is_wsl():
    try:
        release_info = platform.uname().release.lower()
        return "microsoft" in release_info
    except:
        return False

def activate_venv():
    if sys.prefix != sys.base_prefix:
        return
    venv_path = os.path.join(os.getcwd(), "venv")
    if os.name == "nt":
        activate_script = os.path.join(venv_path, "Scripts", "activate")
    else:
        activate_script = os.path.join(venv_path, "bin", "activate")
    if os.path.exists(venv_path) and os.path.exists(activate_script):
        if os.name == "nt":
            os.system(f"{activate_script} && python {' '.join(sys.argv)}")
        else:
            os.system(f"source {activate_script} && python3 {' '.join(sys.argv)}")
        sys.exit()

def convert_to_adb_path(local_file):
    if not isinstance(local_file, str):
        return None
    local_file = local_file.replace("\\", "/")
    if is_wsl():
        if "C:/" in local_file or "c:/" in local_file:
            drive, path = local_file.split(":/", 1)
            local_file = f"/mnt/{drive.lower()}/{path}"
    if is_wsl():
        result = subprocess.run(["ls", local_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return None
    if not os.path.exists(local_file):
        return None

    return local_file

message = ""

class ADBFileManager:
    def __init__(self):
        activate_venv()
        self.current_path = "/sdcard/"
        self.history = []
        self.adb_command = self.detect_adb_environment()
    
    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def detect_adb_environment(self):
        termux_adb_path = "/data/data/com.termux/files/usr/bin/adb"
        if os.path.exists(termux_adb_path):
            return [termux_adb_path, "shell"]
        if shutil.which("adb"):
            return ["adb", "shell"]
        raise EnvironmentError("❌ ADB not found! Install ADB before using this tool.")

    def run_adb(self, command):
        result = subprocess.run(self.adb_command + command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()

    def refresh_files(self):
        output = self.run_adb(["ls", "-p", self.current_path])
        print(f"\n📂 CONTENTS OF {self.current_path}:\n")
        if output and "No such file or directory" not in output:
            files = output.split("\n")
            for file in files:
                if file.endswith("/"):
                    print(f"📁 {file}")
                else:
                    print(f"📄 {file}")
            print(f"\n")
        else:
            print("ℹ️ This Folder is Empty.")

    def change_directory(self, folder_name):
        if folder_name == "..":
            if len(self.history) > 0:
                self.current_path = self.history.pop()
        else:
            new_path = os.path.join(self.current_path, folder_name).replace("//", "/")
            if new_path.endswith("/"):
                self.history.append(self.current_path)
                self.current_path = new_path

    def copy_file_to_pc(self, filename, destination):
        global message
        file_path = os.path.join(self.current_path, filename).replace("\\", "/")
        subprocess.run(["adb", "pull", file_path, destination])
        message = f"\n✅ {filename} Copied To {destination} Successfully."

    def push_file_to_device(self, local_file, remote_path="/sdcard/"):
        global message
        if not isinstance(local_file, str):
            return
        adb_path = convert_to_adb_path(local_file)
        adb_pathh = os.path.basename(adb_path)
        if not adb_path:
            return  
        if is_wsl():
            local_file = adb_path
        if not os.path.exists(local_file):
            return
        subprocess.run(["adb", "push", adb_path, remote_path])
        message = f"\n✅ {adb_pathh} Uploaded To {remote_path} Successfully."

    def rename_file(self, old_name, new_name):
        global message
        old_path = os.path.join(self.current_path, old_name).replace("\\", "/")
        new_path = os.path.join(self.current_path, new_name).replace("\\", "/")
        self.run_adb(["mv", old_path, new_path])
        message = f"\n✅ {old_name} Renamed To {new_name} Successfully."

    def delete_file(self, filename):
        global message
        file_path = os.path.join(self.current_path, filename).replace("\\", "/")
        confirm = input(f"\n⚠  Are you sure you want to delete {filename}? (y/n): ")
        if confirm.lower() == 'y':
            self.run_adb(["rm", "-r", file_path])
            message = f"\n🗑  {filename} Deleted Successfully."

    def show_menu(self):
        print("\nDeveloped by: FarruMobiles")
        print("----------------------------")
        print("Ultimate ADB File Manager")
        print("----------------------------\n")
        print("1️⃣  REFRESH FILES")
        print("2️⃣  OPEN FOLDER")
        print("3️⃣  GO BACK")
        print("4️⃣  COPY FILE")
        print("5️⃣  UPLOAD FILE")
        print("6️⃣  RENAME FILE")
        print("7️⃣  DELETE FILE")
        print("8️⃣  EXIT")

    def start(self):
        while True:
            self.show_menu()
            
            if platform.system() == "Windows" or os.path.exists("/data/data/com.termux/files/usr/bin/adb"):
                import keyboard
                print("\nENTER OPTION: ", end="", flush=True)
                event = keyboard.read_event(suppress=True)
                while event.event_type != "down" or event.name not in "12345678":
                    event = keyboard.read_event(suppress=True)
                choice = event.name
            else:
                choice = input("\nENTER OPTION: ").strip()
            
            if choice == "1":
                self.clear_console()
                self.refresh_files()
            elif choice == "2":
                self.clear_console()
                self.refresh_files()
                folder = input("\nENTER FOLDER NAME: ").strip()
                self.change_directory(folder)
                self.clear_console()
                self.refresh_files()
            elif choice == "3":
                self.change_directory("..")
                self.clear_console()
                self.refresh_files()
            elif choice == "4":
                self.clear_console()
                self.refresh_files()
                filename = input("\nENTER FILENAME: ").strip()
                destination = input("ENTER DESTINATION FOLDER: ").strip()
                self.copy_file_to_pc(filename, destination)
                self.clear_console()
                self.refresh_files()
                print(message)
            elif choice == "5":
                self.clear_console()
                self.refresh_files()
                local_file = input("\nENTER FILE PATH TO UPLOAD: ").strip()
                self.clear_console()
                self.refresh_files()
                if isinstance(local_file, str) and local_file:
                    self.push_file_to_device(local_file)
                    self.clear_console()
                    self.refresh_files()
                    print(message)
                else:
                    self.clear_console()
                    self.refresh_files()
                    print("\n❌ ERROR: Invalid file path! Please enter a valid file path.")
            elif choice == "6":
                self.clear_console()
                self.refresh_files()
                old_name = input("\nENTER OLD FILENAME: ").strip()
                new_name = input("ENTER NEW FILENAME: ").strip()
                self.rename_file(old_name, new_name)
                self.clear_console()
                self.refresh_files()
                print(message)
            elif choice == "7":
                self.clear_console()
                self.refresh_files()
                filename = input("\nENTER FILENAME TO DELETE: ").strip()
                self.delete_file(filename)
                self.clear_console()
                self.refresh_files()
                print(message)
            elif choice == "8":
                print("\n🔴 EXITING...")
                self.clear_console()
                break
            else:
                self.clear_console()
                self.refresh_files()
                print("\n❌ INVALID CHOICE. TRY AGAIN.")

if __name__ == "__main__":
    adb_manager = ADBFileManager()
    adb_manager.start()