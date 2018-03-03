#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/15 12:55
# @Author  : hjy
# @File    : config.py
# 入口函数

from flask import Flask, render_template, request, url_for, redirect, session
import config
from models import User, Drug, DrugType, Sale, Account, Stock
from exts import db
from sqlalchemy import func, extract
import time
import datetime
from api_view import api

app = Flask(__name__)
app.config.from_object(config)
app.register_blueprint(api, url_prefix='/api')
db.init_app(app)

# 首页
@app.route('/')
def home():
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            drug_types = DrugType.query.all()
            drugs = Drug.query.all()
            return render_template('home.html', drugTypes=drug_types, drugs=drugs)
    return redirect(url_for('login'))

# 根据某个类别查询
@app.route('/drugType/<int:drugTypeId>/')
def drugType(drugTypeId):
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            drugTypes = DrugType.query.all()
            drugs = Drug.query.filter(Drug.drugTypeId == drugTypeId).all()
            return render_template('home.html', drugTypes=drugTypes, drugs=drugs, drugTypeId=drugTypeId)

    return redirect(url_for('login'))

# 登录
@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        checkbox = request.form.get('checkbox')
        user = User.query.filter(User.telephone == telephone, User.password == password).first()
        if user:
            session['user_id'] = user.id
            # 选中以后31天内不需要登录  cookie保存
            # if checkbox is not None and checkbox == 'remembered':
            session.permanent = True
            return redirect(url_for('home'))
        else:
            return u'手机号码或者密码错误，请确认后再登录！'


# 注册
@app.route('/regist/', methods=['POST', 'GET'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html', phoneTips='0', passwordTips='0')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password = request.form.get('password')
        password_again = request.form.get('password_again')

        user = User.query.filter(User.telephone == telephone).first()

        if user:
            return render_template('regist.html', phoneTips='1', passwordTips='0')
        else:
            if password != password_again:
                return render_template('regist.html', phoneTips='0', passwordTips='1')
            else:
                user = User(telephone=telephone, username=username, password=password)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))


# 添加药品
@app.route('/addDrug/', methods=['POST', 'GET'])
def addDrug():
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            if request.method == 'GET':
                return render_template('addDrug.html')
            else:
                num = request.form.get('num')
                name = request.form.get('name')
                type = request.form.get('type')
                count = request.form.get('count')
                price = request.form.get('price')
                desc = request.form.get('desc')
                # 首先查找药品是否存在
                drug = Drug.query.filter(Drug.num == num).first()

                # 如果存在
                if drug:
                    # 库存量增加
                    Drug.query.filter(Drug.id == drug.id).update({Drug.count: int(drug.count)+int(count)})
                    stock = Stock(stockPrice=price, stockCount=count, stockMoney=int(count)*float(price), drugId=drug.id, userId=user_id)
                    db.session.add(stock)
                    db.session.commit()
                else:
                    # 判断类别
                    drugType = DrugType.query.filter(DrugType.name == type).first()
                    # 存在
                    if drugType:
                        drug = Drug(num=num, name=name, count=count, price=price, desc=desc, drugTypeId=drugType.id)
                    else:
                        drugType = DrugType(name=type)
                        db.session.add(drugType)
                        db.session.commit()
                        drugType = DrugType.query.filter(DrugType.name == type).first()
                        drug = Drug(num=num, name=name, count=count, price=price, desc=desc, drugTypeId=drugType.id)

                    db.session.add(drug)
                    db.session.commit()
                    drug = Drug.query.filter(Drug.num == num).first()
                    stock = Stock(stockPrice=price, stockCount=count, stockMoney=int(count)*float(price), drugId=drug.id, userId=user_id)
                    db.session.add(stock)
                    db.session.commit()
                return redirect(url_for('home'))

    return redirect(url_for('login'))


# 添加药品类别
@app.route('/addDrugType/', methods=['POST', 'GET'])
def addDrugType():
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            drugTypeTips = None
            if request.method == 'GET':
                drugTypes = DrugType.query.all()
            else:
                drugTypeName = request.form.get('drugTypeName')
                drugType = DrugType.query.filter(DrugType.name == drugTypeName).first()
                if drugType:
                    drugTypeTips = u'该药品类别已经存在，更改其他类别名称吧!'
                else:
                    drugTypeTips = u'该药品类别已经添加成功!'
                    drugType = DrugType(name=drugTypeName)
                    db.session.add(drugType)
                    db.session.commit()
                drugTypes = DrugType.query.all()

            return render_template('addDrugType.html', drugTypes=drugTypes, drugTypeTips=drugTypeTips)

    return redirect(url_for('login'))


# 药品详情
@app.route('/drugDetail/<drugNum>/', methods=['GET'])
def drugDetail(drugNum):
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            # 查找药品数据库
            drug = Drug.query.filter(Drug.num == drugNum).first()

            return render_template('drugDetail.html', drug=drug)

    return redirect(url_for('login'))


# 删除药品类别
@app.route('/deleteDrugType/<drugTypeId>/', methods=['GET', 'POST'])
def deleteDrugType(drugTypeId):
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            # 查找药品数据库
            drugType = DrugType.query.filter(DrugType.id == drugTypeId).first()
            if drugType:
                # # 删除药品
                # drugs = Drug.query.filter(Drug.drugTypeId == drugType.id).all()
                # for drug in drugs:
                #     db.session.delete(drug)
                #     db.session.flush()
                db.session.delete(drugType)
                db.session.commit()
            return redirect(url_for('addDrugType'))

    return redirect(url_for('login'))


# 查找药品
@app.route('/searchDrug/', methods=['POST'])
def searchDrug():
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            # 判断是否是POST
            if request.method == 'POST':
                keywords = request.form.get('keywords')

                drugs = Drug.query.filter(db.or_(Drug.num.like("%" + keywords + "%"),
                                                       Drug.name.like("%" + keywords + "%"),
                                                       Drug.desc.like("%" + keywords + "%"))) \
                    .group_by(Drug.num).order_by(Drug.id)

                return render_template('searchDrug.html', drugs=drugs)

    return redirect(url_for('login'))


# 进货页面
@app.route('/addStock/<drugNum>/', methods=['GET', 'POST'])
def addStock(drugNum):
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            # 判断是否是POST
            if request.method == 'GET':
                drug = Drug.query.filter(Drug.num == drugNum).first()
                return render_template('addStock.html', drug=drug)
            else:
                id = request.form.get('id')
                num = request.form.get('num')
                name = request.form.get('name')
                type = request.form.get('type')
                count = request.form.get('count')
                # 原来库存量
                stockCount = request.form.get('stockCount')
                price = request.form.get('price')
                desc = request.form.get('desc')

                # 库存量增加
                Drug.query.filter(Drug.id == id).update({Drug.count: int(stockCount) + int(count)})
                stock = Stock(stockPrice=price, stockCount=count, stockMoney=int(count) * float(price),
                              drugId=id, userId=user_id)
                db.session.add(stock)
                db.session.commit()

                return redirect(url_for('addStockHome'))
    return redirect(url_for('login'))

# 进货首页
@app.route('/addStockHome/', methods=['GET'])
def addStockHome():
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            drugs = Drug.query.all()
            return render_template('addStockHome.html', drugs=drugs)

    return redirect(url_for('login'))


# 进货历史
@app.route('/addStocHistory/', methods=['GET'])
def addStocHistory():
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            stocks = Stock.query.all()
            return render_template('addStockHis.html', stocks=stocks)

    return redirect(url_for('login'))


# 退货操作
@app.route('/backStock/<stockId>/', methods=['GET'])
def backStock(stockId):
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            stock = Stock.query.filter(Stock.id == stockId).first()
            Drug.query.filter(Drug.id == stock.drug.id).update({Drug.count: int(stock.drug.count)-int(stock.stockCount)})
            db.session.delete(stock)
            db.session.commit()
            return redirect(url_for('addStocHistory'))

    return redirect(url_for('login'))


# 购买首页
@app.route('/saleDrugHome/', methods=['GET'])
def saleDrugHome():
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            drugs = Drug.query.all()
            return render_template('saleDrugHome.html', drugs=drugs)
    return redirect(url_for('login'))


# 购买
@app.route('/saleDrug/<drugId>/', methods=['GET', 'POST'])
def saleDrug(drugId):
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            # 判断是否是POST
            if request.method == 'GET':
                count = 0
                drug = Drug.query.filter(Drug.id == drugId).first()
                # 查找选购表 药品的选购数量
                s = db.session.query(func.sum(Sale.saleCount).label('count')).\
                    filter(db.and_(Sale.userId == user_id, Sale.drugId == drug.id, Sale.accountId == None)).group_by(Sale.drugId).first()
                if s:
                    count = s.count
                return render_template('saleDrug.html', drug=drug, count=int(drug.count)-count)
            else:
                nowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                id = request.form.get('id')
                price = request.form.get('price')
                saleCount = request.form.get('saleCount')

                sale = Sale(time=nowTime, userId=user.id, saleCount=saleCount, saleMoney=int(saleCount)*float(price), drugId=id)
                db.session.add(sale)
                db.session.commit()

                return redirect(url_for('showSaleDrug'))

    return redirect(url_for('login'))


# 查看选购
@app.route('/showSaleDrug/', methods=['GET'])
def showSaleDrug():
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            saleMoney = 0
            # 还未结账 accountId=None
            sales = Sale.query.filter(db.and_(Sale.userId == user_id, Sale.accountId == None)).all()
            for sale in sales:
                saleMoney = saleMoney + sale.saleMoney
            return render_template('showSaleDrug.html', sales=sales, saleMoney=saleMoney)

    return redirect(url_for('login'))


# 删除选购
@app.route('/deleteSale/<id>', methods=['GET'])
def deleteSale(id):
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            sale = Sale.query.filter(Sale.id == id).first()
            db.session.delete(sale)
            db.session.commit()
            return redirect(url_for('showSaleDrug'))

    return redirect(url_for('login'))


# 清除选购
@app.route('/clearSale/', methods=['GET'])
def clearSale():
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            sales = Sale.query.filter(Sale.userId == user_id, Sale.accountId == None).all()
            for sale in sales:
                db.session.delete(sale)
                db.session.flush()
            db.session.commit()

            return redirect(url_for('saleDrugHome'))

    return redirect(url_for('login'))


# 结账英语
@app.route('/account/', methods=['GET'])
def account():
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            saleMoney = 0
            nowDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # 插入结账表
            account = Account(userId=user_id, time=nowDate)
            db.session.add(account)
            db.session.commit()

            sales = Sale.query.filter(Sale.userId == user_id, Sale.accountId == None).all()
            for sale in sales:
                saleMoney = saleMoney + sale.saleMoney
                Sale.query.filter(Sale.id == sale.id).update({Sale.accountId: account.id})
                Drug.query.filter(Drug.id == sale.drug.id).update({Drug.count: int(sale.drug.count)-int(sale.saleCount),
                    Drug.saleCount: int(sale.drug.saleCount) + int(sale.saleCount)})
                db.session.flush()

            Account.query.filter(Account.id == account.id).update({Account.accountMoney: saleMoney})
            db.session.commit()
            return redirect(url_for('saleManageHome'))

    return redirect(url_for('login'))


# 销售管理首页
@app.route('/saleManageHome/', methods=['GET'])
def saleManageHome():
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            accounts = []
            ats = Account.query.all()
            for a in ats:
                account = {}
                account['accountId'] = a.id
                account['username'] = a.user.username
                account['accountMoney'] = a.accountMoney
                account['time'] = a.time
                # 遍历选购表
                ss = Sale.query.filter(Sale.accountId == a.id).all()
                sales = []
                for sale in ss:
                    s = {}
                    s['name'] = sale.drug.name
                    s['price'] = sale.drug.price
                    s['count'] = sale.saleCount
                    s['money'] = sale.saleMoney
                    sales.append(s)

                account['details'] = sales
                accounts.append(account)
            return render_template('saleManageHome.html', accounts=accounts)
    return redirect(url_for('login'))


# 今日明细
@app.route('/saleOnToday/', methods=['GET'])
def saleOnToday():
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            cur = datetime.datetime.now()
            ats = Account.query.filter(db.and_(extract('year', Account.time) == cur.year, extract('month', Account.time) == cur.month,
                                extract('day', Account.time) == cur.day)).all()
            accounts = []
            for a in ats:
                account = {}
                account['accountId'] = a.id
                account['username'] = a.user.username
                account['accountMoney'] = a.accountMoney
                account['time'] = a.time
                # 遍历选购表
                ss = Sale.query.filter(Sale.accountId == a.id).all()
                sales = []
                for sale in ss:
                    s = {}
                    s['name'] = sale.drug.name
                    s['price'] = sale.drug.price
                    s['count'] = sale.saleCount
                    s['money'] = sale.saleMoney
                    sales.append(s)

                account['details'] = sales
                accounts.append(account)
            return render_template('saleOnToday.html', accounts=accounts)
    return redirect(url_for('login'))


# 日期查询
@app.route('/saleSearchByDay/', methods=['GET', 'POST'])
def saleSearchByDay():
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            if request.method == 'GET':
                # 查询今日的明细
                cur = datetime.datetime.now()
                ats = Account.query.filter(db.and_(extract('year', Account.time) == cur.year, extract('month', Account.time) == cur.month,
                            extract('day', Account.time) == cur.day)).all()
                accounts = []
                for a in ats:
                    account = {}
                    account['accountId'] = a.id
                    account['username'] = a.user.username
                    account['accountMoney'] = a.accountMoney
                    account['time'] = a.time
                    # 遍历选购表
                    ss = Sale.query.filter(Sale.accountId == a.id).all()
                    sales = []
                    for sale in ss:
                        s = {}
                        s['name'] = sale.drug.name
                        s['price'] = sale.drug.price
                        s['count'] = sale.saleCount
                        s['money'] = sale.saleMoney
                        sales.append(s)

                    account['details'] = sales
                    accounts.append(account)
                return render_template('saleSearchByDay.html', accounts=accounts, startTime=cur.strftime("%Y-%m-%d"),
                                       endTime=(cur + datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
            else:
                startTime = request.form.get('startTime')
                endTime = request.form.get('endTime')
                ats = Account.query.filter(Account.time.between(startTime, endTime)).all()
                accounts = []
                for a in ats:
                    account = {}
                    account['accountId'] = a.id
                    account['username'] = a.user.username
                    account['accountMoney'] = a.accountMoney
                    account['time'] = a.time
                    # 遍历选购表
                    ss = Sale.query.filter(Sale.accountId == a.id).all()
                    sales = []
                    for sale in ss:
                        s = {}
                        s['name'] = sale.drug.name
                        s['price'] = sale.drug.price
                        s['count'] = sale.saleCount
                        s['money'] = sale.saleMoney
                        sales.append(s)

                    account['details'] = sales
                    accounts.append(account)
                return render_template('saleSearchByDay.html', accounts=accounts, startTime=startTime, endTime=endTime)
    return redirect(url_for('login'))


# 销售排行
@app.route('/saleOrder/', methods=['GET'])
def saleOrder():
    # 判断用户是否登录
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            drugs = Drug.query.filter(Drug.saleCount != 0).order_by(db.desc(Drug.saleCount)).all()
            return render_template('saleOrder.html', drugs=drugs)

    return redirect(url_for('login'))


# 注销
@app.route('/logout/')
def logout():
    # session.pop('user_id')
    session.clear()
    return redirect(url_for('login'))


# 获取上下文
@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return {'user': user}
    return {}

if __name__ == '__main__':
    app.debug = True
    app.run()
    # app.run(debug=app.debug, host='0.0.0.0', port=5001)
