import os
import shutil
import subprocess
import pymysql
import time
import xml.etree.ElementTree as ET
import getpass
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger


def create_xml():
    root = ET.Element('config')
    ET.SubElement(root, 'db_host').text = 'localhost'
    ET.SubElement(root, 'db_port').text = '13307'
    ET.SubElement(root, 'db_user').text = 'root'
    ET.SubElement(root, 'db_password').text = 'T9m5n@2022!!'
    ET.SubElement(root, 'db_name').text = 'tqmsn'
    ET.SubElement(root, 'Outdir').text = 'C:\db\Mysql'
    tree = ET.ElementTree(root)
    tree.write('MysqlOutPut.xml')

def Run_Environment_Variable_Detection():
    backup_home = os.getenv('Backup_HOME')
    path = os.getenv('PATH')
    if backup_home is None or '%Backup_HOME%' not in path:
        # 如果 Backup_HOME 环境变量不存在或者用户/系统路径中不包含 %Backup_HOME%
        # 使用管理员权限运行 set_env.bat
        subprocess.run(['runas', '/user:Administrator', 'set_env.bat'], shell=True)


#另一个版本的设置环境变量，使用ctypes。调用windll.shell32.ShellExecuteW
# def Run_Environment_Variable_Detection():
#     backup_home = os.getenv('Backup_HOME')
#     path = os.getenv('PATH')
#     if backup_home is None or '%Backup_HOME%' not in path:
#         # 构建 set_env.bat 文件的完整路径
#         script_path = os.path.join(os.path.dirname(__file__), 'set_env.bat')
#
#         # 请求以管理员权限运行程序
#         try:
#             ctypes.windll.shell32.ShellExecuteW(None, "runas", "python", script_path, None, 1)
#         except:
#             print("无法以管理员权限运行程序")
def run_MySQL_backup():
    print("正在检测，并设置环境变量...")
    Run_Environment_Variable_Detection()
    print("正在执行MySQL备份...")

    # 检查XML文件是否存在，如果不存在则创建它
    if not os.path.exists('MysqlOutPut.xml'):
        create_xml()

    # 读取XML文件中的数据库配置信息和备份文件保存路径
    tree = ET.parse('MysqlOutPut.xml')
    root = tree.getroot()
    db_host = root.find('db_host').text
    db_port = int(root.find('db_port').text)
    db_user = root.find('db_user').text
    db_password = root.find('db_password').text
    db_name = root.find('db_name').text
    backup_path=root.find('Outdir').text

    # 检查备份文件保存路径是否为空，如果为空则使用默认路径来保存备份文件
    if not backup_path:
        print(f"备份文件保存路径为空，将使用默认路径来保存备份文件")
        backup_path = 'C:\db\Mysql'

    # 检查备份文件保存路径是否存在，如果不存在则创建它
    if not os.path.exists(backup_path):
        try:
            os.makedirs(backup_path)
        except:
            # 如果创建失败，则使用默认路径来保存备份文件
            print(f"无法创建备份文件保存路径：{backup_path}，将使用默认路径来保存备份文件")
            backup_path = 'C:\db\Mysql'

            # 连接数据库
    while True:
        try:
            conn = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, db=db_name)
            break
        except pymysql.err.OperationalError:
            print("数据库连接失败，请检查您的用户名和密码")
            db_password = getpass.getpass("请输入数据库密码: ")
    cursor = conn.cursor()

    # 查询每个表的行数
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    tables_to_backup = []
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        if row_count < 1000000:
            tables_to_backup.append(table_name)

    # 关闭数据库连接
    cursor.close()
    conn.close()

    # 获取当前时间
    date = time.strftime('%Y%m%d')

    # 拼接备份文件名
    backup_file = f"{backup_path}/{db_name}_{date}.sql"

    # 拼接命令行命令
    cmd = f"mysqldump -h {db_host} -P {db_port} -u {db_user} -p{db_password} {db_name} {' '.join(tables_to_backup)} > {backup_file}"

    # 执行命令
    os.system(cmd)
    print("MySQL备份完成")
def countdown():
    today = datetime.now().weekday()+1
    if 5 >today > 1:
        next_run_time = scheduler.get_jobs()[1].next_run_time
    else:
        next_run_time = scheduler.get_jobs()[0].next_run_time
    time_remaining = next_run_time - datetime.now(next_run_time.tzinfo)
    days = time_remaining.days
    hours, remainder = divmod(time_remaining.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"\r据下次生效还有{int(days)}日{int(hours)}时{int(minutes)}分{int(seconds)}秒", end="")



scheduler = BlockingScheduler()
trigger = CronTrigger(day_of_week='mon,thu')
scheduler.add_job(run_MySQL_backup, trigger)
scheduler.add_job(countdown, 'interval', seconds=1)
scheduler.start()