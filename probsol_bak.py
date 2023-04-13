###
 # @Author: Haofei Hou
 # @Date: 07-08-2022 16:04:07
 # @LastEditTime: 08-11-2022 19:50:42
 # @Contact: yuechuhaoxi020609@outlook.com
###
from pickle import GLOBAL
from site import USER_BASE
from flask import (
    Flask,
    request,
    jsonify,
    send_file,
    send_from_directory,
    redirect,
    url_for,
    flash,
    render_template,
)
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, Email
import struct
import sqlite3
import base64
from functools import lru_cache
import os
import logging
import random
from logging import Formatter, FileHandler
import json
from flask_sockets import Sockets
import datetime
from flask_cors import *

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True

CORS(app, supports_credentials=True)

sockets = Sockets(app)


'''BackEnd Flask 

@Databases:
        
sqlite> create table user(
   ...> account char(64) primary key,
   ...> name char(64),
   ...> password char(512),
   ...> image char(256)
   ...> );
    
    
sqlite> create table bill(
   ...> idofbill INTEGER primary key AUTOINCREMENT,
   ...> typeofbill int,
   ...> use char(512),
   ...> date char(64),
   ...> number int,
   ...> account char(64),
   ...> foreign key(account) references user(account)
   ...> );

@Routes:
    register(): method = POST, input user info json. +
                return 0 for success, 1 for repeating name, 2 for error.

    login(): method = POST, input account and password. input user info json. 
            return 0 for success, 1 for not have registered, 2 for password wrong, 3 for error.
            
    store_bill(): method = POST, input bill(without idofbill).
                    return 0 for success, 1 for error.
            
    get_bills() method = POST, input account(string).
                    return 0 for success, 1 for error.

    modify_bill() method = POST, input idofbill, bill(without idofbill).
                    return 0 for success, 1 for error. 
'''

@app.route('/register/', methods = ['POST'])
def register():
    info = request.get_data()
    info = json.loads(info)
    print(info)
    user = info['user']

    try:
        con = sqlite3.connect('/app/test/database.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM user WHERE account = '{}'".format(user['account']))
        users = cur.fetchall()
        if len(users) == 0:
            cur.execute("INSERT INTO user(account, name, password, image) VALUES('{}', '{}', '{}', '{}')".
                        format(user['account'], user['name'], user['password'], user['image']))
            con.commit()
            app.logger.info(user['account'] + ' register successfully')
            return jsonify({'code': 0, 'info':'start successfully', 'data': user['account']})
        else:
            return jsonify({'code': 1, 'info':'repeated account'})
    except sqlite3.Error:
        return jsonify({'code': 2, 'info':'ERROR!'})

@app.route('/login/', methods = ['POST'])
def login():

    account = request.args.get("account")
    password = request.args.get("password")

    try:
        con = sqlite3.connect('/app/test/database.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM user WHERE account = '{}'".format(account))
        users = cur.fetchall()
        if len(users) == 0:
            return jsonify({'code': 1, 'info':'not have registered'})
        elif len(users) == 1:
            if password == users[0][2]:
                app.logger.info(account + ' start successfully')
                return jsonify({'code': 0, 'info':'start successfully', 'data': account})
            else:
                return jsonify({'code': 2, 'info':'email or name not match'})
        else:
            return jsonify({'code': 3, 'info':'ERROR!'})
    except sqlite3.Error:
        return jsonify({'code': 3, 'info':'ERROR!'})



@app.route('/store_bill/', methods = ['POST'])
def store_bill():

    bill = request.args.get('bill')
    bill = json.loads(bill)

    try:
        con = sqlite3.connect('/app/test/database.db')
        cur = con.cursor()
        cur.execute("INSERT INTO bill(typeofbill, use, date, number, account) VALUES({}, '{}', '{}', {}, '{}')".
                        format(bill['typeofbill'], bill['use'], bill['date'], bill['number'], bill['account']))
        con.commit()
        return jsonify({'code': 0, 'info':'success!'})
    except sqlite3.Error:
        return jsonify({'code': 1, 'info':'ERROR!'})

@app.route('/get_bills/', methods = ['POST'])
def get_bills():

    account = request.args.get('account')

    try:
        con = sqlite3.connect('/app/test/database.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM bill WHERE account = '{}'".format(account))
        bills = cur.fetchall()
        json_bills = []
        for bill in bills:
            jbill = {
                'idofbill': bill[0],
                'typeofbill': bill[1],
                'use': bill[2],
                'date': bill[3],
                'number': bill[4],
                'account': bill[5]
            }
            json_bills.append(jbill)
        return jsonify({'code': 0, 'info':'success!', 'data': json_bills})
    except sqlite3.Error:
        return jsonify({'code': 1, 'info':'ERROR!'})

@app.route('/modify_bill/', methods = ['POST'])
def modify_bill():

    billofid = request.args.get('billofid')
    bill = request.args.get('bill')
    bill = json.loads(bill)

    try:
        con = sqlite3.connect('/app/test/database.db')
        cur = con.cursor()
        cur.execute("update bill set typeofbill={}, use='{}', date='{}', number={}, account='{}' WHERE idofbill = {}".
                    format(bill['typeofbill'], bill['use'], bill['date'], bill['number'], bill['account'], idofbill))
        con.commit()
        return jsonify({'code': 0, 'info':'success!'})
    except sqlite3.Error:
        return jsonify({'code': 1, 'info':'ERROR!'})



if __name__ == "__main__":
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY

    # log settings
    handler = FileHandler('/app/test/app.log')
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    # start server
    server = pywsgi.WSGIServer(('0.0.0.0', 8080), app, handler_class=WebSocketHandler)
    print('server start')
    server.serve_forever()


