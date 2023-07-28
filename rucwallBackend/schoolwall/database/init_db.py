from flask import Flask
from flask import request
from flask import Blueprint
from flask import current_app, g
from flask.cli import with_appcontext
import os
import sys
import click

import readio.database.connectPool
global pooldb
pooldb = readio.database.connectPool.pooldb

def init_db():
    print("暂时不支持创建数据库捏~ 数据库好好珍惜，不小心弄坏了就没有了捏")
    # print("开始创建数据库")
    # pooldb.execute_scirpt('schoolwall/database/init.sql')
    

