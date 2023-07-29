"""
帖子管理
"""
import functools
import random
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
from schoolwall.utils.myExceptions import *
from schoolwall.utils.executeSQL import *
from schoolwall.manage.userManage import get_user_by_id_aux

bp = Blueprint('postManage', __name__, url_prefix='/post')

pooldb = schoolwall.database.connectPool.pooldb

def __query_post_sql(query_param: dict) -> List[Dict]:
    sql_select = ' select * from posts '
    args_str_list = []
    args_val_list = []

    if 'content' in query_param:
        args_str_list.append(f' and content like %s ')
        args_val_list.append(f'%{query_param["content"]}%')

    if 'postId' in query_param:
        args_str_list.append(f' and id = %s ')
        args_val_list.append(query_param['postId'])

    sql = sql_select
    if len(args_str_list):
        sql += ' where 1=1 '

    for item in args_str_list:
        sql += item

    sql += ' order by createTime desc '

    rows = execute_sql_query(pooldb, sql, tuple(args_val_list))

    return rows

def __get_liked_posts_sql(userId: str) -> List:
    sql = ' select postId from user_post_like where userId = %s '
    rows = execute_sql_query(pooldb, sql, (userId))
    rows = list(map(lambda x: x['postId'], rows))
    return rows

def __get_post_like_num(postId):
    sql = ' select count(*) from user_post_like where postId = %s '
    row = execute_sql_query_one(pooldb, sql, (postId))
    return int(row['count(*)'])

def __get_post_reply_num(postId):
    sql = ' select count(*) from reply where postId = %s '
    row = execute_sql_query_one(pooldb, sql, (postId))
    return int(row['count(*)'])

@bp.route('/list', methods=['GET'])
def post_list():
    """
    获取全部的帖子
    """
    try:
        rows = __query_post_sql({})
        for i in range(len(rows)):
            rows[i]['isLiked'] = False
            rows[i]['likeNum'] = __get_post_like_num(rows[i]['id'])
            rows[i]['replyNum'] = __get_post_reply_num(rows[i]['id'])
            rows[i]['isYours'] = False

        # 是否喜欢过
        common_user = check_user_before_request(request, False, 'common')
        if common_user is not None:
            liked_posts_ids = __get_liked_posts_sql(common_user['id'])
            print(f'[DEBUG] liked_posts_ids = {liked_posts_ids}')
            for i in range(len(rows)):
                if (rows[i]['id'] in liked_posts_ids):
                    print(f'[DEBUG] into iii')
                    rows[i]['isLiked'] = True

        if common_user is not None:
            # 是否属于你自己
            if common_user['roles'] == 'admin':
                for i in range(len(rows)):
                    rows[i]['isYours'] = True
            else:
                for i in range(len(rows)):
                    if (__check_if_post_belong_to_user(common_user['id'], rows[i]['id'])):
                        rows[i]['isYours'] = True


        return build_success_response(rows)

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')

@bp.route('/get', methods=['GET'])
def post_get():
    """
    获取全部的帖子
    """
    try:
        postId = request.args.get("postId")
        if postId is None:
            raise NetworkException(400, "前端数据错误，缺少postId")
        rows = __query_post_sql({'postId': postId})
        if rows is None or len(rows) == 0:
            raise NetworkException(404, "postId不存在")

        row = rows[0]
        row['isLiked'] = False
        row['likeNum'] = __get_post_like_num(row['id'])
        row['replyNum'] = __get_post_reply_num(row['id'])

        # 是否喜欢过
        common_user = check_user_before_request(request, False, 'common')
        if common_user is not None:
            liked_posts_ids = __get_liked_posts_sql(common_user['id'])
            if (row['id'] in liked_posts_ids):
                row['isLiked'] = True

        if common_user is not None:
            # 是否属于你自己
            if common_user['roles'] == 'admin':
                row['reply'] = get_reply_list_by_postId(row['id'], admin_user['id'], True)
            else:
                row['reply'] = get_reply_list_by_postId(row['id'], common_user['id'])

        return build_success_response(row)

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


def __add_post_sql(content, userId):
    sql = ' insert into posts(content, userId) values(%s, %s) '
    return execute_sql_write(pooldb, sql, (content, userId))

@bp.route('/add', methods=['POST'])
def post_add():
    """
    添加一个新的post
    """
    try:
        content = request.json.get("content")
        if content is None:
            raise NetworkException(400, "前端数据错误，缺少content")
        user = check_user_before_request(request)
        __add_post_sql(content, user['id'])

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


def __del_post_sql(postId):
    sql = ' delete from posts where id = %s '
    return execute_sql_write(pooldb, sql, (postId))


def __check_if_post_belong_to_user(userId, postId):
    sql = ' select * from posts where id = %s and userId = %s '
    rows = execute_sql_query(pooldb, sql, (postId, userId))
    if len(rows) > 0:
        return True
    return False

@bp.route('/del', methods=['GET'])
def post_del():
    """
    删除一个post
    """
    try:
        postId = request.args.get("postId")
        if postId is None:
            raise NetworkException(400, '前端缺少参数postId')
        user = check_user_before_request(request)
        if __check_if_post_belong_to_user(user['id'], postId):
            __del_post_sql(postId)
        else:
            user = check_user_before_request(request, roles='admin')
            __del_post_sql(postId)

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


def __add_post_like_sql(postId, userId):
    sql = ' insert into user_post_like(postId, userId) values(%s, %s) '
    return execute_sql_write(pooldb, sql, (postId, userId))

@bp.route('/like/add', methods=['GET'])
def post_like_add():
    """
    删除一个post
    """
    try:
        postId = request.args.get("postId")
        if postId is None:
            raise NetworkException(400, '前端缺少参数postId')
        user = check_user_before_request(request)
        __add_post_like_sql(postId, user['id'])

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


def __del_post_like_sql(postId, userId):
    sql = ' delete from user_post_like where postId = %s and userId = %s '
    return execute_sql_write(pooldb, sql, (postId, userId))

@bp.route('/like/del', methods=['GET'])
def post_like_del():
    """
    删除一个post
    """
    try:
        postId = request.args.get("postId")
        if postId is None:
            raise NetworkException(400, '前端缺少参数postId')
        user = check_user_before_request(request)
        __del_post_like_sql(postId, user['id'])

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')

#-----------------------------------reply-----------------------------------------------
def __query_reply_sql(postId) -> List[Dict]:
    sql = ' select * from reply where postId=%s order by createTime desc '

    rows = execute_sql_query(pooldb, sql, (postId))

    return rows

def __get_liked_reply_sql(userId: str) -> List:
    sql = ' select replyId from user_reply_like where userId = %s '
    rows = execute_sql_query(pooldb, sql, (userId))
    rows = list(map(lambda x:x['replyId'], rows))
    return rows

def __get_reply_like_num(replyId):
    sql = ' select count(*) from user_reply_like where replyId = %s '
    row = execute_sql_query_one(pooldb, sql, (replyId))
    return int(row['count(*)'])

def get_reply_list_by_postId(postId, userId, is_admin = False):
    rows = __query_reply_sql(postId)

    for i in range(len(rows)):
        rows[i]['isLiked'] = False
        rows[i]['likeNum'] = __get_reply_like_num(rows[i]['id'])
        rows[i]['isYours'] = False

    # 是否喜欢过
    liked_reply_ids = __get_liked_reply_sql(userId)
    for i in range(len(rows)):
        if (rows[i]['id'] in liked_reply_ids):
            rows[i]['isLiked'] = True

    # 是否属于你自己
    if is_admin:
        for i in range(len(rows)):
            rows[i]['isYours'] = True
    else:
        for i in range(len(rows)):
            if (__check_if_reply_belong_to_user(userId, rows[i]['id'])):
                row[i]['isYours'] = True
    return rows

def __add_reply_sql(content, userId, postId):
    sql = ' insert into reply(content, userId, postId) values(%s, %s, %s) '
    return execute_sql_write(pooldb, sql, (content, userId, postId))

@bp.route('/reply/add', methods=['POST'])
def reply_add():
    """
    添加一个新的post
    """
    try:
        content = request.json.get("content")
        postId = request.json.get("postId")
        if content is None or postId is None:
            raise NetworkException(400, "前端数据错误，缺少content或postId")
        user = check_user_before_request(request)
        __add_reply_sql(content, user['id'], postId)

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


def __del_reply_sql(postId):
    sql = ' delete from reply where id = %s '
    return execute_sql_write(pooldb, sql, (postId, userId))


def __check_if_reply_belong_to_user(userId, replyId):
    sql = ' select * from reply where id = %s and userId = %s '
    rows = execute_sql_query(pooldb, sql, (replyId, userId))
    if len(rows) > 0:
        return True
    return False
@bp.route('/reply/del', methods=['GET'])
def reply_del():
    """
    删除一个post
    """
    try:
        replyId = request.args.get("replyId")
        if replyId is None:
            raise NetworkException(400, '前端缺少参数replyId')
        user = check_user_before_request(request)
        if __check_if_reply_belong_to_user(user['id'], replyId):
            __del_reply_sql(replyId)
        else:
            user = check_user_before_request(request, roles='admin')
            __del_reply_sql(replyId)

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


def __add_reply_like_sql(replyId, userId):
    sql = ' insert into user_reply_like(replyId, userId) values(%s, %s) '
    return execute_sql_write(pooldb, sql, (replyId, userId))

@bp.route('/reply/like/add', methods=['GET'])
def reply_like_add():
    """
    删除一个post
    """
    try:
        replyId = request.args.get("replyId")
        if replyId is None:
            raise NetworkException(400, '前端缺少参数replyId')
        user = check_user_before_request(request)
        __add_reply_like_sql(replyId, user['id'])

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


def __del_reply_like_sql(replyId, userId):
    sql = ' delete from user_reply_like where replyId = %s and userId = %s '
    return execute_sql_write(pooldb, sql, (replyId, userId))

@bp.route('/reply/like/del', methods=['GET'])
def reply_like_del():
    """
    删除一个post
    """
    try:
        replyId = request.args.get("replyId")
        if replyId is None:
            raise NetworkException(400, '前端缺少参数replyId')
        user = check_user_before_request(request)
        __del_post_like_sql(reply, user['id'])

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')