"""
该文件包含的函数主要功能是构造response
"""
import json
from flask import make_response
from flask import jsonify


def build_response(code: int, msg: str, data=None, length=0):
    if data is None:
        data = {}
    if length == 0:
        length = len(data)
    # return make_response(json.dumps({'code': code, 'msg': msg, 'data': data, 'length': length}), code)
    return make_response(jsonify({'code': code, 'msg': msg, 'data': data, 'length': length}), code)


def build_error_response(code=400, msg='操作失败'):
    return build_response(code, msg)


def build_success_response(data=None, msg='操作成功', length=0):
    return build_response(code=200, msg=msg, data=data, length=length)


def build_404_response():
    build_response(404, '不存在')


def build_redirect_response(msg: str, url: str):
    url_data = dict({'Location': url})
    return build_response(302, msg, url_data)


def build_method_error_response(code=405, msg='Method Not Allowed', method=None):
    if method is None:
        method = 'Please check the api'
    return build_response(code, msg, method)


# 不建议用这个
def build_raw_response(response):
    return json.dumps(response)
