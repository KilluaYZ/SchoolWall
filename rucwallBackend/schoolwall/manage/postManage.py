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

pooldb = readio.database.connectPool.pooldb

def __query_post_sql(query_param: dict) -> List[Dict]:
    sql_select = ' select * from post '
    args_str_list = []
    args_val_list = []

    if 'content' in query_param:
        args_str_list.append(f' and content like %s ')
        args_val_list.append(f'%{query_param["content"]}%')

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
    return rows

@bp.route('/list', methods=['GET'])
def post_list():
    """
    获取全部的帖子
    """

    try:
        rows = __query_post_sql({})
        for i in range(len(rows)):
            rows[i]['isLiked'] = false

        admin_user = check_user_before_request(request, 'admin')
        if admin_user is not None:
            for i in range(len(rows)):
                rows[i]['isLiked'] = true
        else:
            common_user = check_user_before_request(request, 'common')
            if common_user is not None:
                liked_posts_ids = __get_liked_posts_sql(common_user['id'])
                for i in range(len(rows)):
                    if(rows[i]['id'] in liked_posts_ids):
                        rows[i]['isLiked'] = true

        return build_success_response(rows)

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


def __add_post_sql(content, userId):
    sql = ' insert into post(content, userId) values(%s, %s) '
    return execute_sql_write(pooldb, sql, (content, userId))


@bp.route('/add', methods=['POST'])
def post_add():
    """
    添加一个新的post
    """
    try:
        content = request.json.get("content")
        user = check_user_before_request(request)
        __add_post_sql(content, user['id'])

        return build_success_response()

    except NetworkException as e:
        return build_error_response(code=e.code, msg=e.msg)

    except Exception as e:
        check.printException(e)
        return build_error_response(code=500, msg='服务器内部错误')


def __del_post_sql(postId, userId):
    sql = ' delete from post where id = %s and userId = %s '
    return execute_sql_write(pooldb, sql, (postId, userId))

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
        __del_post_sql(postId, user['id'])

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
def post_like_del():
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
