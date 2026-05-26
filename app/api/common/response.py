#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/7/29 上午12:02
# @Software：PyCharm
# @Author  : scott

from flask_restful import marshal

from app.api.common.fields import common_fields


class CommonResponse(object):
    def __init__(self, status=u'success', resid=200, msg=u'', data=None):
        self.status = status
        self.data = data
        self.resid = resid
        self.msg = msg

    def set_status(self, status=u'success'):
        self.status = status

    def set_resid(self, resid=200):
        self.resid = resid

    def set_msg(self, msg=''):
        self.msg = msg

    def set_data(self, data=None):
        self.data = data


def success(resid=200, msg=u'请求成功', status=u'success', data_fileds=None, data=None):
    """
    成功的业务处理结果
    :param status: 处理结果状态
    :param resid: 错误码
    :param msg: 错误码描述
    :param data_fileds: 数据字段
    :param data: 数据
    :return:
    """
    res_data = CommonResponse(status=status, resid=resid, msg=msg, data=data)
    fields = data_fileds if data_fileds else common_fields()
    return marshal(data=res_data, fields=fields), 200


def error(resid=100, msg=u'请求失败', status=u'error', data_fileds=None, data=None):
    """
    失败的业务处理结果
    :param status: 处理结果状态
    :param resid: 错误码
    :param msg: 错误码描述
    :param data_fileds: 数据字段
    :param data: 数据
    :return:
    """
    res_data = CommonResponse(status=status, resid=resid, msg=msg, data=data)
    fields = data_fileds if data_fileds else common_fields()
    return marshal(data=res_data, fields=fields), 200
