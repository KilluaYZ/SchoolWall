from flask import request
import inspect
import hashlib
import os
import random

from typing import Dict, Union, Optional
from werkzeug.security import check_password_hash, generate_password_hash
import readio.database.connectPool
from readio.utils import check
from readio.utils.check import printException
from readio.utils.myExceptions import NetworkException
from readio.utils.executeSQL import *
global pooldb
pooldb = readio.database.connectPool.pooldb
from readio.utils.buildResponse import *


def build_token():
    while True:
        token = hashlib.sha1(os.urandom(24)).hexdigest()
        rows = pooldb.read('select * from user_token where token="%s"' % token)
        if not rows or (rows and len(rows) == 0):
            # 找到一个不重复的token
            break
    return token


def build_session(uid):
    try:
        token = build_token()
        # print('[DEBUG] build token success, token=',token)
        conn, cursor = pooldb.get_conn()
        cursor.execute('insert into user_token(uid, token) values(%s, %s)', (uid, token))
        conn.commit()
        pooldb.close_conn(conn, cursor)
        return token

    except Exception as e:
        print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        if conn is not None:
            pooldb.close_conn(conn, cursor)
        print(e)
        raise Exception('创建会话失败')


def update_token_visit_time(token):
    try:
        conn, cursor = pooldb.get_conn()
        cursor.execute('update user_token set visitTime=CURRENT_TIMESTAMP where token=%s', (token))
        conn.commit()
        pooldb.close_conn(conn, cursor)
        return token

    except Exception as e:
        print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        if conn is not None:
            pooldb.close_conn(conn, cursor)
        print(e)
        raise Exception('更新token状态失败')


def get_user_by_token(token) -> Dict[str, Union[int, str]]:
    try:
        conn, cursor = pooldb.get_conn()
        cursor.execute('select * from users, user_token where token=%s and user_token.uid=users.id', token)
        row = cursor.fetchone()
        if row is None or len(row) <= 0:
            raise NetworkException(code=401, msg='会话以失效')

        pooldb.close_conn(conn, cursor)
        return row

    except Exception as e:
        check.printException(e)
        raise e
    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


def check_if_token_exist(token: str) -> bool:
    try:
        conn, cursor = pooldb.get_conn()
        cursor.execute('select * from user_token where token=%s ', token)
        row = cursor.fetchall()
        if row is None or len(row) <= 0:
            return False
        return True

    except Exception as e:
        check.printException(e)
        raise e
    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)




def check_tokens_get_state(token, roles):
    if token is None:
        raise Exception(404)
    # print('token=',token)
    if not check_if_token_exist(token):
        return 401

    user = get_user_by_token(token)
    if user is None:
        # 查无此人
        return 404
    if roles == 'admin':
        if user['roles'] != 'admin':
            # 没有权限
            return 403
    elif roles == 'manager':
        if user['roles'] not in ['admin', 'manager']:
            # 没有权限
            return 403
    elif roles == 'common':
        if user['roles'] not in ['admin', 'manager', 'common']:
            return 403
    else:
        # 未知roles
        return 500
    update_token_visit_time(token)
    # 有对应权限,放行
    return 200


# 检查Token和权限，如果不是200就直接返回到客户端
def check_tokens_reponse_if_not200(token, roles):
    state = check_tokens_get_state(token, roles)
    if state == 401:
        raise NetworkException(code=401, msg='会话已过期，请重新登录')
    elif state == 404:
        raise NetworkException(code=404, msg='持有该令牌的用户不存在或已被删除')
    elif state == 403:
        raise NetworkException(code=403, msg='您没有该操作的权限，请联系管理员')
    elif state == 500:
        raise NetworkException(code=500, msg='服务器内部发生错误，请联系管理员')


def check_user_before_request(req, raise_exc=True, roles='common') -> Optional[Dict[str, Union[int, str]]]:
    """
    在请求前检查用户是否有访问该API的权限
    :param req: 请求对象，包含了HTTP请求头部信息
    :param raise_exc: 是否抛出异常，默认为True
    :param roles: 该请求的应有的权限
    :return: 返回具有该访问凭证的用户信息对象
    :raises: Exception, 当访问凭证不存在或无效时，如果raise_exc=True就会抛出异常
    """
    token = req.headers.get('Authorization')  # 获取请求头部中的"Authorization"字段值

    if token is None:
        if raise_exc:
            raise NetworkException(401, '访问凭证不存在，无法进行访问')
        else:
            return None

    # 检查访问凭证是否有效
    check_tokens_reponse_if_not200(token, roles)

    # print(f'[DEBUG] check_user_before_request -> token = {token}')
    # 经过check_token_response_if_not_200的检查，可以保证token是存在的，且本次访问符合对应的权限
    user = get_user_by_token(token)  # 根据访问凭证获取对应的用户信息对象
    # print(f'[DEBUG] check_user_before_request -> user[id] = {user["id"]}')
    return user


def random_gen_str(strlen=14) -> str:
    char_list = 'qwertyuiopasdfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM_'
    res = ''
    for _ in range(strlen):
        res += char_list[random.randint(0, len(char_list) - 1)]
    return res


def random_gen_username():
    return random_gen_str()


def get_user_by_id(userId: int) -> dict:
    return execute_sql_query_one(pooldb,'select id, userName, roles, email, phoneNumber, avator from users where id = %s ', int(userId))


USER_ROLE_MAP = {
    "common": "普通用户",
    "manager": "管理员",
    "admin": "超级管理员"
}
