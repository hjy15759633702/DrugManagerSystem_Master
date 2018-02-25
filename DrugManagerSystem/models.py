#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/15 17:53
# @Author  : hjy
# @File    : models.py
# 数据模型

from exts import db
from datetime import datetime
# 用户信息
# 用户编号 id
# 用户电话 telephone
# 用户账号 username
# 用户密码 password
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    telephone = db.Column(db.String(11), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# 药品信息 drug
# 药品     id  主键
# 药品编号 num
# 药品名称 name
# 药品库存数量 count
# 药品出售数量 saleCount
# 药品价格 price
# 药品描述 desc
# 药品类别编号  外键 drugTypeId
# 进货编号 外键 stockId
# 选购编号 外键 saleId
class Drug(db.Model):
    __tablename__ = 'drug'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    num = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    count = db.Column(db.Integer(), nullable=False)
    saleCount = db.Column(db.Integer(), nullable=False, default=0)
    price = db.Column(db.REAL(), nullable=False, default=0)
    desc = db.Column(db.String(500), nullable=False)
    # 关联药品类别表id
    drugTypeId = db.Column(db.Integer(), db.ForeignKey('drugType.id'))
    drugType = db.relationship('DrugType', backref='drug')

# 药品类别 drugType
# 类别编号 id
# 类别名称 name
class DrugType(db.Model):
    __tablename__ = 'drugType'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

# 进货表 stock
# 进货编号 id
# 进货时间 stockDate
# 进货价格 stockPrice
# 进货数量 stockCount
# 进货总金额 stockMoney
# 进货人编号 外键 userId
class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    stockDate = db.Column(db.DateTime(), nullable=False, default=datetime.now)
    stockPrice = db.Column(db.REAL(), nullable=False)
    stockCount = db.Column(db.Integer(), nullable=False)
    stockMoney = db.Column(db.REAL(), nullable=False)
    # 关联药品表id
    drugId = db.Column(db.Integer(), db.ForeignKey('drug.id'))
    drug = db.relationship('Drug', backref='stock')
    # 关联用户表id
    userId = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user = db.relationship('User', backref='stock')

# 选购表 sale
# 选购编号 id
# 选购时间 time
# 选购数量 saleCount
# 选购总价 saleMoney
# 选购人编号 外键 userId
# 结账编号 外键accountId
class Sale(db.Model):
    __tablename__ = 'sale'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    time = db.Column(db.DateTime(), nullable=False, default=datetime.now)
    saleCount = db.Column(db.Integer(), nullable=False)
    saleMoney = db.Column(db.REAL(), nullable=False)
    # 关联用户表id
    userId = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user = db.relationship('User', backref='sale')
    # 关联结账表id
    accountId = db.Column(db.Integer(), db.ForeignKey('account.id'))
    account = db.relationship('Account', backref='sale')
    # 关联药品表id
    drugId = db.Column(db.Integer(), db.ForeignKey('drug.id'))
    drug = db.relationship('Drug', backref='sale')

# 结账表 account
# 结账编号 id
# 交易流水号 accountNo
# 结账时间 time
# 结账总价 accountMoney
# 结账人编号 外键 userId
class Account(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    # 结账流水号 后期银行对接  可以用上 先架构着  默认是8个0
    accountNo = db.Column(db.String(50), nullable=False, default='00000000')
    # 结账时间
    time = db.Column(db.DateTime(), nullable=False, default=datetime.now)
    accountMoney = db.Column(db.REAL(), nullable=False, default=0)
    # 关联用户表id
    userId = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user = db.relationship('User', backref='account')