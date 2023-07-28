import inspect
import traceback

import pymysql.cursors
from readio.utils.executeSQL import execute_sql_query, execute_sql_query_one


def printException(e):
    print(f"[ERROR]{__file__}::{inspect.getframeinfo(inspect.currentframe().f_back)[2]} \n {e}")
    # print(f"[ERROR] {e.with_traceback()}")


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def checkRequestSingleKeyWithCondition(req: dict, keyName: str, condition: str) -> bool:
    """
    取出req[keyName], 其值会被替代为condition中的#?#检查
    """
    try:
        if keyName not in req:
            raise Exception("key不存在")
        val = req[keyName]
        condition = condition.replace("#?#", f"{val}")
        return eval(condition)

    except Exception as e:
        printException(e)
        return False


def checkRequestMultipleKeysWithCondition(req: dict, keyNameList: list, condition: str) -> list:
    res = []
    for keyName in keyNameList:
        res.append(checkRequestSingleKeyWithCondition(req=req, keyName=keyName, condition=condition))
    return res


def checkRequestMultipleKeysWithCondition(req: dict, keyDefineList: list) -> list:
    res = []
    for keyName, condition in keyDefineList:
        res.append(checkRequestSingleKeyWithCondition(req=req, keyName=keyName, condition=condition))
    return res


def checkRequstIsNotNone(req: dict, keyName: str):
    if keyName not in req:
        return False

    if req[keyName] is None:
        return False

    return True


# req = {"name":"ziyang","phoneNumber":"18314266702","age":18}
# print(checksRequestSingleKeyWithCondition(req,"name","'#?#' < 20"))
# print(checksRequestSingleKeyWithCondition(req,"age","#?# < 20"))
# print(checksRequestSingleKeyWithCondition(req,"name","'#?#' == 'ziyang'"))
# print(checksRequestSingleKeyWithCondition(req,"name","'#?#' != None and len('#?#') > 5 and len('#?#') < 13"))


# ========== appBook.: 工具函数 ==========

# 检查用户 uid 的书架上是否有书 bid
# 注意：这里未检查用户是否有凭证，可以配合使用 check_user_before_request
def check_book_added(pooldb, uid, bid, added=1):
    """ 判断用户 uid 的书架是否有书籍 bid """
    try:
        check_book_sql = "SELECT COUNT(*) FROM user_read_info WHERE userId=%s AND bookId=%s AND added>=%s"
        args = uid, bid, int(added)
        book_count = execute_sql_query_one(pooldb, check_book_sql, args)
        # book_count = {'COUNT(*)': 1}
        return book_count['COUNT(*)'] > 0
    except pymysql.Error as e:
        print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        # raise
        raise Exception("Error occurred while checking book added: " + str(e))


def check_book_read(pooldb, uid, bid):
    """ 判断用户 uid 的是否读过书籍 bid """
    return check_book_added(pooldb, uid, bid, added=0)


def check_book_liked(pooldb, uid, bid):
    """ 判断用户 uid 是否点赞书籍 bid """
    try:
        check_like_sql = "SELECT COUNT(*) FROM book_likes WHERE userId=%s AND bookId=%s"
        args = uid, bid
        like_count = execute_sql_query_one(pooldb, check_like_sql, args)
        # 根据查询结果，判断用户是否点赞
        return like_count['COUNT(*)'] > 0
    except pymysql.Error as e:
        print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        # raise
        raise Exception("Error occurred while checking book liked: " + str(e))


def check_comment_liked(pooldb, uid, cid):
    """ 判断用户 uid 是否点赞评论 cid """
    try:
        # 构造 SQL 查询语句
        check_like_sql = "SELECT COUNT(*) FROM comment_likes WHERE userId=%s AND commentId=%s"
        args = uid, cid
        # 执行 SQL 查询，并获取结果
        like_count = execute_sql_query_one(pooldb, check_like_sql, args)
        # like_count = {'COUNT(*)': 1}
        # 根据查询结果，判断用户是否点赞了该评论
        return like_count['COUNT(*)'] > 0
    except pymysql.Error as e:
        print("[ERROR]" + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        # raise
        raise Exception("Error occurred while checking comment liked: " + str(e))


# 注意：这里未检查用户是否有凭证，可以配合使用 check_user_before_request
def check_has_comment(pooldb, uid, cid):
    """ 判断用户 uid 是否有评论 cid """
    try:
        check_comment_sql = "SELECT COUNT(*) FROM comments WHERE userId=%s AND commentId=%s"
        args = uid, cid
        comment_count = execute_sql_query_one(pooldb, check_comment_sql, args)
        return comment_count['COUNT(*)'] > 0
    except Exception as e:
        print("[ERROR] " + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        raise Exception("Error occurred while checking the comment: " + str(e))


def check_exist_comment(pooldb, cid):
    """ 判断评论 cid 是否存在 """
    try:
        check_comment_sql = "SELECT COUNT(*) FROM comments WHERE commentId=%s"
        args = cid
        comment_count = execute_sql_query_one(pooldb, check_comment_sql, args)
        return comment_count['COUNT(*)'] > 0
    except Exception as e:
        print("[ERROR] " + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        raise Exception("Error occurred while checking the comment: " + str(e))


def check_exist_comment_for_book(pooldb, bid, cid):
    """ 判断表 comment_book(bookId,commentId) 中该书 (bid) 是否有评论 (cid) """
    try:
        check_sql = "SELECT COUNT(*) FROM comment_book WHERE bookId=%s AND commentId=%s"
        args = bid, cid
        count = execute_sql_query_one(pooldb, check_sql, args)
        return count['COUNT(*)'] > 0
    except Exception as e:
        print("[ERROR] " + __file__ + "::" + inspect.getframeinfo(inspect.currentframe().f_back)[2])
        print(e)
        raise Exception("Error occurred while checking the comment: " + str(e))
