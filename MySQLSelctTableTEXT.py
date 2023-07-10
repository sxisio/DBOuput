import os
import subprocess
import pymysql
import time
import xml.etree.ElementTree as ET
import getpass
import traceback
import logging

# 配置日志记录器
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
def create_xml():
    root = ET.Element('config')
    ET.SubElement(root, 'db_host').text = 'localhost'
    ET.SubElement(root, 'db_port').text = '13307'
    ET.SubElement(root, 'db_user').text = 'root'
    ET.SubElement(root, 'db_password').text = 'tqms$2021@Shijiyunyi'
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
def run_MySQL_Backup():
    print("正在执行MySQL备份...")

    try:
        # 检查XML文件是否存在，如果不存在则创建它
        if not os.path.exists('MysqlOutPut.xml'):
            print('MysqlOutPut.xml,不存在，即将创建')
            create_xml()

        # 读取XML文件中的数据库配置信息和备份文件保存路径
        tree = ET.parse('MysqlOutPut.xml')
        root = tree.getroot()
        db_host = root.find('db_host').text
        db_port = int(root.find('db_port').text)
        db_user = root.find('db_user').text
        db_password = root.find('db_password').text
        db_name = root.find('db_name').text
        backup_path = root.find('Outdir').text

        # 检查备份文件保存路径是否为空，如果为空则使用默认路径来保存备份文件
        if not backup_path:
            print(f"备份文件保存路径为空，将使用默认路径来保存备份文件")
            backup_path = 'C:\db\Mysql'

        # 检查备份文件保存路径是否存在，如果不存在则创建它
        if not os.path.exists(backup_path):
            try:
                print({backup_path}+',将创建指定备份路径')
                os.makedirs(backup_path)
            except:
                # 如果创建失败，则使用默认路径来保存备份文件
                print(f"无法创建备份文件保存路径：{backup_path}，将使用默认路径来保存备份文件")
                backup_path = 'C:\db\Mysql'
        print("连接数据库！")
        conn = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, db=db_name)
        # 连接数据库

        cursor = conn.cursor()

        tables_to_backup =input('多表以英文逗号隔开:\n')

        # 关闭数据库连接
        cursor.close()
        conn.close()

        # 获取当前时间
        date = time.strftime('%Y%m%d%H%M%S')

        # 拼接备份文件名
        backup_file = f"{backup_path}/{db_name}_{date}.sql"
        # 检查备份文件是否存在
        if not os.path.exists(backup_file):
            # 如果备份文件不存在，则创建它
            print(f"创建备份文件：{backup_file}")
            open(backup_file, 'w').close()

        else:
            print(f"备份文件已存在：{backup_file}")
        tables_to_backup = tables_to_backup.replace(",", " ")
        # 拼接命令行命令
        cmd = f"mysqldump -h {db_host} -P {db_port} -u {db_user} -p{db_password} {db_name} {' '.join(tables_to_backup)} > {backup_file}"

        print('执行备份命令')
        print(cmd)
        os.system(cmd)
        fileinfo = logging.FileHandler(f"INFO.log")
        fileinfo.setLevel(logging.INFO)
        cmd_pause='pause'
        os.system(cmd_pause)


    except Exception as e:
        # 如果发生异常，则将异常信息记录到日志文件中
        logging.error(traceback.format_exc())

if __name__ == '__main__':

    run_MySQL_Backup()

