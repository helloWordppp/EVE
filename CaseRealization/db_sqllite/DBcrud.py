# -*- coding:utf-8 -*-

"""
@author:Pengbo
@file:DBcrud.py
@className:
@time:2019/8/2 11:05
@function:
数据库读写类
"""

import sqlite3
import os
import sys
import traceback
import threading
from collections import OrderedDict
from CaseRealization.db_sqllite.logging_print import MyLogPrint


def dict_factory(cursor, row):
    """
    序列化sqllite查询结果
    :param cursor:
    :param row:
    :return:
    """
    dic = OrderedDict()
    for idx, col in enumerate(cursor.description):
        dic[col[0]] = row[idx]
    return dic


class CSqllite:
    """

    """
    def __init__(self, db_file_path=None):
        """

        """
        self.dir_path, _ = os.path.split(sys.argv[0])
        if db_file_path is None:
            db_path = os.path.join(self.dir_path, "DB_data")
            if not os.path.exists(db_path):
                os.makedirs(db_path)
            self.db_file_path = os.path.join(db_path, "performance_data.db")
        else:
            self.db_file_path = db_file_path
        log_path = os.path.join(self.dir_path, "Log")
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        log_file_path = os.path.join(log_path, "db.log")
        self.my_log = MyLogPrint(log_file_path)

        # 打开数据
        try:
            self.conn = sqlite3.connect(self.db_file_path, check_same_thread=False)
            self.conn.row_factory = dict_factory
            # self.cursor = self.conn.cursor()
        except:
            error = traceback.format_exc()
            self.my_log.print_info(error)
            raise Exception("打开数据库失败")

        self.lock = threading.RLock()
        self.insert_count = 0

    def Excution_sql(self, sql):
        """

        :param sql:
        :return:
        """
        try:
            with self.lock:
                result = self.conn.cursor().execute(sql)
                # result = self.cursor.execute(sql)
                if sql.lower().startswith("insert") or sql.lower().startswith("update"):
                    temp = self.insert_count
                    temp = temp + 1
                    self.insert_count = temp
                    if self.insert_count == 1:
                        self.conn.commit()
                        self.insert_count = 0
                # else:
                #     self.conn.commit()  # select 不需要提交数据库
        except:
            self.my_log.print_info("执行sql异常：", sql)
            error = traceback.format_exc()
            self.my_log.print_info(error)
            return "error"
        # finally:
        #     self.lock.release()

        return result

    def Close_db(self):
        """
        关闭数据库连接
        :return:
        """
        self.conn.close()

