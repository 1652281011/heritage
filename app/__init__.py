#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/7/27 16:00 
# @Author : Scott
# @Software: PyCharm

from datetime import datetime, timedelta, date, time

from flask import Flask
from flask_migrate import Migrate
from flask_redis import FlaskRedis
from flask_restful import Api
from flask_socketio import emit, SocketIO  # 从'flask_socketio'模块中导入'socketio'对象


from flask_apscheduler import APScheduler
from app.config import config_dict
from app.models import db
from threading import Lock
from flask import Flask, render_template, session, request, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect,send

from flask import g, current_app, jsonify, request

redis_store = FlaskRedis(decode_responses=True)
migrate = Migrate()
app_api = Api()

async_mode = None
# socketio = SocketIO(app, async_mode=async_mode)
# socketio.init_app(app, cors_allowed_origins='*')

scheduler = APScheduler()
# 初始化 SocketIO
socketio = SocketIO()
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])

    db.app = app
    db.init_app(app)
    migrate.init_app(app, db)
    redis_store.init_app(app)

    register_blueprints(app=app)
    app_api.app = app
    configure_resources(app_api)
    configure_logger(app=app)

    app.config['SCHEDULER_EXECUTE_IN_APP_CONTEXT'] = True
    # 初始化 APScheduler
    scheduler.init_app(app)

    scheduler.start()

    @app.before_request
    def before_request_handler():
        """
        全局拦截器：在每个请求进入逻辑前运行。
        它负责从 Postman/前端发送的 Headers 中提取数据并存入 g。
        """
        # 注意：这里的 Key 必须和 Postman Headers 里的 Key 完全一致
        g.auth_token = request.headers.get('auth-token')
        g.api_type = request.headers.get('api-type', 'user')
        g.app_type = request.headers.get('app-type', 'web')
        # g.current_user_id = request.headers.get('Current-User-Id')
        print(f"Token is: {g.auth_token}")




    # app.logger.warning("config_dict[config_name]:"+str(config_dict[config_name]))
    # app.logger.w
    # app.logger.info("current_app.config['WX_APPLET_ID']:"+current_app.config['WX_APPLET_ID'])
    # socketio.init_app(app=app, async_mode=async_mode)  # 新添加的代码
    # socketio.init_app(app=app, cors_allowed_origins='*')
    return app



# 注册蓝图
def register_blueprints(app):
    from .view import blueprints as view_bp
    for view, url_prefix in view_bp:
        app.register_blueprint(view, url_prefix=url_prefix)



def configure_resources(app_api):
    from app.api import RESOURCES
    for resource, prefix in RESOURCES:
        app_api.add_resource(resource, prefix)


# 注册日志
def configure_logger(app):
    import os
    import time
    import logging

    format_str = '%(asctime)s %(levelname)s in %(pathname)s:%(lineno)d :\n%(message)s'
    formatter = logging.Formatter(format_str)

    # 日志文件路径设置
    logfile_path = app.config['LOGFILE_PATH']
    if not os.path.exists(logfile_path):
        try:
            os.mkdir(logfile_path)
        except Exception as e:
            print(e)
            return
    logfile_name = "XINLS_{}.log".format(time.strftime('%Y%m%d', time.localtime(time.time())))
    logfile = os.path.join(logfile_path, logfile_name)

    logfile_handler = logging.FileHandler(logfile)
    if app.config["LOG_LEVEL"]:
        log_level = app.config["LOG_LEVEL"]
    else:
        if app.config["DEBUG"]:
            log_level = logging.DEBUG
        else:
            log_level = logging.WARNING

    logfile_handler.setLevel(log_level)
    logfile_handler.setFormatter(formatter)
    app.logger.addHandler(logfile_handler)
    app.logger.info("------boot--------")

thread = None
thread_lock = Lock()

# @socketio.on('tos', namespace='/chat')
# def channel(message):
#     emit('froms', {'data': message}, broadcast=True)
#     socketio.emit('froms',{'data':message})
@socketio.on('tos', namespace='/mp')
def toss1(aaa):
    # socketio.send(message,False)
    # socketio.emit('froms', aaa)#收不到数据
    # socketio.emit('froms', message, broadcast=True)
    # socketio.emit('froms', aaa, namespace='/chat',broadcast=True)#收不到数据
    #
    #
    emit('froms', aaa,broadcast=True)
    socketio.sleep(1)
@socketio.on('tos', namespace='/chat')
def toss(aaa):
    # socketio.send(message,False)
    # socketio.emit('froms', aaa)#收不到数据
    # socketio.emit('froms', message, broadcast=True)
    # socketio.emit('froms', aaa, namespace='/chat',broadcast=True)#收不到数据
    #
    #
    emit('froms', aaa,broadcast=True)
    socketio.sleep(1)
    #
    # send(aaa,broadcast=True)

    # session['receive_count'] = session.get('receive_count', 0) + 1
    # emit('my_response',
    #      {'data': message['data'], 'count': session['receive_count']})
    # emit("my_event celled")
@socketio.on('message_from_client')
def handle_message(message):
    print('Received message:', message)
    emit('message_from_server', {'data': 'Message received'})

@socketio.event
def my_broadcast_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1

    emit('my_response',message,broadcast=True)

#    emit('my_response',
#         {'data': message['data'], 'count': session['receive_count']},
#         broadcast=True)



@socketio.event
def join(message):
    emit('my_response',message['room'],broadcast=True)
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1

    emit('my_response',message['room'],broadcast=True)
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.event
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room')
def on_close_room(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         to=message['room'])
    close_room(message['room'])


@socketio.event
def my_room_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         to=message['room'])





# @socketio.event
@socketio.on('connect', namespace='/chat')
def connect():
    global thread
    # with thread_lock:
    #     if thread is None:
    #         thread = socketio.start_background_task(background_thread)
    #         print("222")
    emit('my_response', {'data': 'Connected', 'count': 0})
    print("111")
    emit('my_response', {'data': '您好！连接成功'})
    print("333")
    send("ccccc",broadcast=True)
    socketio.start_background_task(threadFunc)
#
@socketio.on('connect', namespace='/mp')
def connect1():
    global thread
    # with thread_lock:
    #     if thread is None:
    #         thread = socketio.start_background_task(background_thread)
    #         print("222")
    emit('my_response', {'data': 'Connected', 'count': 0})
    print("111")
    emit('my_response', {'data': '您好！连接成功'})
    print("333")
    send("ccccc",broadcast=True)
    socketio.start_background_task(threadFuncmp)
def threadFunc():
    while(True):
        emit("response")
        socketio.sleep(1)
def threadFuncmp():
    while(True):
        emit("response")
        socketio.sleep(1)
@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)

# def background_thread():
#     """Example of how to send server generated events to clients."""
#     count = 0
#     # while True:
#     #     socketio.sleep(10)
#     #     count += 1
#     #     socketio.emit('my_response',
#     #                   {'data': 'Server generated event', 'count': count})