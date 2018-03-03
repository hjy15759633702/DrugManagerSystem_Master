#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/3 16:01
# @Author  : hjy
# @File    : api_view.py.py
# api接口风格

from flask import Blueprint
from flask import jsonify

api = Blueprint('api', __name__)

@api.route('/user')
def user():
    return jsonify({'code': 1, 'nickname': 'hjy', 'phone_number': 'hjy'})