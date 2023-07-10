import os
import xml.etree.ElementTree as ET
import time
import threading
import logging
import traceback

def restore_database(backup_file, db_host, db_port, db_user, db_password, backup_path):
    print("����ִ�� MySQL �ָ�...")
    try:
        # ƴ������������
        command = f"mysqlbackup --user={db_user} --password={db_password} --host={db_host} --port={db_port} --backup-dir={backup_path} --backup-image={backup_file} image-to-backup-dir"
        # ִ������������
        os.system(command)
        print(f"�ָ��ɹ���{backup_file}")
    except Exception as e:
        # ��������쳣�����쳣��Ϣ��¼����־�ļ���
        logging.error(traceback.format_exc())
        # ��������쳣�����ӡ�쳣��Ϣ
        print(f"�ָ�ʧ�ܣ�{e}")

def get_latest_backup_file(backup_path):
    backup_files = [f for f in os.listdir(backup_path) if f.endswith('.mbi')]
    if not backup_files:
        raise Exception(f"û���ҵ������ļ���{backup_path}")
    latest_backup_file = max(backup_files, key=lambda x: os.path.getmtime(os.path.join(backup_path, x)))
    return latest_backup_file

def get_closest_backup_file(backup_path, partial_name):
    backup_files = [f for f in os.listdir(backup_path) if f.endswith('.mbi') and partial_name.lower() in f.lower()]
    if not backup_files:
        raise Exception(f"û���ҵ��� {partial_name} ƥ��ı����ļ���{backup_path}")
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
        backup_file = timed_input(f"�����뱸���ļ�����Ĭ�ϣ�{get_latest_backup_file(backup_path)}��{timeout} ���ʱ����", timeout=10)
        if not backup_file:
            confirm = timed_input("����Ϊ�գ��Ƿ�����ָ����������ļ�����y/n��Ĭ�ϣ�n��{timeout} ���ʱ����", timeout=10)
            if confirm and confirm.lower() == 'y':
                continue
            else:
                return
        else:
            try:
                closest_backup_file = get_closest_backup_file(backup_path, backup_file)
                confirm = timed_input(f"�ҵ���ӽ��ı����ļ���{closest_backup_file}���Ƿ�ʹ�ã���y/n��Ĭ�ϣ�y��{timeout} ���ʱ����", timeout=10)
                if not confirm or confirm.lower() == 'y':
                    backup_file = closest_backup_file
                    break
                elif confirm.lower() == 'n':
                    continue
                else:
                    print("��Ч����")
            except Exception as e:
                # ��������쳣�����쳣��Ϣ��¼����־�ļ���
                logging.error(traceback.format_exc())
                print(e)
                continue
    restore_database(os.path.join(backup_path, backup_file), db_host, db_port, db_user, db_password, backup_path)
    confirm = timed_input("�Ƿ�����ָ����������ļ�����y/n��Ĭ�ϣ�n��{timeout} ���ʱ����", timeout=10)
    if confirm and confirm.lower() == 'y':
        restore_database_interactive(db_host, db_port, db_user, db_password, backup_path)

if __name__ == '__main__':
    logging.basicConfig(filename='error.log', level=logging.ERROR,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    # ��� XML �ļ��Ƿ���ڣ�������������׳��쳣
    if not os.path.exists('MysqlOutPut.xml'):
        raise Exception('MysqlOutPut.xml �ļ�������')
    # ��ȡ XML �ļ��е����ݿ�������Ϣ�ͱ����ļ�����·��
    tree = ET.parse('MysqlOutPut.xml')
    root = tree.getroot()
    db_host = root.find('db_host').text
    db_port = int(root.find('db_port').text)
    db_user = root.find('db_user').text
    db_password = root.find('db_password').text
    backup_path = root.find('Outdir').text
    restore_database_interactive(db_host, db_port, db_user, db_password, backup_path)
