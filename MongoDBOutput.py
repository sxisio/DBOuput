import os
import shutil
from datetime import datetime
import traceback
import logging

# 配置日志记录器
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
def run_MogoDB_backup():
    try:
        db_file = r"C:\db\dump"
        mongo_file = r"C:\Program Files\MongoDB\Server\4.2\bin"
        db_name = "zk_model_tqmsn"
        db_name_options = {"1": "config", "2": "metadata", "3": "admin", "4": "drgs-auto", "5": "local"}
        dump_command = "dump.bat  27017  "

        # 提示用户输入数据库名称
        db_name_input = input(
            f"请输入数据库名称 (默认值为 {db_name}): 输入对应数字可快速填入:1.config 2.medical 3.admin 4.drgs-auto 5.local\n")
        if db_name_input:
            db_name = db_name_options.get(db_name_input, db_name_input)

        # 提示用户是否备份文件夹
        # backup = input("是否备份文件？(Y/N，默认值为 N): ")
        # 直接进行文件备份，不进行提示
        backup = "N"
        if backup.upper() == "" or backup.upper() is None:
            backup = "N"
        if backup.upper() == "Y" or backup.upper() == "y":
            # 如果需要备份，则切换到 mongo_file 所设置的文件路径，执行 dump_command 与 db_name 拼接的命令
            os.chdir(mongo_file)
            os.system(f"{dump_command} {db_name}")
        elif backup.upper() == "N" or backup.upper() == "n":
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
    except Exception as e:
        # 如果发生异常，则将异常信息记录到日志文件中
        logging.error(traceback.format_exc())


while True:
    run_MogoDB_backup()
    restart = input("是否重新执行整个程序？(Y/N，默认值为 N): ")
    if restart.upper() == "" or restart.upper() is None:
        restart="N"
    if restart.upper() != "Y" or restart.upper() !="y":
        break
