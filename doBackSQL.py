import os
import re
from datetime import datetime

def get_backup_file_by_time(db_dir, db_name):
    backup_files = []
    for file_name in os.listdir(db_dir):
        if db_name in file_name:
            match = re.search(r"\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2}", file_name)
            if match:
                backup_time = datetime.strptime(match.group(), "%Y-%m-%d %H-%M-%S")
                backup_files.append((backup_time, file_name))

    backup_files.sort(key=lambda x: x[0], reverse=True)

    if backup_files:
        return backup_files[0][1]
    else:
        return None

def get_backup_file_by_choice(db_dir, db_name, db_time):
    backup_files = []
    for file_name in os.listdir(db_dir):
        if db_name in file_name:
            match = re.search(r"\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2}", file_name)
            if match:
                backup_time = datetime.strptime(match.group(), "%Y-%m-%d %H-%M-%S")
                backup_files.append((backup_time, file_name))

    backup_files.sort(key=lambda x: abs(x[0] - db_time))

    if not backup_files:
        return None

    closest_file = backup_files[0]
    if closest_file[0] != db_time:
        print(f"没有找到精确匹配的备份文件。最接近的备份文件为：{closest_file[1]}")
        choice = input("是否使用此备份文件？（y/n）：")
        if choice.lower() == 'y':
            return closest_file[1]
        else:
            choice = input("是否继续？（y/n）：")
            if choice.lower() == 'y':
                return get_backup_file()
            else:
                return None
    else:
        return closest_file[1]

def get_backup_file():
    db_dir = "C:/db/Mysql"
    choice = input("请选择操作：1. 获取最新备份文件，2. 获取指定时间的备份文件：")
    db_name = input("请输入数据库名称：")

    if choice == '1':
        return get_backup_file_by_time(db_dir, db_name)
    elif choice == '2':
        db_time_str = input("请输入备份时间（格式为 YYYY-MM-DD HH:MM:SS）：")
        try:
            db_time = datetime.strptime(db_time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print("无效的时间格式。")
            return None
        return get_backup_file_by_choice(db_dir, db_name, db_time)
    else:
        print("无效的选择。")
        return None

backup_file = get_backup_file()
if backup_file:
    print(f"选择的备份文件为：{backup_file}")
else:
    print("未选择备份文件。")
