import os
import subprocess
import platform
import sys
import shutil

def is_wsl():
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False

def activate_venv():
    if sys.prefix != sys.base_prefix:
        return
    venv_path = os.path.join(os.getcwd(), "venv")
    activate_script = os.path.join(venv_path, "bin", "activate")
    if os.path.exists(venv_path) and os.path.exists(activate_script):
        print("🔄 Activating Virtual Environment...")
        os.system(f"source {activate_script} && python3 {' '.join(sys.argv)}")
        sys.exit()

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
        self.refresh_files()

    def copy_file_to_pc(self, filename, destination):
        file_path = os.path.join(self.current_path, filename).replace("\\", "/")
        subprocess.run(["adb", "pull", file_path, destination])
        print(f"\n✅ {filename} copied to {destination}")
        self.refresh_files()

    def push_file_to_device(self, local_file):
        if os.path.exists(local_file):
            local_file = local_file.replace("\\", "/")
            subprocess.run(["adb", "push", local_file, self.current_path])
            print(f"\n✅ {local_file} uploaded to {self.current_path}")
        else:
            print(f"\n❌ Error: File '{local_file}' not found! Check the path.")
        self.refresh_files()

    def rename_file(self, old_name, new_name):
        old_path = os.path.join(self.current_path, old_name).replace("\\", "/")
        new_path = os.path.join(self.current_path, new_name).replace("\\", "/")
        self.run_adb(["mv", old_path, new_path])
        print(f"\n✅ {old_name} renamed to {new_name}")
        self.refresh_files()

    def delete_file(self, filename):
        file_path = os.path.join(self.current_path, filename).replace("\\", "/")
        confirm = input(f"⚠ Are you sure you want to delete {filename}? (y/n): ")
        if confirm.lower() == 'y':
            self.run_adb(["rm", "-r", file_path])
            print(f"\n🗑 {filename} deleted.")
        self.refresh_files()

    def show_menu(self):
        print("\n--- ADB File Manager ---\n")
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
                self.clear_console()
                self.copy_file_to_pc(filename, destination)
                self.refresh_files()
            elif choice == "5":
                self.clear_console()
                self.refresh_files()
                local_file = input("\nENTER FILE PATH TO UPLOAD: ").strip()
                self.clear_console()
                self.push_file_to_device(local_file)
                self.refresh_files()
            elif choice == "6":
                self.clear_console()
                self.refresh_files()
                old_name = input("\nENTER OLD FILENAME: ").strip()
                new_name = input("ENTER NEW FILENAME: ").strip()
                self.clear_console()
                self.rename_file(old_name, new_name)
                self.refresh_files()
            elif choice == "7":
                self.clear_console()
                self.refresh_files()
                filename = input("\nENTER FILENAME TO DELETE: ").strip()
                self.clear_console()
                self.delete_file(filename)
                self.refresh_files()
            elif choice == "8":
                self.clear_console()
                print("\n🔴 EXITING...")
                break
            else:
                print("❌ INVALID CHOICE. TRY AGAIN.")

if __name__ == "__main__":
    adb_manager = ADBFileManager()
    adb_manager.start()
