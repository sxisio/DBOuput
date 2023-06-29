import os
import shutil
import subprocess
import pymysql
import time
import xml.etree.ElementTree as ET
import getpass
# import ctypes
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from inputimeout import inputimeout, TimeoutOccurred

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
def create_xml():
    root = ET.Element('config')
    ET.SubElement(root, 'db_host').text = 'localhost'
    ET.SubElement(root, 'db_port').text = '13307'
    ET.SubElement(root, 'db_user').text = 'root'
    ET.SubElement(root, 'db_password').text = 'T9m5n@2022!'
    ET.SubElement(root, 'db_name').text = 'tqmsn'
    ET.SubElement(root, 'Outdir').text = 'C:\db\Mysql'
    tree = ET.ElementTree(root)
    tree.write('MysqlOutPut.xml')


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
    # 执行命令
    subprocess.run(cmd, shell=True)
    print("MySQL备份完成")

def run_MogoDB_backup():
    print("程序正在执行！！")
    db_file = r"C:\db\dump"
    mongo_file = r"C:\Program Files\MongoDB\Server\4.2\bin"
    db_name = "zk_model_tqmsn"
    db_name_options = {"1": "config", "2": "metadata", "3": "admin", "4": "drgs-auto", "5": "local"}
    dump_command = "dump.bat  27017  "

    # 提示用户输入数据库名称
    try:
        db_name_input = inputimeout(prompt=f"请输入数据库名称 (默认值为 {db_name}): 输入对应数字可快速填入:1.config 2.medical 3.admin 4.drgs-auto 5.local\n", timeout=5)
    except TimeoutOccurred:
        print(f"您没有在5秒内输入任何字符，将按默认值 {db_name} 执行")
        db_name_input = db_name

    if db_name_input:
        db_name = db_name_options.get(db_name_input, db_name_input)

    # 提示用户是否备份文件夹
    # backup = input("是否备份文件？(Y/N，默认值为 N): ")
    # 直接进行文件备份，不进行提示
    backup = "N"
    if backup.upper() == "" or backup.upper() is None:
        backup="N"
    if backup.upper() == "Y" or backup.upper() =="y":
        # 如果需要备份，则切换到 mongo_file 所设置的文件路径，执行 dump_command 与 db_name 拼接的命令
        os.chdir(mongo_file)
        os.system(f"{dump_command} {db_name}")
    elif backup.upper() == "N" or backup.upper() =="n":
        # 如果需要备份，则切换到 db_file，将名为 db_name 参数名称的文件夹重命名为 db_name 参数名称拼接时间
        os.chdir(db_file)
        datestr = datetime.now().strftime("%Y-%m-%d")
        old_folder = os.path.join(db_file, db_name)
        new_folder = os.path.join(db_file, f"{db_name}_{datestr}")
        if os.path.exists(old_folder):
            shutil.move(old_folder, new_folder)

        # 检测 db_file 下是否还存在 db_name
        if not os.path.exists(old_folder):
            # 如果不存在，则切换到 mongo_file，执行 dump_command 拼接 db_name
            os.chdir(mongo_file)
            os.system(f"{dump_command} {db_name}")
            print("程序执行完毕！！")
        os.system('cls' if os.name == 'nt' else 'clear')

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

def run_Combined_backup():
    run_MySQL_backup()
    run_MogoDB_backup()

scheduler = BlockingScheduler()
trigger = CronTrigger(day_of_week='mon,thu')
scheduler.add_job(run_Combined_backup, trigger)
scheduler.add_job(countdown, 'interval', seconds=1)
scheduler.start()