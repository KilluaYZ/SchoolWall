import json
# from dbtest.showdata10 import db # 引入其他蓝图
import re
from typing import Dict, Tuple, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, url_for
from flask_cors import CORS  # 跨域

# app
from schoolwall.auth import appAuth
from schoolwall.database.init_db import init_db
from schoolwall.manage import postManage, userManage
from schoolwall.utils.json import CustomJSONEncoder


# 创建flask app
def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)

    app.json_encoder = CustomJSONEncoder

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # 在应用中注册init_db
    @app.cli.command('init-db')
    def init_db_command():
        """删除现有的所有数据，并新建关系表"""
        init_db()

    app.register_blueprint(userManage.bp)
    app.register_blueprint(appAuth.bp)
    app.register_blueprint(postManage.bp)

    # 配置定时任务
    # 该任务作用是每个一个小时检查一次user_token表，将超过1天未活动的token删掉（随便定的，后面改
    from schoolwall.manage.userManage import checkSessionsAvailability
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=checkSessionsAvailability,
                      id='checkSessionsAvailability',
                      trigger='interval',
                      seconds=21600,
                      replace_existing=True
                      )
    # 启动任务列表
    scheduler.start()
    """ 测试 """
    # print(f'[TEST] filePath = {getFilePathById("0658a5df12791200a99b5e0f26b03e2d53154567c759683d7b355982cff124a6")}')
    # app_test(app)

    return app
