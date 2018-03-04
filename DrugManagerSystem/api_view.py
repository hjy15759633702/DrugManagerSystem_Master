#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/3 16:01
# @Author  : hjy
# @File    : api_view.py.py
# api接口风格

from flask import Blueprint, request
from flask import jsonify

api = Blueprint('api', __name__)

@api.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return jsonify({'code': 0, 'msg': '请求方法不对!', 'data': ''})
    return jsonify({'code': 1, 'msg': 'hjy', 'data': 'hjy'})