#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 libei. All right reserved.
"""=================================================
@IDE    ：PyCharm
@Author ：Li Bei
@Email  : libei@cadg.cn
@Date   ：2021/4/22 16:20
================================================="""
import pymysql


# 建立连接
conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='root',
    db='db2',
    charset='utf8'
)

# 获取游标
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 执行sql语句
# # 增、删、改
# sql = 'insert into employee(name, sex, hire_date, age, salary) values(%s, %s, %s, %s, %s)'
# # rows = cursor.execute(sql, ('melissa', 'male', 20210713, 25, 1000))
# rows = cursor.executemany(sql, [('jason1', 'female', 20210713, 25, 1000), ('liam1', 'female', 20210713, 25, 1000)])
# # 提交修改
# conn.commit()
# print(cursor.lastrowid)

# 查询
# rows = cursor.execute('select * from employee')
# 获取内容
# print(cursor.fetchone())
# print(cursor.fetchone())
# print(cursor.fetchone())
# print(cursor.fetchall())
# print(cursor.fetchmany(2))

# 移动游标
# cursor.scroll(3, mode='absolute')  # 相对绝对位置移动
# print(cursor.fetchone())
# print(cursor.fetchone())
# cursor.scroll(2, mode='relative')  # 相对相对位置移动
# print(cursor.fetchone())

# 执行sql语句
# sqls = [['create table course (cid int PRIMARY KEY , cname char(6), teacher_id int)', None],
#         ['create table teacher (tid int PRIMARY KEY , tname char(6))', None],
#         ['insert into course (cid, cname, teacher_id) values(%s, %s, %s)', [(1, '生物', 1),
#                                                                             (2, '物理', 2),
#                                                                             (3, '体育', 3),
#                                                                             (4, '美术', 2)]],
#         ['insert into teacher (tid, tname) values(%s, %s)', [(1, '张磊'),
#                                                              (2, '李平'),
#                                                              (3, '刘海燕'),
#                                                              (4, '朱云海'),
#                                                              (5, '李杰')]]
#         ]
sqls = [['select * from course inner join teacher on teacher.tid=course.teacher_id', None]]
for sql, value in sqls:
    if not value:
        rows = cursor.execute(sql)
    elif len(value) == 1:
        rows = cursor.execute(sql, value)
    else:
        rows = cursor.executemany(sql, value)
    if sql.startswith('select'):
        print(cursor.fetchall())
# 提交修改
conn.commit()

# 关闭游标
cursor.close()
# 关闭连接
conn.cursor()

# 进行判断
if rows:
    print("Successful")
else:
    print("Unsuccessful")
