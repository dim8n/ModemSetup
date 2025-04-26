# build.py
import subprocess
import os
from generate_verfile import generate_ver_file

def build():
    # Генерируем version_info.txt файл
    ver_file = generate_ver_file("version.txt", "version_info.txt.template", "version_info.txt")
    
    user_dir = os.getenv('USERPROFILE')

    # Запускаем PyInstaller
    subprocess.run([
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--strip",
        f"--upx-dir={user_dir}\\Documents\\develop\\upx",
        f"--version-file={ver_file}",
        "ModemSetup.py"
    ])

if __name__ == "__main__":
    build()