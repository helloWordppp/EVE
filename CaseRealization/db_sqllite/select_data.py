# -*- coding:utf-8 -*-
from __future__ import unicode_literals
"""
@author:Pengbo
@file:select_data.py
@className:
@time:2019/8/22 9:14
@function:

"""

from collections import OrderedDict
from CaseRealization.db_sqllite.DBcrud import CSqllite


class CSelect_data(object):
    """
    数据查询类，负责数据的查询
    """
    def __init__(self):
        """"""
        # self.my_sqlite = CSqllite()
        pass

    def Select_data(self, process_name):
        """
        数据查询接口
        :param process_name:
        :return:
        """
        cpu = []
        memory = []
        io_read = []
        io_write = []
        handles = []
        gdi = []
        install_time = []
        threads = []
        return_data = OrderedDict([("cpu", cpu), ("memory", memory), ("io_read", io_read), ("io_write", io_write),
                                   ("handles", handles), ("gdi", gdi),
                                   ("install_time", install_time), ("threads", threads)])
        # process_name = process_name.lower()
        if process_name.endswith(".exe"):
            table_name = process_name.replace(".exe", "").strip()
        elif process_name.endswith(".tmp"):
            table_name = process_name.replace(".tmp", "").strip()
        elif process_name.endswith(".msi"):
            table_name = process_name.replace(".msi", "").strip()
        else:
            table_name = process_name
        sql = "select * from '{0}' order by install_time".format(table_name)

        my_sqlite = CSqllite()
        result = my_sqlite.Excution_sql(sql)
        if isinstance(result, str):
            print("sql 执行错误")
            return return_data
        # print(len(result))
        for item in result:
            # if item["cpu_use"] == -1:
            #     continue
            return_data["cpu"].append(item["cpu_use"])
            return_data["memory"].append(item["memory"])
            return_data["io_read"].append(item["io_read"])
            return_data["io_write"].append(item["io_write"])
            return_data["handles"].append(item["handles"])
            return_data["gdi"].append(item["gdi"])
            return_data["threads"].append(item["threads"])
            return_data["install_time"].append(item["install_time"])
        print(return_data["cpu"].__len__())
        my_sqlite.Close_db()
        return return_data

    def Select_data_avg(self, process_name, db_path=None):
        """
        查询最大值最小值等信息
        :param process_name: 数据库名称也就是 进程名称  不带.exe
        :param db_path: 数据库的路径
        :return:
        """

        return_data = OrderedDict([("max_cpu_use", -1), ("min_cpu_use", -1), ("avg_cpu_use", -1),
                                   ("max_gpu", -1), ("min_gpu", -1), ("avg_gpu", -1),
                                   ("max_memory", -1), ("min_memory", -1), ("avg_memory", -1)])

        table_name = process_name
        sql = """SELECT MAX(cpu_use) as max_cpu_use, MIN(cpu_use) as min_cpu_use, AVG(cpu_use) as avg_cpu_use, 
        MAX(gpu) as max_gpu, MIN(gpu) as min_gpu, AVG(gpu) as avg_gpu,MAX(memory) as max_memory, 
        MIN(memory) as min_memory, AVG(memory) as avg_memory FROM {0}
        """.format(table_name)
        # print(sql)
        my_sqlite = CSqllite(db_file_path=db_path)
        result = my_sqlite.Excution_sql(sql)

        if isinstance(result, str):
            print("sql 执行错误")
            return return_data
        # print(len(result))
        for one_line in result:
            print(one_line)
            for item in return_data.keys():
                return_data[item] = one_line[item]
            break

        # print(return_data["cpu"].__len__())
        my_sqlite.Close_db()
        return return_data

    def Get_table_exist(self, table_name):
        """
        判断某一数据库表是否存在
        :return:
        """
        sql_cmd = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        my_sqlite = CSqllite()
        all_table = my_sqlite.Excution_sql(sql_cmd)
        if isinstance(all_table, str):
            print("查表失败")
            my_sqlite.Close_db()
            # self.my_sqlite.Close_db()
            return True
        table_exist = False

        for one in all_table:
            if table_name == one["name"]:
                table_exist = True
                break
        my_sqlite.Close_db()
        return table_exist


# if __name__ == '__main__':
#     test = CSelect_data()
#     print(test.Get_table_exist("TbService"))
#     test.Select_data("TbService")
