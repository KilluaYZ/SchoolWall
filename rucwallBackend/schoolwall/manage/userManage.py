from typing import Any

from flask import request
from flask import Blueprint
import os
import sys
import inspect
import hashlib

from werkzeug.security import check_password_hash, generate_password_hash

from schoolwall.utils import check
from schoolwall.utils.buildResponse import *
from schoolwall.utils.check import is_number
from schoolwall.utils.auth import check_tokens_get_state, check_user_before_request, USER_ROLE_MAP, get_user_by_id
from schoolwall.utils.executeSQL import *
from schoolwall.utils.myExceptions import NetworkException


# conndb = Conndb(cursor_mode='dict')
bp = Blueprint('user', __name__, url_prefix='/user')

import readio.database.connectPool

pooldb = readio.database.connectPool.pooldb


def query_user_sql(queryParam):
    # 假设queryParam是绝对正确的，本函数就忽略对queryParam的正确性检验，将注意力集中在功能上
    try:
        # print('queryParam : ',queryParam)
        conn, cursor = pooldb.get_conn()
        if 'userName' in queryParam:
            # username = '%'+queryParam['userName']+'%'
            # print(username)
            username = f'%{queryParam["userName"]}%'
            cursor.execute('select * from users where userName like %s', (username))
        else:
            cursor.execute('select * from users')
        rows = cursor.fetchall()

        return rows

    except Exception as e:
        check.printException(e)
        raise e

    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


@bp.route('/list', methods=['GET'])
def userList():
    try:
        check_user_before_request(request, roles='common')
        queryParam = request.args
        rows = query_user_sql(queryParam)
        data_length = len(rows)
        # print('debug',rows)
        # 构造前端所需数据
        pageSize = request.args.get('pageSize')
        pageNum = request.args.get('pageNum')
        if pageSize is not None and pageNum is not None:
            pageSize = int(pageSize)
            pageNum = int(pageNum)
            rows = rows[(pageNum - 1) * pageSize:pageNum * pageSize]

        response = []
        for row in rows:

            response.append({
                "userName": row['userName'],
                'userId': row['id'],
                "phoneNumber": row['phoneNumber'],
                'createTime': row['createTime'],
                'roles': USER_ROLE_MAP[row['roles']],
                'email': row['email']
            })

        return build_success_response(data=response, length=data_length)

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)
    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg="服务器内部错误")


def add_user_sql(data):
    try:
        # 假设data中的属性都是确定无误的
        sql = 'insert into users ('
        sql2 = ' values ('
        val_list = []
        data_key_val = list(data.items())
        for i in range(len(data_key_val) - 1):
            val_list.append(data_key_val[i][1])
            sql += " %s ," % (data_key_val[i][0])
            sql2 += "%s ,"

        val_list.append(data_key_val[-1][1])
        sql += "%s)" % (data_key_val[-1][0])
        sql2 += "%s)"
        sql += sql2
        # print("[DEBUG] insert sql=",sql)
        conn, cursor = pooldb.get_conn()
        cursor.execute(sql, tuple(val_list))
        conn.commit()

    except Exception as e:
        check.printException(e)
        if conn is not None:
            conn.rollback()
        raise e

    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


def check_if_phonenumber_is_unique(phoneNumber: str) -> bool:
    try:
        conn, cursor = pooldb.get_conn()
        cursor.execute(f'select * from users where phoneNumber = %s', phoneNumber)
        rows = cursor.fetchall()
        if len(rows) > 0:
            return False
        return True

    except Exception as e:
        check.printException(e)
        if conn is not None:
            conn.rollback()
        raise e

    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


@bp.route('/add', methods=['POST'])
def addUser():
    try:
        user = check_user_before_request(request, roles='admin')

        data = request.json
        if ('phoneNumber' not in data or 'passWord' not in data):
            raise NetworkException(code=400, msg="前端数据错误，请检查电话号码、密码是否设置正确")

        if not check_if_phonenumber_is_unique(data['phoneNumber']):
            raise NetworkException(code=400, msg="电话号码已被注册，请重试")

        user_add_data = {}

        for item in data.items():
            if item[0] == 'userName':
                user_add_data['userName'] = item[1]
            elif item[0] == 'roles':
                user_add_data['roles'] = item[1]
            elif item[0] == 'phoneNumber':
                user_add_data['phoneNumber'] = item[1]
            elif item[0] == 'email':
                user_add_data['email'] = item[1]
            elif item[0] == 'passWord':
                user_add_data['passWord'] = generate_password_hash(item[1])

        add_user_sql(user_add_data)

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg="服务器内部错误")


def user_manage_update_user_sql(data):
    # 假定data绝对正确
    # 暂不支持修改号码
    try:
        sql = 'update users set userName=%s, email=%s, passWord=%s, roles=%s where id=%s'

        conn, cursor = pooldb.get_conn()
        cursor.execute(sql, (data['userName'], data['email'],
                             generate_password_hash(data['passWord']), data['roles'], data['userId']))
        conn.commit()

    except Exception as e:
        check.printException(e)
        if conn is not None:
            conn.rollback()
        raise e
    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


@bp.route('/update', methods=['POST'])
def userUpdate():
    try:
        check_user_before_request(request, roles='admin')

        data = request.json
        if ('userId' not in data):
            raise Exception('前端数据不正确，重要数据缺失')

        user_manage_update_user_sql(data)

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg="服务器内部错误")


@bp.route('/get', methods=['GET'])
def getUser():
    try:
        # check_user_before_request(request, roles='admin')
        data = request.args
        if ('userId' not in data):
            raise NetworkException(400, '前端数据错误，无userId')

        user = get_user_by_id(data['userId'])
        if user is None:
            user = {}
        user['userId'] = user['id']
        return build_success_response(user)

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg="服务器内部错误")


@bp.route('/online/list', methods=['GET'])
def getOnlineUser():
    try:
        # pageNum = request.args.get('pageNum')
        # pageSize = request.args.get('pageSize')
        # if pageNum is None or pageSize is None:
        #     raise NetworkException(400, "前端数据错误，pageNum或pageSize不存在")

        check_user_before_request(request, roles='manager')

        userName = request.args.get('userName')
        if userName is None:
            rows = pooldb.read(
                'select token, userName ,roles,users.id as userId, user_token.createTime as loginTime from users, user_token where users.id=user_token.uid')

        else:
            conn, cursor = pooldb.get_conn()
            cursor.execute(
                'select token,userName ,roles,users.id as userId,user_token.createTime as loginTime from users, user_token where userName = %s and users.id=user_token.uid',
                (userName))
            rows = cursor.fetchall()
            pooldb.close_conn(conn, cursor)

        length = len(rows)
        # rows = rows[(pageNum-1)*pageSize:pageNum*pageSize]


        return build_success_response(data=rows, length=length)

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)

        if conn is not None:
            pooldb.close_conn(conn, cursor)

        return build_error_response(code=500, msg="服务器内部错误")


@bp.route('/online/forceLogout', methods=['POST'])
def forceLogout():
    try:
        check_user_before_request(request, roles='admin')

        token = request.json.get('token')
        if token is None:
            raise NetworkException(code=400, msg=f"前端数据错误，token{token}不存在")

        conn, cursor = pooldb.get_conn()
        cursor.execute('delete from user_token where token=%s', token)
        conn.commit()
        pooldb.close_conn(conn, cursor)

        return build_success_response()


    except NetworkException as e:

        return build_error_response(code=e.code, msg=e.msg)


    except Exception as e:

        check.printException(e)

        if conn is not None:
            pooldb.close_conn(conn, cursor)

        return build_error_response(code=500, msg="服务器内部错误")


from readio.auth.appAuth import user_profile_update_user_pwd


@bp.route('/resetPwd', methods=['POST'])
def resetPwd():
    try:
        check_user_before_request(request, roles='admin')

        userId = request.json.get('userId')
        passWord = request.json.get('passWord')
        if userId is None or passWord is None:
            raise NetworkException(code=400, msg="前端数据中不包含userId或passWord")
        user_profile_update_user_pwd(userId, passWord)

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg="服务器内部错误")


def user_manage_del_user(uid):
    try:
        conn, cursor = pooldb.get_conn()
        sql = 'delete from users where id=%s'
        cursor.execute(sql, uid)
        conn.commit()

    except Exception as e:
        check.printException(e)
        raise e
    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


@bp.route('/del', methods=['POST'])
def del_user():
    try:
        check_user_before_request(request, roles='admin')

        userId = request.json.get('userId')
        if userId is None:
            raise NetworkException(code=400, msg="前端数据中不包含userId")
        if isinstance(userId, list):
            for user in userId:
                user_manage_del_user(user)
        else:
            user_manage_del_user(userId)

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg="服务器内部错误")


# 每过一段时间，都会检查一遍user_token表，看createTime和visitTime之差，如果二者之差>=30min，说明该用户已经长时间未进行操作了，应该该会话关闭
def checkSessionsAvailability():
    try:
        conn, cursor = pooldb.get_conn()
        cursor.execute('delete from user_token where timestampdiff(minute,visitTime,CURRENT_TIMESTAMP) >= 1440')
        conn.commit()

    except Exception as e:
        check.printException(e)
    finally:
        if conn is not None:
            pooldb.close_conn(conn, cursor)


# 用户关注
def __add_user_subscribe(followerId, authorId, trans=None):
    sql = 'insert into user_subscribe(followerId, authorId) values(%s, %s)'
    if trans is None:
        return execute_sql_write(pooldb, sql, (followerId, authorId))
    else:
        return trans.execute(sql, (followerId, authorId))


def __get_all_followerId_id_by_userid(userId) -> List[Dict]:
    """
    通过用户Id来获取该用户所有collect的pieces的id
    """
    sql = 'select followerId from user_subscribe where authorId=%s'
    rows = execute_sql_query(pooldb, sql, userId)
    rows = list(map(lambda x: int(x['followerId']), rows))
    return rows

def __get_all_authorId_id_by_userid(userId) -> List[Dict]:
    """
    通过用户Id来获取该用户所有collect的pieces的id
    """
    sql = 'select authorId from user_subscribe where followerId=%s'
    rows = execute_sql_query(pooldb, sql, userId)
    rows = list(map(lambda x: int(x['authorId']), rows))
    return rows

def __get_all_followers_obj_by_userid(userId) -> List[Dict]:
    """
    通过用户Id来获取该用户所有collect的pieces
    """
    sql = 'select users.id as id, users.userName as userName, ' \
          'users.roles as roles, users.phoneNumber as phoneNumber, ' \
          'users.avator as avator from users, user_subscribe ' \
          'where users.id=user_subscribe.followerId ' \
          'and user_subscribe.authorId = %s order by user_subscribe.createTime desc'
    return execute_sql_query(pooldb, sql, userId)

def __get_all_authors_obj_by_userid(userId) -> List[Dict]:
    """
    通过用户Id来获取该用户所有collect的pieces
    """
    sql = 'select users.id as id, users.userName as userName, ' \
          'users.roles as roles, users.phoneNumber as phoneNumber, ' \
          'users.avator as avator from users, user_subscribe ' \
          'where users.id=user_subscribe.authorId ' \
          'and user_subscribe.followerId = %s order by user_subscribe.createTime desc'
    return execute_sql_query(pooldb, sql, userId)

def __check_id_user_has_subscribed_the_author(followerId, authorId) -> bool:
    followerId = int(followerId)
    authorId = int(authorId)
    if followerId == authorId:
        return True
    rows = __get_all_authorId_id_by_userid(followerId)
    if rows is not None and len(rows) and authorId in rows:
        return True
    return False


@bp.route('/subscribe/add', methods=['GET'])
def add_user_subscribe():
    """
    关注用户
    """
    try:
        authorId = request.args.get("userId")
        if authorId is None:
            raise NetworkException(400, "前端数据缺失，缺少authorId")

        user = check_user_before_request(request)
        userId = int(user['id'])
        authorId = int(authorId)
        print(f'[DEBUG] userId={userId}, authorId={authorId}')
        if userId == authorId:
            raise NetworkException(400, "不能自己关注自己奥！")

        if not __check_id_user_has_subscribed_the_author(userId, authorId):
            # 还没有点赞过
            __add_user_subscribe(userId, authorId)

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


def __del_user_subscribe(followerId, authorId, trans=None):
    sql = 'delete from user_subscribe where followerId=%s and authorId=%s'
    if trans is None:
        return execute_sql_write(pooldb, sql, (followerId, authorId))
    else:
        return trans.execute(sql, (followerId, authorId))


@bp.route('/subscribe/del', methods=['GET'])
def del_user_subscribe():
    """
    取关用户
    """
    try:
        authorId = request.args.get("userId")
        if authorId is None:
            raise NetworkException(400, "前端数据缺失，缺少piecesId")

        user = check_user_before_request(request)
        userId = user['id']
        __del_user_subscribe(userId, authorId)
        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


@bp.route('/subscribe/get/author', methods=['GET'])
def get_user_subscribe_author():
    """
    获取该用户关注的所有用户
    """
    try:
        user = check_user_before_request(request)
        userId = user['id']
        rows = __get_all_authors_obj_by_userid(userId)

        return build_success_response(data=rows, length=len(rows))

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')

@bp.route('/subscribe/get/follower', methods=['GET'])
def get_user_subscribe_follower():
    """
    获取该用户关注的所有粉丝
    """
    try:
        user = check_user_before_request(request)
        userId = user['id']
        rows = __get_all_followers_obj_by_userid(userId)

        return build_success_response(data=rows, length=len(rows))

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


def get_user_by_id_aux(userId: int, request=None):

    user = execute_sql_query_one(pooldb,
                                 'select id, userName, roles, email, phoneNumber, avator from users where id = %s ',
                                 int(userId))
    if user is None:
        return None

    user['isSubscribed'] = 0
    if request is not None:
        try:
            # 尝试获取user点赞信息
            follower = check_user_before_request(request)
            followerId = follower['id']
            if __check_id_user_has_subscribed_the_author(followerId, userId):
                user['isSubscribed'] = 1

        except NetworkException:
            print("用户未登录或不存在，不返回点赞收藏信息")
        except Exception as e:
            raise e

    return user
