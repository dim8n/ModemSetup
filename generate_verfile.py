# generate_rc.py
import os
from update_version import increment_version

def generate_ver_file(version_file, template_file_txt, output_file_txt):
    # Получаем/обновляем версию
    version = increment_version(version_file)
    version_tuple = tuple(map(int, version.split('.'))) + (0,)
    version_str = ",".join(map(str, version_tuple))
    
    # Читаем шаблон txt
    with open(template_file_txt, 'r') as f:
        template = f.read()
    
    # Заменяем плейсхолдеры txt
    rc_content = template.replace("{FILEVERSION}", version_str)
    rc_content = rc_content.replace("{PRODUCTVERSION}", version_str)
    rc_content = rc_content.replace("{COMPANYNAME}", "dim8n Co")
    rc_content = rc_content.replace("{FILEDESCRIPTION}", "Modem Setup")
    rc_content = rc_content.replace("{INTERNALNAME}", "modemsetup")
    rc_content = rc_content.replace("{COPYRIGHT}", "Elizarov D.O. (c) d.elizarov@gmail.com 2025")
    rc_content = rc_content.replace("{ORIGINALFILENAME}", "ModemSetup.exe")
    rc_content = rc_content.replace("{PRODUCTNAME}", "ModemSetup")
    rc_content = rc_content.replace("{FILEVERSION}", version)
    rc_content = rc_content.replace("{PRODUCTVERSION}", version)
    
    # Сохраняем .rc файл
    with open(output_file_txt, 'w') as f:
        f.write(rc_content)

    return output_file_txt

if __name__ == "__main__":
    version_file = "version.txt"
    template_file = "version.rc.template"
    template_file_txt = "version_info.txt.template"
    output_file = "version.rc"
    output_file_txt = "version_info.txt"
    
    rc_file = generate_ver_file(version_file, template_file_txt, output_file_txt)
    print(f"Generated file: {rc_file}")