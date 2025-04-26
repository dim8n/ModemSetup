# update_version.py
import os
import sys

def increment_version(version_file):
    # Читаем текущую версию
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            version = f.read().strip()
        
        # Разбираем версию на компоненты
        try:
            major, minor, build = map(int, version.split('.'))
            build += 1  # Инкрементируем номер сборки
            new_version = f"{major}.{minor}.{build}"
        except:
            new_version = "1.0.1"  # Если файл поврежден, начинаем заново
    else:
        new_version = "1.0.1"  # Первая версия
    
    # Записываем новую версию
    with open(version_file, 'w') as f:
        f.write(new_version)
    
    return new_version

if __name__ == "__main__":
    version_file = "version.txt"
    new_version = increment_version(version_file)
    print(f"Version updated to: {new_version}")