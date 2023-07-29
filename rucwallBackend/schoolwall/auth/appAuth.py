import functools
from typing import List

from flask import request
from flask import Blueprint
from flask import redirect
from flask import url_for
from werkzeug.security import check_password_hash, generate_password_hash
from schoolwall.utils.buildResponse import *
from schoolwall.utils.auth import *
import schoolwall.database.connectPool
import schoolwall.utils.check as check
from schoolwall.utils.executeSQL import execute_sql_query

# appAuth = Blueprint('/auth/app', __name__)
bp = Blueprint('auth', __name__, url_prefix='/auth')

pooldb = schoolwall.database.connectPool.pooldb

def authorize_username_password(username, passWord):
    try:
        conn, cursor = pooldb.get_conn()
        cursor.execute('select * from users where username=%s', (username))
        user = cursor.fetchone()
        pooldb.close_conn(conn, cursor)
        if user is None:
            raise Exception('用户名不正确')

        if not check_password_hash(user['password'], passWord):
            raise Exception('密码不正确')

        # 都正确了，开始创建会话
        print('验证成功')
        return user
    except Exception as e:
        check.printException(e)
        pooldb.close_conn(conn, cursor) if conn is not None else None
        return None


def authorize_userId_password(userId, passWord):
    try:
        conn, cursor = pooldb.get_conn()
        cursor.execute('select * from users where id=%s', (userId))
        user = cursor.fetchone()
        pooldb.close_conn(conn, cursor)
        if user is None:
            raise Exception('用户名不正确')

        if not check_password_hash(user['passWord'], passWord):
            raise Exception('密码不正确')

        # 都正确了，开始创建会话
        print('验证成功')
        return user
    except Exception as e:
        check.printException(e)
        pooldb.close_conn(conn, cursor) if conn is not None else None
        return None


# 用户注册的sql语句, 默认的用户名随机生成，用户用phoneNumber和password注册
def register_user_sql(password, username):
    sql = ' insert into users(username,password,roles) values(%s,%s,%s) '
    return execute_sql_write(pooldb, sql, (username, generate_password_hash(password), 'common'))


# 检查phoneNumber是不是唯一的，如果是则返回True，否则返回False
def checkUsernameIsUnique(username):
    rows = execute_sql_query(pooldb, ' select * from users where username=%s ', (username))
    if (len(rows) == 0):
        return True
    return False

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        if 'username' not in data or 'password' not in data:
            raise Exception('前端数据错误！缺少username或password')

        if not checkUsernameIsUnique(data['username']):
            return build_error_response(msg='该用户名已被注册')

        register_user_sql(data['password'], data['username'])

        return build_success_response()


    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


# 收到用户名密码，返回会话对应的toKen
@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        if 'username' not in data or 'password' not in data:
            raise Exception('前端数据不正确，username或password')
        username = data['username']

        password = data['password']
        user = authorize_username_password(username, password)
        if user is None:
            return build_error_response(msg='用户名或密码错误')

        token = build_session(user['id'])
        print('[DEBUG] get token, token = ', token)
        # tokenList.append(token)
        return build_success_response({"token": token})


    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


# 退出登录，本质上就是删除与用户建立的对话
@bp.route('/logout', methods=['GET'])
def logout():
    try:
        token = request.headers.get('Authorization')
        if token is None:
            return build_success_response()
        conn, cursor = pooldb.get_conn()
        cursor.execute('delete from user_token where token=%s', (token))
        conn.commit()
        pooldb.close_conn(conn, cursor)
        return build_success_response()

    except Exception as e:
        check.printException(e)
        pooldb.close_conn(conn, cursor) if conn is not None else None
        return build_error_response()

# 获取用户详细信息
@bp.route('/profile', methods=['GET'])
def profile():
    try:
        if request.method == 'GET':
            user = check_user_before_request(request)

            response = {
                "userInfo": {
                    "userId": user['id'],
                    "username": user['username'],
                    "roles": user['roles'],
                }
            }

            return build_success_response(response)

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)
    except Exception as e:
        check.printException(e)
        return build_error_response()


def user_profile_update_user_pwd(uid, pwd):
    try:
        sql = 'update users set password=%s where id=%s'
        conn, cursor = pooldb.get_conn()
        cursor.execute(sql, (generate_password_hash(pwd), uid))
        conn.commit()
        pooldb.close_conn(conn, cursor)
    except Exception as e:
        check.printException(e)
        pooldb.close_conn(conn, cursor) if conn is not None else None
        raise Exception(f'用户{uid}密码修改失败')


@bp.route('/profile/updatePwd', methods=['POST'])
def updatePwd():
    try:
        data = request.json
        if 'oldPassword' not in data or 'newPassword' not in data:
            raise NetworkException(400, '前端数据错误，不存在oldPassword或newPassword')

        user = check_user_before_request(request)

        res = authorize_userId_password(user['id'], data['oldPassword'])
        if res is None:
            raise NetworkException(400, '密码不正确')

        user_profile_update_user_pwd(user['id'], data['newPassword'])

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)
    except Exception as e:
        check.printException(e)
        return build_error_response(500, "服务器内部错误")