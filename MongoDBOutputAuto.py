import os
import shutil
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from inputimeout import inputimeout, TimeoutOccurred

def run_backup():
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

scheduler = BlockingScheduler()
trigger = CronTrigger(day_of_week='mon,thu')
scheduler.add_job(run_backup, trigger)
scheduler.add_job(countdown, 'interval', seconds=1)
scheduler.start()
