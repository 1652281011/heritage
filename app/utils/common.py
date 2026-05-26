#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/30 上午8:30
# @Software：PyCharm
# @Author  : scott
import datetime
# import urllib
import random
from hashlib import md5
import socket
from urllib import request as urllib_request, error as urllib_error, parse as urllib_parse

mp3_url_head="https://cocos-resources-1309764129.cos.ap-nanjing.myqcloud.com/yscp_voice/"


# md5加密
def md5_str(parm):
    if isinstance(parm, str):
        parm = parm.encode('utf8')
    return md5(parm).hexdigest()


# 将时间对象转换为字符串格式
def time_to_str(parm=None, only_date=False, time=''):
    if parm is None:
        parm = datetime.datetime.now()
    try:
        if only_date:
            return datetime.datetime.strftime(parm, '%Y-%m-%d')
        if time:
            return datetime.datetime.strftime(parm, time)
        return datetime.datetime.strftime(parm, '%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(e)
        return ''


# 字符串格式转时间对象
def str_to_time(parm=None, only_date=False):
    if parm is None:
        return ''
    try:
        time_tuple = datetime.datetime.strptime(parm, '%Y-%m-%d %H:%M:%S')
        if only_date:
            return datetime.datetime.strftime(time_tuple, '%Y-%m-%d')
        return datetime.datetime.strftime(time_tuple, '%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(e)
    return ''


# 输入日期名词返回对应的开始时间和结束时间
def date_name_to_time(data_name):
    """
    输入日期名词返回对应的开始时间和结束时间
    :param data_name: today, yesterday, week, month
    :return: start_time, end_time
    """
    start_time = end_time = datetime.datetime.now()

    if data_name == 'today':
        start_time = end_time.replace(hour=0, minute=0, second=0, microsecond=0)
    elif data_name == 'yesterday':
        end_time = end_time.replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = end_time - datetime.timedelta(days=1)
    elif data_name == 'week':
        start_time = end_time - datetime.timedelta(days=7)
    elif data_name == 'month':
        start_time = end_time - datetime.timedelta(days=30)

    return start_time, end_time


def get_age(birthday):
    """
    获取年龄
    :param birthday: str 出生日期 '2021-10-11'
    :return: 年龄
    """
    now = datetime.datetime.now()
    birthday = datetime.datetime.strptime(birthday, '%Y-%m-%d')

    year_difference = now.year - birthday.year
    if now.month < birthday.month:
        year_difference -= 1
    elif now.month == birthday.month:
        if now.day < birthday.day:
            year_difference -= 1
    return year_difference


def seconds_to_minute(seconds):
    """
    将秒转为时分秒
    :param seconds: int 秒
    :return: 时间字符串
    """
    if seconds >= 60 * 60:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        value = "%02d:%02d:%02d" % (h, m, s)
    else:
        m, s = divmod(seconds, 60)
        value = "%02d:%02d" % (m, s)

    return value


def urllib_get(url, num_retries=2):
    """发送GET请求"""
    try:
        res = urllib_request.urlopen(url).read()
    except urllib_error.URLError as e:
        res = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return urllib_get(url, num_retries - 1)
    return res


def urllib_post(url, data, num_retries=2):
    """发送POST请求"""
    data = urllib_parse.urlencode(data)
    data = data.encode('ascii')
    try:
        res = urllib_request.urlopen("http://requestb.in/xrbl82xr", data).read().deconde('utf-8')
    except urllib_error.URLError as e:
        res = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return urllib_post(url, num_retries - 1)
    return res


def create_id_no(count=12):
    """
    生成随机id编号,用于url内
    依次生成1000个放到redis中，获取时候依次获取
    如果没有长度小于等于5的时候就再次生成
    """
    from app import redis_store
    random_nos = redis_store.smembers(f'random_no_{count}')
    if len(random_nos) <= 5:
        for i in range(1000):
            value = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz0123456789', count))
            redis_store.sadd(f'random_no_{count}', value)
    return redis_store.spop(f'random_no_{count}')

def get_host_ip():
    """
    查询本机局域网IP地址
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 这一步并不真正建立连接，只是为了探测本机出口IP
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip