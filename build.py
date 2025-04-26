# build.py
import subprocess
from generate_verfile import generate_ver_file

def build():
    # Генерируем .rc файл
    rc_file = generate_ver_file("version.txt", "version_info.txt.template", "version_info.txt")
    
    # Запускаем PyInstaller
    subprocess.run([
        "pyinstaller",
        "--onefile",
        "--noconsole",
        f"--version-file={rc_file}",
        "ModemSetup.py"
    ])

if __name__ == "__main__":
    build()