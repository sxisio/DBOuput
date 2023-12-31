import os
import subprocess
import pymysql
import time
import xml.etree.ElementTree as ET
import getpass
import traceback
import logging

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
    ET.SubElement(root, 'db_password').text = 'tqms$2021@Shijiyunyi'
    ET.SubElement(root, 'db_name').text = 'tqmsn'
    ET.SubElement(root, 'Outdir').text = 'C:\db\Mysql'
    tree = ET.ElementTree(root)
    tree.write('MysqlOutPut.xml')


def run_MySQL_Backup():
    print("正在执行MySQL备份...")
    if_staut=0
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
        try:
            # 连接数据库
            conn = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password, db=db_name)
            print("连接数据库成功！")
            try:
                cursor = conn.cursor()
                Horizontalbar='-'
                sql = "SELECT TABLE_NAME  FROM INFORMATION_SCHEMA.TABLES  WHERE  TABLE_SCHEMA = '%s' AND TABLE_NAME REGEXP '^[^0-9]+$' AND TABLE_TYPE = 'BASE TABLE' AND TABLE_NAME  NOT IN (SELECT TABLE_NAME  FROM INFORMATION_SCHEMA.TABLES  WHERE  TABLE_TYPE = 'VIEW') AND TABLE_NAME NOT LIKE '%%-%%' AND TABLE_NAME NOT IN ('CHARACTER_SETS','COLLATIONS','COLLATION_CHARACTER_SET_APPLICABILITY','COLUMNS','COLUMN_PRIVILEGES','ENGINES','EVENTS','FILES','GLOBAL_STATUS','GLOBAL_VARIABLES','KEY_COLUMN_USAGE','OPTIMIZER_TRACE','PARAMETERS','PARTITIONS','PLUGINS','PROCESSLIST','PROFILING','REFERENTIAL_CONSTRAINTS','ROUTINES','SCHEMATA','SCHEMA_PRIVILEGES','SESSION_STATUS','SESSION_VARIABLES','STATISTICS','TABLES','TABLESPACES','TABLE_CONSTRAINTS','TABLE_PRIVILEGES','TRIGGERS','USER_PRIVILEGES','VIEWS','INNODB_LOCKS','INNODB_TRX','INNODB_SYS_DATAFILES','INNODB_FT_CONFIG','INNODB_SYS_VIRTUAL','INNODB_CMP','INNODB_FT_BEING_DELETED','INNODB_CMP_RESET','INNODB_CMP_PER_INDEX','INNODB_CMPMEM_RESET','INNODB_FT_DELETED','INNODB_BUFFER_PAGE_LRU','INNODB_LOCK_WAITS','INNODB_TEMP_TABLE_INFO','INNODB_SYS_INDEXES','INNODB_SYS_TABLES','INNODB_SYS_FIELDS','INNODB_CMP_PER_INDEX_RESET','INNODB_BUFFER_PAGE','INNODB_FT_DEFAULT_STOPWORD','INNODB_FT_INDEX_TABLE','INNODB_FT_INDEX_CACHE','INNODB_SYS_TABLESPACES','INNODB_METRICS','INNODB_SYS_FOREIGN_COLS','INNODB_CMPMEM','INNODB_BUFFER_POOL_STATS','INNODB_SYS_COLUMNS','INNODB_SYS_FOREIGN','INNODB_SYS_TABLESTATS','columns_priv','db','engine_cost','event','func','general_log','gtid_executed','help_category','help_keyword','help_relation','help_topic','innodb_index_stats','innodb_table_stats','ndb_binlog_index','plugin','proc','procs_priv','proxies_priv','server_cost','servers','slave_master_info','slave_relay_log_info','slave_worker_info','slow_log','tables_priv','time_zone','time_zone_leap_second','time_zone_name','time_zone_transition','time_zone_transition_type','user','accounts','cond_instances','events_stages_current','events_stages_history','events_stages_history_long','events_stages_summary_by_account_by_event_name','events_stages_summary_by_host_by_event_name','events_stages_summary_by_thread_by_event_name','events_stages_summary_by_user_by_event_name','events_stages_summary_global_by_event_name','events_statements_current','events_statements_history','events_statements_history_long','events_statements_summary_by_account_by_event_name','events_statements_summary_by_digest','events_statements_summary_by_host_by_event_name','events_statements_summary_by_program','events_statements_summary_by_thread_by_event_name','events_statements_summary_by_user_by_event_name','events_statements_summary_global_by_event_name','events_transactions_current','events_transactions_history','events_transactions_history_long','events_transactions_summary_by_account_by_event_name','events_transactions_summary_by_host_by_event_name','events_transactions_summary_by_thread_by_event_name','events_transactions_summary_by_user_by_event_name','events_transactions_summary_global_by_event_name','events_waits_current','events_waits_history','events_waits_history_long','events_waits_summary_by_account_by_event_name','events_waits_summary_by_host_by_event_name','events_waits_summary_by_instance','events_waits_summary_by_thread_by_event_name','events_waits_summary_by_user_by_event_name','events_waits_summary_global_by_event_name','file_instances','file_summary_by_event_name','file_summary_by_instance','host_cache','hosts','memory_summary_by_account_by_event_name','memory_summary_by_host_by_event_name','memory_summary_by_thread_by_event_name','memory_summary_by_user_by_event_name','memory_summary_global_by_event_name','metadata_locks','mutex_instances','objects_summary_global_by_type','performance_timers','prepared_statements_instances','replication_applier_configuration','replication_applier_status','replication_applier_status_by_coordinator','replication_applier_status_by_worker','replication_connection_configuration','replication_connection_status','replication_group_member_stats','replication_group_members','rwlock_instances','session_account_connect_attrs','session_connect_attrs','setup_actors','setup_consumers','setup_instruments','setup_objects','setup_timers','socket_instances','socket_summary_by_event_name','socket_summary_by_instance','status_by_account','status_by_host','status_by_thread','status_by_user','table_handles','table_io_waits_summary_by_index_usage','table_io_waits_summary_by_table','table_lock_waits_summary_by_table','threads','user_variables_by_thread','users','variables_by_thread','host_summary','host_summary_by_file_io','host_summary_by_file_io_type','host_summary_by_stages','host_summary_by_statement_latency','host_summary_by_statement_type','innodb_buffer_stats_by_schema','innodb_buffer_stats_by_table','io_by_thread_by_latency','io_global_by_file_by_bytes','io_global_by_file_by_latency','io_global_by_wait_by_bytes','io_global_by_wait_by_latency','latest_file_io','memory_by_host_by_current_bytes','memory_by_thread_by_current_bytes','memory_by_user_by_current_bytes','memory_global_by_current_bytes','memory_global_total','metrics','ps_check_lost_instrumentation','schema_auto_increment_columns','schema_index_statistics','schema_object_overview','schema_redundant_indexes','schema_table_lock_waits','schema_table_statistics','schema_table_statistics_with_buffer','schema_tables_with_full_table_scans','schema_unused_indexes','session','session_ssl_status','statement_analysis','statements_with_errors_or_warnings','statements_with_full_table_scans','statements_with_sorting','statements_with_temp_tables','sys_config','user_summary','user_summary_by_file_io','user_summary_by_file_io_type','user_summary_by_stages','user_summary_by_statement_latency','user_summary_by_statement_type','version','wait_classes_global_by_avg_latency','wait_classes_global_by_latency','waits_by_host_by_latency','waits_by_user_by_latency','waits_global_by_latency','x$host_summary','x$host_summary_by_file_io','x$host_summary_by_file_io_type','x$host_summary_by_stages','x$host_summary_by_statement_latency','x$host_summary_by_statement_type','x$innodb_buffer_stats_by_schema','x$innodb_buffer_stats_by_table','x$innodb_lock_waits','x$io_by_thread_by_latency','x$io_global_by_file_by_bytes','x$io_global_by_file_by_latency','x$io_global_by_wait_by_bytes','x$io_global_by_wait_by_latency','x$latest_file_io','x$memory_by_host_by_current_bytes','x$memory_by_thread_by_current_bytes','x$memory_by_user_by_current_bytes','x$memory_global_by_current_bytes','x$memory_global_total','x$processlist','x$ps_digest_avg_latency_distribution','x$ps_schema_table_statistics_io','x$schema_flattened_keys','x$schema_index_statistics','x$schema_table_lock_waits','x$schema_table_statistics','x$schema_table_statistics_with_buffer','x$schema_tables_with_full_table_scans','x$session','x$statement_analysis','x$statements_with_errors_or_warnings','x$statements_with_full_table_scans','x$statements_with_sorting','x$statements_with_temp_tables','x$user_summary','x$user_summary_by_file_io','x$user_summary_by_file_io_type','x$user_summary_by_stages','x$user_summary_by_statement_latency','x$user_summary_by_statement_type','x$wait_classes_global_by_avg_latency','x$wait_classes_global_by_latency','x$waits_by_host_by_latency','x$waits_by_user_by_latency','x$waits_global_by_latency','sys_user')" % db_name
                # 查询每个表的行数
                # command = "mysql -uroot -ptqms$2021@Shijiyunyi  -h localhost -P  13307 -D tqmsn -sqp -e %s" % sql
                try:
                    command = f"mysql -u{db_user} -p{db_password} -h {db_host} -P {db_port} -D {db_name} -e \"{sql}\""
                    print(command)
                    try:
                        result = subprocess.check_output(command, shell=True).decode('utf-8')
                    except:
                        result = subprocess.check_output(command, shell=True).decode('gbk')
                    print("result")
                    print(result)
                except subprocess.CalledProcessError as e:
                    # 如果发生异常，则将异常信息记录到日志文件中
                    with open('err.log', 'a') as f:
                        f.write(str(e) + '\n')
                # 获取输出结果
                lines = result.strip().split('\n')
                header = lines[0]
                output = [line.split('\t') for line in lines[2:]]
                print('执行查表操作后查出一下表')
                print(output)
                tables = output
                tables_to_backup = []
                for table in tables:
                    table_name = table[0]
                    print(table_name)
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                    if row_count < 1000000:
                        tables_to_backup.append(table_name)
                last_tables_to_backup = tables_to_backup[-1]
                print('即将备份数据表')
                tables_to_backup = [line[:-1] for line in tables_to_backup]
                tables_to_backup[-1] = last_tables_to_backup
                print(tables_to_backup)
                # 关闭数据库连接
                cursor.close()
                conn.close()
                if_staut = 1
            except Exception as e:
                # 如果发生异常，则将异常信息记录到日志文件中
                logging.error(traceback.format_exc())
            if if_staut == 1:
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
                # 拼接命令行命令
                file_name = "set_Tables.txt"
                with open(file_name, 'w') as f:
                    for item in tables_to_backup:
                        f.write(item + '\n')
                delims='"delims="'
                cmd = f"for /f %s %%a in ({file_name}) do ( mysqldump -h {db_host} -P {db_port} -u {db_user} -p{db_password} {db_name} %%a >> {backup_file})" %delims
                print('执行备份命令')
                print(cmd)
                os.system(cmd)
                print('清屏！')
                os.system('cls' if os.name == 'nt' else 'clear')
                restore_MySQL_Backup(backup_file, db_user, db_password, db_host, db_port)
                backup_Test_Database(backup_file)
        except Exception as e:
            print("连接数据库失败！")
            # 如果发生异常，则将异常信息记录到日志文件中
            logging.error(traceback.format_exc())
    except Exception as e:
        print("连接数据库失败！")
        # 如果发生异常，则将异常信息记录到日志文件中
        logging.error(traceback.format_exc())

def restore_MySQL_Backup(backup_file, db_user, db_password, db_host, db_port):
    print("正在执行 MySQL 备份还原...")
    try:
         # 连接到数据库
        conn = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password)
        cursor = conn.cursor()
        # 删除 test 数据库中的所有数据
        print('删除 test 数据库中的所有数据')
        try:
            cursor.execute("DROP DATABASE IF EXISTS test")
            cursor.execute("CREATE DATABASE test")
        except Exception as e:
            print(f"删除失败：{e}")
            # 如果发生异常，则将异常信息记录到日志文件中
            logging.error(traceback.format_exc())
        # 关闭数据库连接
        cursor.close()
        conn.close()
        # 拼接命令行命令
        command = f"mysql -u {db_user} -p{db_password} -h {db_host} -P {db_port} test < {backup_file}"
        # 执行命令行命令
        os.system(command)
        print(f"备份还原成功：{backup_file}")
    except Exception as e:
        # 如果发生异常，则打印异常信息
        print(f"备份还原失败：{e}")
        # 如果发生异常，则将异常信息记录到日志文件中
        logging.error(traceback.format_exc())
def backup_Test_Database(backup_file):
    print("正在执行 MySQL 备份...")
    try:
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
        # 获取当前时间
        date = time.strftime('%Y%m%d%H%M%S')
        # 拼接备份文件名
        new_backup_file = f"test_{date}.mbi"
        # 拼接命令行命令
        command = f"mysqlbackup --user={db_user} --password={db_password} --host={db_host} --port={db_port} --backup-dir={backup_path} --databases=test backup-to-image={new_backup_file}"
        # 执行命令行命令
        os.system(command)
        print(f"备份成功：{new_backup_file}")
        # 删除旧的备份文件
        if os.path.exists(backup_file):
            os.remove(backup_file)
            print(f"已删除旧的备份文件：{backup_file}")
        print(f"已删除旧的备份文件：{backup_file}")
    except Exception as e:
        # 如果发生异常，则打印异常信息
        print(f"备份失败：{e}")
if __name__ == '__main__':
    # 配置日志记录器
    logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    run_MySQL_Backup()

