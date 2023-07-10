import os
import xml.etree.ElementTree as ET
import time
import threading
import logging
import traceback

def restore_database(backup_file, db_host, db_port, db_user, db_password, backup_path):
    print("正在执行 MySQL 恢复...")
    try:
        # 拼接命令行命令
        command = f"mysqlbackup --user={db_user} --password={db_password} --host={db_host} --port={db_port} --backup-dir={backup_path} --backup-image={backup_file} image-to-backup-dir"
        # 执行命令行命令
        os.system(command)
        print(f"恢复成功：{backup_file}")
    except Exception as e:
        # 如果发生异常，则将异常信息记录到日志文件中
        logging.error(traceback.format_exc())
        # 如果发生异常，则打印异常信息
        print(f"恢复失败：{e}")

def get_latest_backup_file(backup_path):
    backup_files = [f for f in os.listdir(backup_path) if f.endswith('.mbi')]
    if not backup_files:
        raise Exception(f"没有找到备份文件：{backup_path}")
    latest_backup_file = max(backup_files, key=lambda x: os.path.getmtime(os.path.join(backup_path, x)))
    return latest_backup_file

def get_closest_backup_file(backup_path, partial_name):
    backup_files = [f for f in os.listdir(backup_path) if f.endswith('.mbi') and partial_name.lower() in f.lower()]
    if not backup_files:
        raise Exception(f"没有找到与 {partial_name} 匹配的备份文件：{backup_path}")
    closest_backup_file = max(backup_files, key=lambda x: os.path.getmtime(os.path.join(backup_path, x)))
    return closest_backup_file

def timed_input(prompt, timeout=5):
    timer = threading.Timer(timeout, thread.interrupt_main)
    answer = None
    try:
        timer.start()
        answer = input(prompt)
    except KeyboardInterrupt:
        pass
    timer.cancel()
    return answer

def restore_database_interactive(db_host, db_port, db_user, db_password, backup_path):
    while True:
        backup_file = timed_input(f"请输入备份文件名（默认：{get_latest_backup_file(backup_path)}，{timeout} 秒后超时）：", timeout=10)
        if not backup_file:
            confirm = timed_input("输入为空，是否继续恢复其他备份文件？（y/n，默认：n，{timeout} 秒后超时）：", timeout=10)
            if confirm and confirm.lower() == 'y':
                continue
            else:
                return
        else:
            try:
                closest_backup_file = get_closest_backup_file(backup_path, backup_file)
                confirm = timed_input(f"找到最接近的备份文件：{closest_backup_file}，是否使用？（y/n，默认：y，{timeout} 秒后超时）：", timeout=10)
                if not confirm or confirm.lower() == 'y':
                    backup_file = closest_backup_file
                    break
                elif confirm.lower() == 'n':
                    continue
                else:
                    print("无效输入")
            except Exception as e:
                # 如果发生异常，则将异常信息记录到日志文件中
                logging.error(traceback.format_exc())
                print(e)
                continue
    restore_database(os.path.join(backup_path, backup_file), db_host, db_port, db_user, db_password, backup_path)
    confirm = timed_input("是否继续恢复其他备份文件？（y/n，默认：n，{timeout} 秒后超时）：", timeout=10)
    if confirm and confirm.lower() == 'y':
        restore_database_interactive(db_host, db_port, db_user, db_password, backup_path)

if __name__ == '__main__':
    logging.basicConfig(filename='error.log', level=logging.ERROR,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    # 检查 XML 文件是否存在，如果不存在则抛出异常
    if not os.path.exists('MysqlOutPut.xml'):
        raise Exception('MysqlOutPut.xml 文件不存在')
    # 读取 XML 文件中的数据库配置信息和备份文件保存路径
    tree = ET.parse('MysqlOutPut.xml')
    root = tree.getroot()
    db_host = root.find('db_host').text
    db_port = int(root.find('db_port').text)
    db_user = root.find('db_user').text
    db_password = root.find('db_password').text
    backup_path = root.find('Outdir').text
    restore_database_interactive(db_host, db_port, db_user, db_password, backup_path)
