import inspect
from typing import List, Dict, Optional
from readio.utils.myExceptions import NetworkException
from readio.utils import check


# 读取数据库
def execute_sql_query(pooldb, sql: str, *args) -> List[dict]:
    """
    执行 SQL 查询并返回查询结果，结果以字典列表形式返回。
    """
    conn, cursor = pooldb.get_conn()
    try:
        # 执行 SQL 查询
        cursor.execute(sql, *args)
        # 返回结果集
        results = cursor.fetchall()
        return results
    except Exception as e:
        print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        raise e
    finally:
        # 关闭数据库连接和游标对象
        pooldb.close_conn(conn, cursor) if conn is not None else None


def execute_sql_query_one(pooldb, sql: str, *args) -> Dict:
    """
    执行 SQL 查询语句并返回单一结果。

    :param pooldb: 数据库连接池对象。
    :param sql: 要执行的 SQL 查询语句。
    :param args: SQL 查询语句所需的参数，可变参数。
    :return: 返回 SQL 查询结果中的第一条数据。
    :raises Exception: 如果执行 SQL 查询失败，则抛出异常并终止程序运行。
    """
    conn, cursor = pooldb.get_conn()
    try:
        # 执行 SQL 查询
        cursor.execute(sql, *args)
        # 返回结果，仅一条
        result = cursor.fetchone()
        return result
    except Exception as e:
        print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        raise e
    finally:
        # 关闭数据库连接和游标对象
        pooldb.close_conn(conn, cursor) if conn is not None else None


# 写入数据库
def execute_sql_write(pooldb, sql: str, *args) -> Optional[int]:
    """
    执行写入操作，并返回插入自增主键 ID。

    :param pooldb: 连接池对象。
    :param sql: SQL 语句。
    :param args: SQL 参数。
    :return: 如果是插入操作，返回插入记录的自增主键 ID；如果是更新或删除操作，返回 None。
    :raises NetworkException: 如果执行 SQL 失败，将抛出此异常。
    """
    conn, cursor = pooldb.get_conn()
    try:
        # 执行 SQL
        cursor.execute(sql, *args)
        conn.commit()
        # 获取插入自增主键 ID
        id_ = cursor.lastrowid
        return id_
    except Exception as e:
        # 发生错误，回滚事务并抛出异常
        conn.rollback() if conn is not None else None
        print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        raise NetworkException(500, 'Database error: ' + str(e))
    finally:
        # 关闭数据库连接和游标对象
        pooldb.close_conn(conn, cursor) if conn is not None else None


class SqlTransaction:
    """
    用来执行事务
    """

    def __init__(self, pooldb):
        self.pooldb = pooldb

    def begin(self):
        conn, cursor = self.pooldb.get_conn()
        self.conn = conn
        self.cursor = cursor

    def commit(self):
        self.check_null_exception()
        self.conn.commit()
        self.pooldb.close_conn(self.conn, self.cursor)

    def rollback(self):
        self.check_null_exception()
        self.conn.rollback()
        self.pooldb.close_conn(self.conn, self.cursor) if self.conn is not None else None

    def execute(self, sql: str, *args) -> Optional[int]:
        """
        执行写入操作，并返回插入自增主键 ID。

        :param sql: SQL 语句。
        :param args: SQL 参数。
        :return: 如果是插入操作，返回插入记录的自增主键 ID；如果是更新或删除操作，返回 None。
        :raises Exception: 如果执行 SQL 失败，将抛出此异常。
        """
        self.check_null_exception()
        try:
            # 执行 SQL
            self.cursor.execute(sql, *args)
            # 获取插入自增主键 ID
            id_ = self.cursor.lastrowid
            return id_
        except Exception as e:
            # 发生错误，回滚事务并抛出异常
            check.printException(e)
            self.rollback()
            raise e

    def check_null_exception(self):
        if self.conn is None or self.cursor is None:
            raise Exception("[ERROR] SqlTransaction NullException :: 事务未开启或已结束")
