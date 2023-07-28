'''
后端服务器将会面对很多连接，面对大量的web请求，增删改查，mysql连接会不稳定，
可能会发生Lost connection to MySQL或线程竞争的情况，所以我们新建一个连接池，
在程序创建连接的时候从空闲的来凝结中获取，不需要重新初始化连接，提升获取连接的速度
使用DBUtils实现连接池
'''
import pymysql
from sqlalchemy import null
from dbutils.pooled_db import PooledDB
from pymysql.cursors import DictCursor
import time
import os


class Pooldb:
    def __init__(
            self,
            host="127.0.0.1",
            user="root",
            password="123456",
            database="rucwall",
            port=3306,
            max_reconnect_time=20
    ):
        self.host = host
        self.user = user
        self.port = int(port)
        self.password = password
        self.database = database

        for i in range(max_reconnect_time):
            try:
                # 打开数据库连接
                self.pool = PooledDB(
                    creator=pymysql,  # 数据库类型
                    maxcached=200,  # 最大空闲数
                    blocking=True,  # 达到最大连接数时，新连接阻塞，等待连接数减少再连接
                    ping=1,  # 何时用ping检查连接，选择4是执行sql语句时ping，1是当连接被取走时ping，2是当连接创建cursor时ping
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    passwd=self.password,
                    db=self.database,
                    charset='utf8mb4',
                    local_infile=True,
                )
            except BaseException as e:
                print(f"数据库连接错误！{e}")
                self.pool = null
            if self.pool:
                print(f"数据库{self.host}:{self.port}连接成功！当前操作数据库{self.database}")
                break
            time.sleep(5)  # 停一段时间再重新连接

    def execute_scirpt(self, file, conn, cursor):
        with open(file, 'r', encoding='utf8') as f:
            data = f.read()
            lines = data.splitlines()
            sql_data = ''
            for line in lines:
                if len(line) == 0:
                    continue
                elif line.startswith('--'):
                    continue
                else:
                    sql_data += line

            sql_list = sql_data.split(';')[:-1]
            sql_list = [x.replace('\n', ' ') if '\n' in x else x for x in sql_list]
            sql_item = ""
            try:
                for sql_item in sql_list:
                    cursor.execute(sql_item)

            except:
                print('connect.py::execute_scirpt sql脚本执行失败')
                print('错误的sql语句：', sql_item)
                conn.rollback()
                raise Exception()

            try:
                conn.commit()
            except:
                print('connect.py::execute_scirpt 事务提交失败')
                raise Exception()

    def get_conn(self, cursor_mode='dict'):
        conn = self.pool.connection()
        if cursor_mode == 'tuple':
            cursor = conn.cursor()
        elif cursor_mode == 'dict':
            cursor = conn.cursor(DictCursor)
        return conn, cursor

    def close_conn(self, conn, cursor):
        cursor.close()
        conn.close()

    def read(self, sql):
        try:
            conn, cursor = pooldb.get_conn()
            cursor.execute(sql)
            rows = cursor.fetchall()
            pooldb.close_conn(conn, cursor)
            return rows

        except Exception as e:
            print(e)
            pooldb.close_conn(conn, cursor)
            raise Exception('Pooldb::read错误！')

    def execute_scirpt(self, file):
        with open(file, 'r', encoding='utf8') as f:
            data = f.read()
            lines = data.splitlines()
            # print("lines:",lines)
            sql_data = ''
            for line in lines:
                if len(line) == 0:
                    continue
                elif line.startswith('--'):
                    continue
                else:
                    sql_data += line
            # print("sql_data:",sql_data)

            sql_list = sql_data.split(';')[:-1]
            sql_list = [x.replace('\n', ' ') if '\n' in x else x for x in sql_list]
            sql_item = ""
            # print(sql_list)
            try:
                conn, cursor = self.get_conn()
                for sql_item in sql_list:
                    # print("[DEBUG] execute : ",sql_item)
                    cursor.execute(sql_item)

            except:
                print('connect.py::execute_scirpt sql脚本执行失败')
                print('错误的sql语句：', sql_item)
                conn.rollback()
                self.close_conn(conn, cursor)
                raise Exception()

            try:
                conn.commit()
            except:
                conn.rollback()
                self.close_conn(conn, cursor)
                print('connect.py::execute_scirpt 事务提交失败')
                raise Exception()


MYSQL_HOST = os.environ.get('MYSQL_HOST')
MYSQL_PORT = os.environ.get('MYSQL_PORT')
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
if not MYSQL_HOST:
    MYSQL_HOST = '127.0.0.1'
if not MYSQL_PORT:
    MYSQL_PORT = 3306
if not MYSQL_USER:
    MYSQL_USER = 'root'
if not MYSQL_PASSWORD:
    MYSQL_PASSWORD = '123456'
if not MYSQL_DATABASE:
    MYSQL_DATABASE = 'rucwall'

global pooldb
pooldb = Pooldb(host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE)
