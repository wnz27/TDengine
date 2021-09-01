###################################################################
#           Copyright (c) 2016 by TAOS Technologies, Inc.
#                     All rights reserved.
#
#  This file is proprietary and confidential to TAOS Technologies.
#  No part of this file may be reproduced, stored, transmitted,
#  disclosed or used in any form or by any means other than as
#  expressly provided by the written permission from Jianhui Tao
#
###################################################################

# -*- coding: utf-8 -*-

import sys
import taos
from util.log import tdLog
from util.cases import tdCases
from util.sql import tdSql
from util.dnodes import *
import random
import time


class TDTestCase:
    def init(self, conn, logSql):
        tdLog.debug("start to execute %s" % __file__)
        tdSql.init(conn.cursor(), logSql)

        self.ts = 1600000000000
        self.num = 50
        self.num4096 = 5

    def getBuildPath(self):
        selfPath = os.path.dirname(os.path.realpath(__file__))

        if ("community" in selfPath):
            projPath = selfPath[:selfPath.find("community")]
        else:
            projPath = selfPath[:selfPath.find("tests")]

        for root, dirs, files in os.walk(projPath):
            if ("taosd" in files):
                rootRealPath = os.path.dirname(os.path.realpath(root))
                if ("packaging" not in rootRealPath):
                    buildPath = root[:len(root) - len("/build/bin")]
                    break
        return buildPath

    def run(self):
        tdSql.prepare()
        # test case for https://jira.taosdata.com:18080/browse/TD-5062

        startTime = time.time()

        tdSql.execute('''drop database if exists test_updata_2 ;''')
        # update 0 不更新 ; update 1 覆盖更新 ;update 2 合并更新
        tdLog.info("========== test database updata = 2 ==========")
        tdSql.execute(
            '''create database test_updata_2 update 2 minrows 10 maxrows 200 ;'''
        )
        tdSql.execute('''use test_updata_2;''')
        tdSql.execute('''create stable stable_1
                    (ts timestamp , q_int int , q_bigint bigint , q_smallint smallint , q_tinyint tinyint, 
                    q_bool bool , q_binary binary(10) , q_nchar nchar(10) , q_float float , q_double double , q_ts timestamp) 
                    tags(loc nchar(20) , t_int int);''')
        tdSql.execute(
            '''create table table_1 using stable_1 tags('table_1' , '1' )''')
        tdSql.execute(
            '''create table table_2 using stable_1 tags('table_2' , '2' )''')
        tdSql.execute(
            '''create table table_3 using stable_1 tags('table_3' , '3' )''')

        #regular table
        tdSql.execute('''create table regular_table_1
                    (ts timestamp , q_int int , q_bigint bigint , q_smallint smallint , q_tinyint tinyint, 
                    q_bool bool , q_binary binary(10) , q_nchar nchar(10) , q_float float , q_double double , q_ts timestamp) ;'''
                      )
        tdSql.execute('''create table regular_table_2
                    (ts timestamp , q_int int , q_bigint bigint , q_smallint smallint , q_tinyint tinyint, 
                    q_bool bool , q_binary binary(10) , q_nchar nchar(10) , q_float float , q_double double , q_ts timestamp) ;'''
                      )
        tdSql.execute('''create table regular_table_3
                    (ts timestamp , q_int int , q_bigint bigint , q_smallint smallint , q_tinyint tinyint, 
                    q_bool bool , q_binary binary(10) , q_nchar nchar(10) , q_float float , q_double double , q_ts timestamp) ;'''
                      )

        tdLog.info("========== test1.1 : insert data , check data==========")
        tdLog.info("========== regular_table ==========")
        tdSql.execute(
            '''insert into regular_table_1 values( %d , 0, 0, 0, 0, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 200))
        sql = '''select * from regular_table_1 where ts = %d ;''' % (self.ts -
                                                                     200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.execute(
            '''insert into regular_table_1 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts + 200))
        sql = '''select * from regular_table_1 where ts = %d ;''' % (self.ts +
                                                                     200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdSql.execute(
            '''insert into regular_table_1 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts - 500))
        sql = '''select * from regular_table_1 where ts = %d ;''' % (self.ts -
                                                                     500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdSql.execute(
            '''insert into regular_table_1 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts + 500))
        sql = '''select * from regular_table_1 where ts = %d ;''' % (self.ts +
                                                                     500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdLog.info("========== stable ==========")
        tdSql.execute(
            '''insert into table_1 values( %d , 0, 0, 0, 0, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 200))
        sql = '''select * from table_1 where ts = %d ;''' % (self.ts - 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where ts = %d ;''' % (self.ts - 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.execute(
            '''insert into table_1 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts + 200))
        sql = '''select * from table_1 where ts = %d ;''' % (self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)
        sql = '''select * from stable_1 where ts = %d ;''' % (self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdSql.execute(
            '''insert into table_1 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts - 500))
        sql = '''select * from table_1 where ts = %d ;''' % (self.ts - 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)
        sql = '''select * from stable_1 where ts = %d ;''' % (self.ts - 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdSql.execute(
            '''insert into table_1 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts + 500))
        sql = '''select * from table_1 where ts = %d ;''' % (self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)
        sql = '''select * from stable_1 where ts = %d ;''' % (self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdLog.info("========== 4096 regular_table ==========")
        sql = "create table regular_table_4096_1 (ts timestamp, "
        for i in range(500):
            sql += "int_%d int, " % (i + 1)
        for i in range(500, 1000):
            sql += "smallint_%d smallint, " % (i + 1)
        for i in range(1000, 1500):
            sql += "tinyint_%d tinyint, " % (i + 1)
        for i in range(1500, 2000):
            sql += "double_%d double, " % (i + 1)
        for i in range(2000, 2500):
            sql += "float_%d float, " % (i + 1)
        for i in range(2500, 3000):
            sql += "bool_%d bool, " % (i + 1)
        for i in range(3000, 3500):
            sql += "bigint_%d bigint, " % (i + 1)
        for i in range(3500, 3800):
            sql += "nchar_%d nchar(4), " % (i + 1)
        for i in range(3800, 4090):
            sql += "binary_%d binary(10), " % (i + 1)
        for i in range(4090, 4094):
            sql += "timestamp_%d timestamp, " % (i + 1)
        sql += "col4095 binary(22))"
        tdLog.info(len(sql))
        tdSql.execute(sql)

        for i in range(self.num4096):
            sql = "insert into regular_table_4096_1 values(%d, "
            for j in range(4090):
                str = "'%s', " % 'NULL'
                sql += str
            for j in range(4090, 4094):
                str = "%s, " % (self.ts + j)
                sql += str
            sql += "'%s')" % (self.ts + i)
            tdSql.execute(sql % (self.ts + i))
        tdSql.query('''select * from regular_table_4096_1 where ts = %d ;''' %
                    (self.ts))
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 501, None)
        tdSql.checkData(0, 1001, None)
        tdSql.checkData(0, 1501, None)
        tdSql.checkData(0, 2001, None)
        tdSql.checkData(0, 2501, None)
        tdSql.checkData(0, 3001, None)
        tdSql.checkData(0, 3501, 'NULL')
        tdSql.checkData(0, 3801, 'NULL')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4095, '1600000000000')

        sql = '''insert into regular_table_4096_1 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4095 )
                values('2020-09-10 20:26:40.000' , 1 , 501 , 101 , 1501 , 2001 , 1 , 3001 , '3501' , '3801' ,'2020-09-10 20:26:44.090','1500000000000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from regular_table_4096_1 where ts ='2020-09-10 20:26:40.000';"
        )
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4095, '1500000000000')

        tdLog.info("========== 4096 stable ==========")
        sql = "create stable stable_4096_1 (ts timestamp, "
        for i in range(500):
            sql += "int_%d int, " % (i + 1)
        for i in range(500, 1000):
            sql += "smallint_%d smallint, " % (i + 1)
        for i in range(1000, 1500):
            sql += "tinyint_%d tinyint, " % (i + 1)
        for i in range(1500, 2000):
            sql += "double_%d double, " % (i + 1)
        for i in range(2000, 2500):
            sql += "float_%d float, " % (i + 1)
        for i in range(2500, 3000):
            sql += "bool_%d bool, " % (i + 1)
        for i in range(3000, 3500):
            sql += "bigint_%d bigint, " % (i + 1)
        for i in range(3500, 3800):
            sql += "nchar_%d nchar(4), " % (i + 1)
        for i in range(3800, 4090):
            sql += "binary_%d binary(10), " % (i + 1)
        for i in range(4090, 4092):
            sql += "timestamp_%d timestamp, " % (i + 1)
        sql += " col4093 binary(22)) "
        sql += " tags (loc nchar(20),tag_1 int) "
        tdLog.info(len(sql))
        tdSql.execute(sql)

        sql = " create table table_4096_1 using stable_4096_1 tags ('table_4096_1',1); "
        tdSql.execute(sql)

        for i in range(self.num4096):
            sql = "insert into table_4096_1 values(%d, "
            for j in range(4090):
                str = "'%s', " % 'NULL'
                sql += str
            for j in range(4090, 4092):
                str = "%s, " % (self.ts + j)
                sql += str
            sql += "'%s')" % (self.ts + i)
            tdSql.execute(sql % (self.ts + i))
        tdSql.query('''select * from table_4096_1 where ts = %d ;''' %
                    (self.ts))
        tdSql.checkCols(4094)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 501, None)
        tdSql.checkData(0, 1001, None)
        tdSql.checkData(0, 1501, None)
        tdSql.checkData(0, 2001, None)
        tdSql.checkData(0, 2501, None)
        tdSql.checkData(0, 3001, None)
        tdSql.checkData(0, 3501, 'NULL')
        tdSql.checkData(0, 3801, 'NULL')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4093, '1600000000000')
        tdSql.query('''select * from stable_4096_1 where ts = %d ;''' %
                    (self.ts))
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 501, None)
        tdSql.checkData(0, 1001, None)
        tdSql.checkData(0, 1501, None)
        tdSql.checkData(0, 2001, None)
        tdSql.checkData(0, 2501, None)
        tdSql.checkData(0, 3001, None)
        tdSql.checkData(0, 3501, 'NULL')
        tdSql.checkData(0, 3801, 'NULL')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4093, '1600000000000')

        sql = '''insert into table_4096_1 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4093 )
                values('2020-09-10 20:26:40.000' , 1 , 501 , 101 , 1501 , 2001 , 1 , 3001 , '3501' , '3801' ,'2020-09-10 20:26:44.090','1500000000000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from table_4096_1 where ts ='2020-09-10 20:26:40.000';")
        tdSql.checkCols(4094)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4093, '1500000000000')
        tdSql.query(
            "select * from stable_4096_1 where ts ='2020-09-10 20:26:40.000';")
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4093, '1500000000000')

        # minrows 10 maxrows 200
        for i in range(self.num):
            tdSql.execute(
                '''insert into regular_table_1 values(%d, %d, %d, %d, %d, 0, 'binary.%s', 'nchar.%s', %f, %f, %d)'''
                %
                (self.ts - 100 + i, i, i, i, i, i, i, i, i, self.ts - 100 + i))
            tdSql.execute(
                '''insert into regular_table_1 values(%d, %d, %d, %d, %d, false, 'binary%s', 'nchar%s', %f, %f, %d)'''
                % (self.ts + i, random.randint(-2147483647, 2147483647),
                   random.randint(-9223372036854775807, 9223372036854775807),
                   random.randint(-32767, 32767), random.randint(-127, 127),
                   random.randint(-99, 99), random.randint(
                       -9999, 9999), random.uniform(-100000, 100000),
                   random.uniform(-1000000000, 1000000000), self.ts + i))

            tdSql.execute(
                '''insert into table_1 values(%d, %d, %d, %d, %d, 0, 'binary.%s', 'nchar.%s', %f, %f, %d)'''
                %
                (self.ts - 100 + i, i, i, i, i, i, i, i, i, self.ts - 100 + i))
            tdSql.execute(
                '''insert into table_1 values(%d, %d, %d, %d, %d, false, 'binary%s', 'nchar%s', %f, %f, %d)'''
                % (self.ts + i, random.randint(-2147483647, 2147483647),
                   random.randint(-9223372036854775807, 9223372036854775807),
                   random.randint(-32767, 32767), random.randint(-127, 127),
                   random.randint(-99, 99), random.randint(
                       -9999, 9999), random.uniform(-100000, 100000),
                   random.uniform(-1000000000, 1000000000), self.ts + i))

        tdLog.info("========== regular_table ==========")
        tdSql.execute(
            '''insert into regular_table_1 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts - 200))
        sql = '''select * from regular_table_1 where ts = %d ;''' % (self.ts -
                                                                     200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.execute(
            '''insert into regular_table_1 values( %d , 0, 0, 0, 0, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 200))
        sql = '''select * from regular_table_1 where ts = %d ;''' % (self.ts +
                                                                     200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+0')
        tdSql.checkData(0, 7, 'nchar+0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        tdSql.execute(
            '''insert into regular_table_1 values( %d , 1, 1, 1, 1, 1, 'binary+1', 'nchar+1', 1.000000, 1.000000, 1600000001000);'''
            % (self.ts + 200))
        sql = '''select * from regular_table_1 where ts = %d ;''' % (self.ts +
                                                                     200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 2, 1)
        tdSql.checkData(0, 3, 1)
        tdSql.checkData(0, 4, 1)
        tdSql.checkData(0, 5, 'True')
        tdSql.checkData(0, 6, 'binary+1')
        tdSql.checkData(0, 7, 'nchar+1')
        tdSql.checkData(0, 8, 1)
        tdSql.checkData(0, 9, 1)
        tdSql.checkData(0, 10, '2020-09-13 20:26:41.000')

        tdSql.error(
            '''insert into regular_table_1 values( %d , -2147483648, -9223372036854775807, -32767, -127, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into regular_table_1 values( %d , -2147483647, -9223372036854775808, -32767, -127, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into regular_table_1 values( %d , -2147483647, -9223372036854775807, -32768, -127, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into regular_table_1 values( %d , -2147483647, -9223372036854775807, -32767, -128, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into regular_table_1 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-0123', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into regular_table_1 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-0', 'nchar-01234', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))

        tdSql.execute(
            '''insert into regular_table_1 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-012', 'nchar-0123', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        sql = '''select * from regular_table_1 where ts = %d ;''' % (self.ts -
                                                                     500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, -2147483647)
        tdSql.checkData(0, 2, -9223372036854775807)
        tdSql.checkData(0, 3, -32767)
        tdSql.checkData(0, 4, -127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-012')
        tdSql.checkData(0, 7, 'nchar-0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.error(
            '''insert into regular_table_1 values( %d , 2147483648, 9223372036854775807, 32767, 127, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into regular_table_1 values( %d , 2147483647, 9223372036854775808, 32767, 127, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into regular_table_1 values( %d , 2147483647, 9223372036854775807, 32768, 127, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into regular_table_1 values( %d , 2147483647, 9223372036854775807, 32767, 128, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into regular_table_1 values( %d , 2147483647, 9223372036854775807, 32767, 127, 0, 'binary+0123', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into regular_table_1 values( %d , 2147483647, 9223372036854775807, 32767, 127, 0, 'binary+0', 'nchar+01234', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))

        tdSql.execute(
            '''insert into regular_table_1 values( %d , 2147483647, 9223372036854775807, 32767, 127, 0, 'binary+012', 'nchar+0123', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        sql = '''select * from regular_table_1 where ts = %d ;''' % (self.ts +
                                                                     500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 2147483647)
        tdSql.checkData(0, 2, 9223372036854775807)
        tdSql.checkData(0, 3, 32767)
        tdSql.checkData(0, 4, 127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+012')
        tdSql.checkData(0, 7, 'nchar+0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        tdSql.execute(
            '''insert into regular_table_1 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-012', 'nchar-0123', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        sql = '''select * from regular_table_1 where ts = %d ;''' % (self.ts +
                                                                     500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, -2147483647)
        tdSql.checkData(0, 2, -9223372036854775807)
        tdSql.checkData(0, 3, -32767)
        tdSql.checkData(0, 4, -127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-012')
        tdSql.checkData(0, 7, 'nchar-0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdLog.info("========== stable ==========")
        tdSql.execute(
            '''insert into table_1 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts - 200))
        sql = '''select * from table_1 where ts = %d ;''' % (self.ts - 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where ts = %d ;''' % (self.ts - 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.execute(
            '''insert into table_1 values( %d , 0, 0, 0, 0, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 200))
        sql = '''select * from table_1 where ts = %d ;''' % (self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+0')
        tdSql.checkData(0, 7, 'nchar+0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where ts = %d ;''' % (self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+0')
        tdSql.checkData(0, 7, 'nchar+0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.execute(
            '''insert into table_1 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts + 200))
        sql = '''select * from table_1 where ts = %d ;''' % (self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+0')
        tdSql.checkData(0, 7, 'nchar+0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where ts = %d ;''' % (self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+0')
        tdSql.checkData(0, 7, 'nchar+0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.error(
            '''insert into table_1 values( %d , -2147483648, -9223372036854775807, -32767, -127, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into table_1 values( %d , -2147483647, -9223372036854775808, -32767, -127, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into table_1 values( %d , -2147483647, -9223372036854775807, -32768, -127, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into table_1 values( %d , -2147483647, -9223372036854775807, -32767, -128, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into table_1 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-0123', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into table_1 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-0', 'nchar-01234', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))

        tdSql.execute(
            '''insert into table_1 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-012', 'nchar-0123', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        sql = '''select * from table_1 where ts = %d ;''' % (self.ts - 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, -2147483647)
        tdSql.checkData(0, 2, -9223372036854775807)
        tdSql.checkData(0, 3, -32767)
        tdSql.checkData(0, 4, -127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-012')
        tdSql.checkData(0, 7, 'nchar-0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where ts = %d ;''' % (self.ts - 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, -2147483647)
        tdSql.checkData(0, 2, -9223372036854775807)
        tdSql.checkData(0, 3, -32767)
        tdSql.checkData(0, 4, -127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-012')
        tdSql.checkData(0, 7, 'nchar-0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.error(
            '''insert into table_1 values( %d , 2147483648, 9223372036854775807, 32767, 127, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into table_1 values( %d , 2147483647, 9223372036854775808, 32767, 127, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into table_1 values( %d , 2147483647, 9223372036854775807, 32768, 127, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into table_1 values( %d , 2147483647, 9223372036854775807, 32767, 128, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into table_1 values( %d , 2147483647, 9223372036854775807, 32767, 127, 0, 'binary+0123', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into table_1 values( %d , 2147483647, 9223372036854775807, 32767, 127, 0, 'binary+0', 'nchar+01234', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))

        tdSql.execute(
            '''insert into table_1 values( %d , 2147483647, 9223372036854775807, 32767, 127, 0, 'binary+012', 'nchar+0123', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        sql = '''select * from table_1 where ts = %d ;''' % (self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 2147483647)
        tdSql.checkData(0, 2, 9223372036854775807)
        tdSql.checkData(0, 3, 32767)
        tdSql.checkData(0, 4, 127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+012')
        tdSql.checkData(0, 7, 'nchar+0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where ts = %d ;''' % (self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 2147483647)
        tdSql.checkData(0, 2, 9223372036854775807)
        tdSql.checkData(0, 3, 32767)
        tdSql.checkData(0, 4, 127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+012')
        tdSql.checkData(0, 7, 'nchar+0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        tdSql.execute(
            '''insert into table_1 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-012', 'nchar-0123', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        sql = '''select * from table_1 where ts = %d ;''' % (self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, -2147483647)
        tdSql.checkData(0, 2, -9223372036854775807)
        tdSql.checkData(0, 3, -32767)
        tdSql.checkData(0, 4, -127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-012')
        tdSql.checkData(0, 7, 'nchar-0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where ts = %d ;''' % (self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, -2147483647)
        tdSql.checkData(0, 2, -9223372036854775807)
        tdSql.checkData(0, 3, -32767)
        tdSql.checkData(0, 4, -127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-012')
        tdSql.checkData(0, 7, 'nchar-0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdLog.info("========== 4096 regular_table ==========")
        sql = '''insert into regular_table_4096_1 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4095 )
                values('2020-09-13 20:26:40.000' , 1 , 501 , 101 , 1501 , 2001 , 1 , 3001 , '3501' , '3801' ,'2020-09-13 20:26:44.090','1600000000000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from regular_table_4096_1 where ts ='2020-09-13 20:26:40.000';"
        )
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4095, '1600000000000')

        sql = '''insert into regular_table_4096_1 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4095 )
                values('2020-09-10 20:26:40.000' , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL);'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from regular_table_4096_1 where ts ='2020-09-10 20:26:40.000';"
        )
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4095, '1500000000000')

        sql = '''insert into regular_table_4096_1 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4095 )
                values('2020-09-13 20:26:40.000' , 2 , 502 , 102 , 1502 , 2002 , 0 , 3002 , '3502' , '3802' ,'2020-09-13 20:26:44.092','1600000002000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from regular_table_4096_1 where ts ='2020-09-13 20:26:40.000';"
        )
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 2)
        tdSql.checkData(0, 501, 502)
        tdSql.checkData(0, 1001, 102)
        tdSql.checkData(0, 1501, 1502)
        tdSql.checkData(0, 2001, 2002)
        tdSql.checkData(0, 2501, 'False')
        tdSql.checkData(0, 3001, 3002)
        tdSql.checkData(0, 3501, '3502')
        tdSql.checkData(0, 3801, '3802')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.092')
        tdSql.checkData(0, 4095, '1600000002000')

        tdLog.info("========== 4096 stable ==========")
        sql = '''insert into table_4096_1 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4093 )
                values('2020-09-13 20:26:40.000' , 1 , 501 , 101 , 1501 , 2001 , 1 , 3001 , '3501' , '3801' ,'2020-09-13 20:26:44.090','1600000000000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from table_4096_1 where ts ='2020-09-13 20:26:40.000';")
        tdSql.checkCols(4094)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4093, '1600000000000')
        tdSql.query(
            "select * from stable_4096_1 where ts ='2020-09-13 20:26:40.000';")
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4093, '1600000000000')

        sql = '''insert into table_4096_1 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4093 )
                values('2020-09-10 20:26:40.000' , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL);'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from table_4096_1 where ts ='2020-09-10 20:26:40.000';")
        tdSql.checkCols(4094)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4093, '1500000000000')
        tdSql.query(
            "select * from stable_4096_1 where ts ='2020-09-10 20:26:40.000';")
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4093, '1500000000000')

        sql = '''insert into table_4096_1 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4093 )
                values('2020-09-13 20:26:40.000' , 2 , 502 , 102 , 1502 , 2002 , 0 , 3002 , '3502' , '3802' ,'2020-09-13 20:26:44.092','1600000002000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from table_4096_1 where ts ='2020-09-13 20:26:40.000';")
        tdSql.checkCols(4094)
        tdSql.checkData(0, 1, 2)
        tdSql.checkData(0, 501, 502)
        tdSql.checkData(0, 1001, 102)
        tdSql.checkData(0, 1501, 1502)
        tdSql.checkData(0, 2001, 2002)
        tdSql.checkData(0, 2501, 'False')
        tdSql.checkData(0, 3001, 3002)
        tdSql.checkData(0, 3501, '3502')
        tdSql.checkData(0, 3801, '3802')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.092')
        tdSql.checkData(0, 4093, '1600000002000')
        tdSql.query(
            "select * from stable_4096_1 where ts ='2020-09-13 20:26:40.000';")
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 2)
        tdSql.checkData(0, 501, 502)
        tdSql.checkData(0, 1001, 102)
        tdSql.checkData(0, 1501, 1502)
        tdSql.checkData(0, 2001, 2002)
        tdSql.checkData(0, 2501, 'False')
        tdSql.checkData(0, 3001, 3002)
        tdSql.checkData(0, 3501, '3502')
        tdSql.checkData(0, 3801, '3802')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.092')
        tdSql.checkData(0, 4093, '1600000002000')

        tdLog.info(
            "========== test1.2 : insert data , taosdemo force data dropping disk , check data=========="
        )
        tdLog.info("========== regular_table ==========")
        tdSql.execute(
            '''insert into regular_table_2 values( %d , 0, 0, 0, 0, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 200))
        sql = '''select * from regular_table_2 where ts = %d ;''' % (self.ts -
                                                                     200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.execute(
            '''insert into regular_table_2 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts + 200))
        sql = '''select * from regular_table_2 where ts = %d ;''' % (self.ts +
                                                                     200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdSql.execute(
            '''insert into regular_table_2 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts - 500))
        sql = '''select * from regular_table_2 where ts = %d ;''' % (self.ts -
                                                                     500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdSql.execute(
            '''insert into regular_table_2 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts + 500))
        sql = '''select * from regular_table_2 where ts = %d ;''' % (self.ts +
                                                                     500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdLog.info("========== stable ==========")
        tdSql.execute(
            '''insert into table_2 values( %d , 0, 0, 0, 0, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 200))
        sql = '''select * from table_2 where ts = %d ;''' % (self.ts - 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where loc = 'table_2' and ts = %d ;''' % (
            self.ts - 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.execute(
            '''insert into table_2 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts + 200))
        sql = '''select * from table_2 where ts = %d ;''' % (self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)
        sql = '''select * from stable_1 where loc = 'table_2' and ts = %d ;''' % (
            self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdSql.execute(
            '''insert into table_2 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts - 500))
        sql = '''select * from table_2 where ts = %d ;''' % (self.ts - 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)
        sql = '''select * from stable_1 where loc = 'table_2' and ts = %d ;''' % (
            self.ts - 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdSql.execute(
            '''insert into table_2 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts + 500))
        sql = '''select * from table_2 where ts = %d ;''' % (self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)
        sql = '''select * from stable_1 where loc = 'table_2' and ts = %d ;''' % (
            self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdLog.info("========== 4096 regular_table ==========")
        sql = "create table regular_table_4096_2 (ts timestamp, "
        for i in range(500):
            sql += "int_%d int, " % (i + 1)
        for i in range(500, 1000):
            sql += "smallint_%d smallint, " % (i + 1)
        for i in range(1000, 1500):
            sql += "tinyint_%d tinyint, " % (i + 1)
        for i in range(1500, 2000):
            sql += "double_%d double, " % (i + 1)
        for i in range(2000, 2500):
            sql += "float_%d float, " % (i + 1)
        for i in range(2500, 3000):
            sql += "bool_%d bool, " % (i + 1)
        for i in range(3000, 3500):
            sql += "bigint_%d bigint, " % (i + 1)
        for i in range(3500, 3800):
            sql += "nchar_%d nchar(4), " % (i + 1)
        for i in range(3800, 4090):
            sql += "binary_%d binary(10), " % (i + 1)
        for i in range(4090, 4094):
            sql += "timestamp_%d timestamp, " % (i + 1)
        sql += "col4095 binary(22))"
        tdLog.info(len(sql))
        tdSql.execute(sql)

        for i in range(self.num4096):
            sql = "insert into regular_table_4096_2 values(%d, "
            for j in range(4090):
                str = "'%s', " % 'NULL'
                sql += str
            for j in range(4090, 4094):
                str = "%s, " % (self.ts + j)
                sql += str
            sql += "'%s')" % (self.ts + i)
            tdSql.execute(sql % (self.ts + i))
        tdSql.query('''select * from regular_table_4096_2 where ts = %d ;''' %
                    (self.ts))
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 501, None)
        tdSql.checkData(0, 1001, None)
        tdSql.checkData(0, 1501, None)
        tdSql.checkData(0, 2001, None)
        tdSql.checkData(0, 2501, None)
        tdSql.checkData(0, 3001, None)
        tdSql.checkData(0, 3501, 'NULL')
        tdSql.checkData(0, 3801, 'NULL')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4095, '1600000000000')

        sql = '''insert into regular_table_4096_2 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4095 )
                values('2020-09-10 20:26:40.000' , 1 , 501 , 101 , 1501 , 2001 , 1 , 3001 , '3501' , '3801' ,'2020-09-10 20:26:44.090','1500000000000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from regular_table_4096_2 where ts ='2020-09-10 20:26:40.000';"
        )
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4095, '1500000000000')

        tdLog.info("========== 4096 stable ==========")
        sql = "create stable stable_4096_2 (ts timestamp, "
        for i in range(500):
            sql += "int_%d int, " % (i + 1)
        for i in range(500, 1000):
            sql += "smallint_%d smallint, " % (i + 1)
        for i in range(1000, 1500):
            sql += "tinyint_%d tinyint, " % (i + 1)
        for i in range(1500, 2000):
            sql += "double_%d double, " % (i + 1)
        for i in range(2000, 2500):
            sql += "float_%d float, " % (i + 1)
        for i in range(2500, 3000):
            sql += "bool_%d bool, " % (i + 1)
        for i in range(3000, 3500):
            sql += "bigint_%d bigint, " % (i + 1)
        for i in range(3500, 3800):
            sql += "nchar_%d nchar(4), " % (i + 1)
        for i in range(3800, 4090):
            sql += "binary_%d binary(10), " % (i + 1)
        for i in range(4090, 4092):
            sql += "timestamp_%d timestamp, " % (i + 1)
        sql += " col4093 binary(22)) "
        sql += " tags (loc nchar(20),tag_1 int) "
        tdLog.info(len(sql))
        tdSql.execute(sql)

        sql = " create table table_4096_2 using stable_4096_2 tags ('table_4096_2',1); "
        tdSql.execute(sql)

        for i in range(self.num4096):
            sql = "insert into table_4096_2 values(%d, "
            for j in range(4090):
                str = "'%s', " % 'NULL'
                sql += str
            for j in range(4090, 4092):
                str = "%s, " % (self.ts + j)
                sql += str
            sql += "'%s')" % (self.ts + i)
            tdSql.execute(sql % (self.ts + i))
        tdSql.query('''select * from table_4096_2 where ts = %d ;''' %
                    (self.ts))
        tdSql.checkCols(4094)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 501, None)
        tdSql.checkData(0, 1001, None)
        tdSql.checkData(0, 1501, None)
        tdSql.checkData(0, 2001, None)
        tdSql.checkData(0, 2501, None)
        tdSql.checkData(0, 3001, None)
        tdSql.checkData(0, 3501, 'NULL')
        tdSql.checkData(0, 3801, 'NULL')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4093, '1600000000000')
        tdSql.query('''select * from stable_4096_2 where ts = %d ;''' %
                    (self.ts))
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 501, None)
        tdSql.checkData(0, 1001, None)
        tdSql.checkData(0, 1501, None)
        tdSql.checkData(0, 2001, None)
        tdSql.checkData(0, 2501, None)
        tdSql.checkData(0, 3001, None)
        tdSql.checkData(0, 3501, 'NULL')
        tdSql.checkData(0, 3801, 'NULL')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4093, '1600000000000')

        sql = '''insert into table_4096_2 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4093 )
                values('2020-09-10 20:26:40.000' , 1 , 501 , 101 , 1501 , 2001 , 1 , 3001 , '3501' , '3801' ,'2020-09-10 20:26:44.090','1500000000000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from table_4096_2 where ts ='2020-09-10 20:26:40.000';")
        tdSql.checkCols(4094)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4093, '1500000000000')
        tdSql.query(
            "select * from stable_4096_2 where ts ='2020-09-10 20:26:40.000';")
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4093, '1500000000000')

        # taosdemo force data dropping disk
        buildPath = self.getBuildPath()
        if (buildPath == ""):
            tdLog.exit("taosd not found!")
        else:
            tdLog.info("taosd found in %s" % buildPath)
        binPath = buildPath + "/build/bin/"
        os.system("%staosdemo -N -d taosdemo -t 100 -n 100 -l 1000 -y" %
                  binPath)

        tdLog.info("========== stable ==========")
        tdSql.execute(
            '''insert into table_2 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts - 200))
        sql = '''select * from table_2 where ts = %d ;''' % (self.ts - 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where loc = 'table_2' and ts = %d ;''' % (
            self.ts - 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.execute(
            '''insert into table_2 values( %d , 0, 0, 0, 0, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 200))
        sql = '''select * from table_2 where ts = %d ;''' % (self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+0')
        tdSql.checkData(0, 7, 'nchar+0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where loc = 'table_2' and ts = %d ;''' % (
            self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+0')
        tdSql.checkData(0, 7, 'nchar+0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.execute(
            '''insert into table_2 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts + 200))
        sql = '''select * from table_1 where ts = %d ;''' % (self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+0')
        tdSql.checkData(0, 7, 'nchar+0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where loc = 'table_2' and ts = %d ;''' % (
            self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+0')
        tdSql.checkData(0, 7, 'nchar+0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.error(
            '''insert into table_2 values( %d , -2147483648, -9223372036854775807, -32767, -127, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into table_2 values( %d , -2147483647, -9223372036854775808, -32767, -127, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into table_2 values( %d , -2147483647, -9223372036854775807, -32768, -127, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into table_2 values( %d , -2147483647, -9223372036854775807, -32767, -128, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into table_2 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-0123', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into table_2 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-0', 'nchar-01234', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))

        tdSql.execute(
            '''insert into table_2 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-012', 'nchar-0123', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        sql = '''select * from table_2 where ts = %d ;''' % (self.ts - 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, -2147483647)
        tdSql.checkData(0, 2, -9223372036854775807)
        tdSql.checkData(0, 3, -32767)
        tdSql.checkData(0, 4, -127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-012')
        tdSql.checkData(0, 7, 'nchar-0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:44.090')
        sql = '''select * from stable_1 where loc = 'table_2' and ts = %d ;''' % (
            self.ts - 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, -2147483647)
        tdSql.checkData(0, 2, -9223372036854775807)
        tdSql.checkData(0, 3, -32767)
        tdSql.checkData(0, 4, -127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-012')
        tdSql.checkData(0, 7, 'nchar-0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:44.090')

        tdSql.error(
            '''insert into table_2 values( %d , 2147483648, 9223372036854775807, 32767, 127, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into table_2 values( %d , 2147483647, 9223372036854775808, 32767, 127, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into table_2 values( %d , 2147483647, 9223372036854775807, 32768, 127, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into table_2 values( %d , 2147483647, 9223372036854775807, 32767, 128, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into table_2 values( %d , 2147483647, 9223372036854775807, 32767, 127, 0, 'binary+0123', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into table_2 values( %d , 2147483647, 9223372036854775807, 32767, 127, 0, 'binary+0', 'nchar+01234', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))

        tdSql.execute(
            '''insert into table_2 values( %d , 2147483647, 9223372036854775807, 32767, 127, 0, 'binary+012', 'nchar+0123', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        sql = '''select * from table_2 where ts = %d ;''' % (self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 2147483647)
        tdSql.checkData(0, 2, 9223372036854775807)
        tdSql.checkData(0, 3, 32767)
        tdSql.checkData(0, 4, 127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+012')
        tdSql.checkData(0, 7, 'nchar+0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:44.090')
        sql = '''select * from stable_1 where loc = 'table_2' and ts = %d ;''' % (
            self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 2147483647)
        tdSql.checkData(0, 2, 9223372036854775807)
        tdSql.checkData(0, 3, 32767)
        tdSql.checkData(0, 4, 127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+012')
        tdSql.checkData(0, 7, 'nchar+0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:44.090')
        tdSql.execute(
            '''insert into table_2 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-012', 'nchar-0123', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        sql = '''select * from table_1 where ts = %d ;''' % (self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, -2147483647)
        tdSql.checkData(0, 2, -9223372036854775807)
        tdSql.checkData(0, 3, -32767)
        tdSql.checkData(0, 4, -127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-012')
        tdSql.checkData(0, 7, 'nchar-0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where loc = 'table_2' and ts = %d ;''' % (
            self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, -2147483647)
        tdSql.checkData(0, 2, -9223372036854775807)
        tdSql.checkData(0, 3, -32767)
        tdSql.checkData(0, 4, -127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-012')
        tdSql.checkData(0, 7, 'nchar-0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdLog.info("========== 4096 regular_table ==========")
        sql = '''insert into regular_table_4096_2 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4095 )
                values('2020-09-13 20:26:40.000' , 1 , 501 , 101 , 1501 , 2001 , 1 , 3001 , '3501' , '3801' ,'2020-09-13 20:26:44.090','1600000000000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from regular_table_4096_2 where ts ='2020-09-13 20:26:40.000';"
        )
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4095, '1600000000000')

        sql = '''insert into regular_table_4096_2 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4095 )
                values('2020-09-10 20:26:40.000' , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL);'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from regular_table_4096_2 where ts ='2020-09-10 20:26:40.000';"
        )
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4095, '1500000000000')

        sql = '''insert into regular_table_4096_2 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4095 )
                values('2020-09-13 20:26:40.000' , 2 , 502 , 102 , 1502 , 2002 , 0 , 3002 , '3502' , '3802' ,'2020-09-13 20:26:44.092','1600000002000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from regular_table_4096_2 where ts ='2020-09-13 20:26:40.000';"
        )
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 2)
        tdSql.checkData(0, 501, 502)
        tdSql.checkData(0, 1001, 102)
        tdSql.checkData(0, 1501, 1502)
        tdSql.checkData(0, 2001, 2002)
        tdSql.checkData(0, 2501, 'False')
        tdSql.checkData(0, 3001, 3002)
        tdSql.checkData(0, 3501, '3502')
        tdSql.checkData(0, 3801, '3802')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.092')
        tdSql.checkData(0, 4095, '1600000002000')

        tdLog.info("========== 4096 stable ==========")
        sql = '''insert into table_4096_2 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4093 )
                values('2020-09-13 20:26:40.000' , 1 , 501 , 101 , 1501 , 2001 , 1 , 3001 , '3501' , '3801' ,'2020-09-13 20:26:44.090','1600000000000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from table_4096_2 where ts ='2020-09-13 20:26:40.000';")
        tdSql.checkCols(4094)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4093, '1600000000000')
        tdSql.query(
            "select * from stable_4096_2 where ts ='2020-09-13 20:26:40.000';")
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4093, '1600000000000')

        sql = '''insert into table_4096_2 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4093 )
                values('2020-09-10 20:26:40.000' , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL);'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from table_4096_2 where ts ='2020-09-10 20:26:40.000';")
        tdSql.checkCols(4094)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4093, '1500000000000')
        tdSql.query(
            "select * from stable_4096_2 where ts ='2020-09-10 20:26:40.000';")
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4093, '1500000000000')

        sql = '''insert into table_4096_2 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4093 )
                values('2020-09-13 20:26:40.000' , 2 , 502 , 102 , 1502 , 2002 , 0 , 3002 , '3502' , '3802' ,'2020-09-13 20:26:44.092','1600000002000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from table_4096_2 where ts ='2020-09-13 20:26:40.000';")
        tdSql.checkCols(4094)
        tdSql.checkData(0, 1, 2)
        tdSql.checkData(0, 501, 502)
        tdSql.checkData(0, 1001, 102)
        tdSql.checkData(0, 1501, 1502)
        tdSql.checkData(0, 2001, 2002)
        tdSql.checkData(0, 2501, 'False')
        tdSql.checkData(0, 3001, 3002)
        tdSql.checkData(0, 3501, '3502')
        tdSql.checkData(0, 3801, '3802')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.092')
        tdSql.checkData(0, 4093, '1600000002000')
        tdSql.query(
            "select * from stable_4096_2 where ts ='2020-09-13 20:26:40.000';")
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 2)
        tdSql.checkData(0, 501, 502)
        tdSql.checkData(0, 1001, 102)
        tdSql.checkData(0, 1501, 1502)
        tdSql.checkData(0, 2001, 2002)
        tdSql.checkData(0, 2501, 'False')
        tdSql.checkData(0, 3001, 3002)
        tdSql.checkData(0, 3501, '3502')
        tdSql.checkData(0, 3801, '3802')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.092')
        tdSql.checkData(0, 4093, '1600000002000')

        tdLog.info(
            "========== test1.3 : insert data , tdDnodes restart force data dropping disk , check data=========="
        )
        tdLog.info("========== regular_table ==========")
        tdSql.execute(
            '''insert into regular_table_3 values( %d , 0, 0, 0, 0, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 200))
        sql = '''select * from regular_table_3 where ts = %d ;''' % (self.ts -
                                                                     200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.execute(
            '''insert into regular_table_3 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts + 200))
        sql = '''select * from regular_table_3 where ts = %d ;''' % (self.ts +
                                                                     200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdSql.execute(
            '''insert into regular_table_3 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts - 500))
        sql = '''select * from regular_table_3 where ts = %d ;''' % (self.ts -
                                                                     500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdSql.execute(
            '''insert into regular_table_3 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts + 500))
        sql = '''select * from regular_table_3 where ts = %d ;''' % (self.ts +
                                                                     500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdLog.info("========== stable ==========")
        tdSql.execute(
            '''insert into table_3 values( %d , 0, 0, 0, 0, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 200))
        sql = '''select * from table_3 where ts = %d ;''' % (self.ts - 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where loc = 'table_3' and ts = %d ;''' % (
            self.ts - 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.execute(
            '''insert into table_3 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts + 200))
        sql = '''select * from table_3 where ts = %d ;''' % (self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)
        sql = '''select * from stable_1 where loc = 'table_3' and ts = %d ;''' % (
            self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdSql.execute(
            '''insert into table_3 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts - 500))
        sql = '''select * from table_3 where ts = %d ;''' % (self.ts - 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)
        sql = '''select * from stable_1 where loc = 'table_3' and ts = %d ;''' % (
            self.ts - 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdSql.execute(
            '''insert into table_3 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts + 500))
        sql = '''select * from table_3 where ts = %d ;''' % (self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)
        sql = '''select * from stable_1 where loc = 'table_3' and ts = %d ;''' % (
            self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 2, None)
        tdSql.checkData(0, 3, None)
        tdSql.checkData(0, 4, None)
        tdSql.checkData(0, 5, None)
        tdSql.checkData(0, 6, None)
        tdSql.checkData(0, 7, None)
        tdSql.checkData(0, 8, None)
        tdSql.checkData(0, 9, None)
        tdSql.checkData(0, 10, None)

        tdLog.info("========== 4096 regular_table ==========")
        sql = "create table regular_table_4096_3 (ts timestamp, "
        for i in range(500):
            sql += "int_%d int, " % (i + 1)
        for i in range(500, 1000):
            sql += "smallint_%d smallint, " % (i + 1)
        for i in range(1000, 1500):
            sql += "tinyint_%d tinyint, " % (i + 1)
        for i in range(1500, 2000):
            sql += "double_%d double, " % (i + 1)
        for i in range(2000, 2500):
            sql += "float_%d float, " % (i + 1)
        for i in range(2500, 3000):
            sql += "bool_%d bool, " % (i + 1)
        for i in range(3000, 3500):
            sql += "bigint_%d bigint, " % (i + 1)
        for i in range(3500, 3800):
            sql += "nchar_%d nchar(4), " % (i + 1)
        for i in range(3800, 4090):
            sql += "binary_%d binary(10), " % (i + 1)
        for i in range(4090, 4094):
            sql += "timestamp_%d timestamp, " % (i + 1)
        sql += "col4095 binary(22))"
        tdLog.info(len(sql))
        tdSql.execute(sql)

        for i in range(self.num4096):
            sql = "insert into regular_table_4096_3 values(%d, "
            for j in range(4090):
                str = "'%s', " % 'NULL'
                sql += str
            for j in range(4090, 4094):
                str = "%s, " % (self.ts + j)
                sql += str
            sql += "'%s')" % (self.ts + i)
            tdSql.execute(sql % (self.ts + i))
        tdSql.query('''select * from regular_table_4096_3 where ts = %d ;''' %
                    (self.ts))
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 501, None)
        tdSql.checkData(0, 1001, None)
        tdSql.checkData(0, 1501, None)
        tdSql.checkData(0, 2001, None)
        tdSql.checkData(0, 2501, None)
        tdSql.checkData(0, 3001, None)
        tdSql.checkData(0, 3501, 'NULL')
        tdSql.checkData(0, 3801, 'NULL')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4095, '1600000000000')

        sql = '''insert into regular_table_4096_3 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4095 )
                values('2020-09-10 20:26:40.000' , 1 , 501 , 101 , 1501 , 2001 , 1 , 3001 , '3501' , '3801' ,'2020-09-10 20:26:44.090','1500000000000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from regular_table_4096_3 where ts ='2020-09-10 20:26:40.000';"
        )
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4095, '1500000000000')

        tdLog.info("========== 4096 stable ==========")
        sql = "create stable stable_4096_3 (ts timestamp, "
        for i in range(500):
            sql += "int_%d int, " % (i + 1)
        for i in range(500, 1000):
            sql += "smallint_%d smallint, " % (i + 1)
        for i in range(1000, 1500):
            sql += "tinyint_%d tinyint, " % (i + 1)
        for i in range(1500, 2000):
            sql += "double_%d double, " % (i + 1)
        for i in range(2000, 2500):
            sql += "float_%d float, " % (i + 1)
        for i in range(2500, 3000):
            sql += "bool_%d bool, " % (i + 1)
        for i in range(3000, 3500):
            sql += "bigint_%d bigint, " % (i + 1)
        for i in range(3500, 3800):
            sql += "nchar_%d nchar(4), " % (i + 1)
        for i in range(3800, 4090):
            sql += "binary_%d binary(10), " % (i + 1)
        for i in range(4090, 4092):
            sql += "timestamp_%d timestamp, " % (i + 1)
        sql += " col4093 binary(22)) "
        sql += " tags (loc nchar(20),tag_1 int) "
        tdLog.info(len(sql))
        tdSql.execute(sql)

        sql = " create table table_4096_3 using stable_4096_3 tags ('table_4096_3',1); "
        tdSql.execute(sql)

        for i in range(self.num4096):
            sql = "insert into table_4096_3 values(%d, "
            for j in range(4090):
                str = "'%s', " % 'NULL'
                sql += str
            for j in range(4090, 4092):
                str = "%s, " % (self.ts + j)
                sql += str
            sql += "'%s')" % (self.ts + i)
            tdSql.execute(sql % (self.ts + i))
        tdSql.query('''select * from table_4096_3 where ts = %d ;''' %
                    (self.ts))
        tdSql.checkCols(4094)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 501, None)
        tdSql.checkData(0, 1001, None)
        tdSql.checkData(0, 1501, None)
        tdSql.checkData(0, 2001, None)
        tdSql.checkData(0, 2501, None)
        tdSql.checkData(0, 3001, None)
        tdSql.checkData(0, 3501, 'NULL')
        tdSql.checkData(0, 3801, 'NULL')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4093, '1600000000000')
        tdSql.query('''select * from stable_4096_3 where ts = %d ;''' %
                    (self.ts))
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, None)
        tdSql.checkData(0, 501, None)
        tdSql.checkData(0, 1001, None)
        tdSql.checkData(0, 1501, None)
        tdSql.checkData(0, 2001, None)
        tdSql.checkData(0, 2501, None)
        tdSql.checkData(0, 3001, None)
        tdSql.checkData(0, 3501, 'NULL')
        tdSql.checkData(0, 3801, 'NULL')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4093, '1600000000000')

        sql = '''insert into table_4096_3 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4093 )
                values('2020-09-10 20:26:40.000' , 1 , 501 , 101 , 1501 , 2001 , 1 , 3001 , '3501' , '3801' ,'2020-09-10 20:26:44.090','1500000000000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from table_4096_3 where ts ='2020-09-10 20:26:40.000';")
        tdSql.checkCols(4094)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4093, '1500000000000')
        tdSql.query(
            "select * from stable_4096_3 where ts ='2020-09-10 20:26:40.000';")
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4093, '1500000000000')

        # tdDnodes restart force data dropping disk
        tdDnodes.stopAll()
        tdDnodes.start()

        tdLog.info("========== regular_table ==========")
        tdSql.execute(
            '''insert into regular_table_3 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts - 200))
        sql = '''select * from regular_table_3 where ts = %d ;''' % (self.ts -
                                                                     200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.execute(
            '''insert into regular_table_3 values( %d , 0, 0, 0, 0, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 200))
        sql = '''select * from regular_table_3 where ts = %d ;''' % (self.ts +
                                                                     200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+0')
        tdSql.checkData(0, 7, 'nchar+0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        tdSql.execute(
            '''insert into regular_table_3 values( %d , 1, 1, 1, 1, 1, 'binary+1', 'nchar+1', 1.000000, 1.000000, 1600000001000);'''
            % (self.ts + 200))
        sql = '''select * from regular_table_3 where ts = %d ;''' % (self.ts +
                                                                     200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 2, 1)
        tdSql.checkData(0, 3, 1)
        tdSql.checkData(0, 4, 1)
        tdSql.checkData(0, 5, 'True')
        tdSql.checkData(0, 6, 'binary+1')
        tdSql.checkData(0, 7, 'nchar+1')
        tdSql.checkData(0, 8, 1)
        tdSql.checkData(0, 9, 1)
        tdSql.checkData(0, 10, '2020-09-13 20:26:41.000')

        tdSql.error(
            '''insert into regular_table_3 values( %d , -2147483648, -9223372036854775807, -32767, -127, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into regular_table_3 values( %d , -2147483647, -9223372036854775808, -32767, -127, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into regular_table_3 values( %d , -2147483647, -9223372036854775807, -32768, -127, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into regular_table_3 values( %d , -2147483647, -9223372036854775807, -32767, -128, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into regular_table_3 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-0123', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into regular_table_3 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-0', 'nchar-01234', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))

        tdSql.execute(
            '''insert into regular_table_3 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-012', 'nchar-0123', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        sql = '''select * from regular_table_3 where ts = %d ;''' % (self.ts -
                                                                     500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, -2147483647)
        tdSql.checkData(0, 2, -9223372036854775807)
        tdSql.checkData(0, 3, -32767)
        tdSql.checkData(0, 4, -127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-012')
        tdSql.checkData(0, 7, 'nchar-0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:44.090')

        tdSql.error(
            '''insert into regular_table_3 values( %d , 2147483648, 9223372036854775807, 32767, 127, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into regular_table_3 values( %d , 2147483647, 9223372036854775808, 32767, 127, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into regular_table_3 values( %d , 2147483647, 9223372036854775807, 32768, 127, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into regular_table_3 values( %d , 2147483647, 9223372036854775807, 32767, 128, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into regular_table_3 values( %d , 2147483647, 9223372036854775807, 32767, 127, 0, 'binary+0123', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into regular_table_3 values( %d , 2147483647, 9223372036854775807, 32767, 127, 0, 'binary+0', 'nchar+01234', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))

        tdSql.execute(
            '''insert into regular_table_3 values( %d , 2147483647, 9223372036854775807, 32767, 127, 0, 'binary+012', 'nchar+0123', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        sql = '''select * from regular_table_3 where ts = %d ;''' % (self.ts +
                                                                     500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 2147483647)
        tdSql.checkData(0, 2, 9223372036854775807)
        tdSql.checkData(0, 3, 32767)
        tdSql.checkData(0, 4, 127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+012')
        tdSql.checkData(0, 7, 'nchar+0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:44.090')
        tdSql.execute(
            '''insert into regular_table_3 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-012', 'nchar-0123', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        sql = '''select * from regular_table_3 where ts = %d ;''' % (self.ts +
                                                                     500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, -2147483647)
        tdSql.checkData(0, 2, -9223372036854775807)
        tdSql.checkData(0, 3, -32767)
        tdSql.checkData(0, 4, -127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-012')
        tdSql.checkData(0, 7, 'nchar-0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdLog.info("========== stable ==========")
        tdSql.execute(
            '''insert into table_3 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts - 200))
        sql = '''select * from table_3 where ts = %d ;''' % (self.ts - 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where loc = 'table_3' and ts = %d ;''' % (
            self.ts - 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-0')
        tdSql.checkData(0, 7, 'nchar-0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.execute(
            '''insert into table_3 values( %d , 0, 0, 0, 0, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 200))
        sql = '''select * from table_3 where ts = %d ;''' % (self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+0')
        tdSql.checkData(0, 7, 'nchar+0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where loc = 'table_3' and ts = %d ;''' % (
            self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+0')
        tdSql.checkData(0, 7, 'nchar+0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.execute(
            '''insert into table_3 values( %d , NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);'''
            % (self.ts + 200))
        sql = '''select * from table_3 where ts = %d ;''' % (self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+0')
        tdSql.checkData(0, 7, 'nchar+0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where loc = 'table_3' and ts = %d ;''' % (
            self.ts + 200)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 0)
        tdSql.checkData(0, 2, 0)
        tdSql.checkData(0, 3, 0)
        tdSql.checkData(0, 4, 0)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+0')
        tdSql.checkData(0, 7, 'nchar+0')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdSql.error(
            '''insert into table_3 values( %d , -2147483648, -9223372036854775807, -32767, -127, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into table_3 values( %d , -2147483647, -9223372036854775808, -32767, -127, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into table_3 values( %d , -2147483647, -9223372036854775807, -32768, -127, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into table_3 values( %d , -2147483647, -9223372036854775807, -32767, -128, 0, 'binary-0', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into table_3 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-0123', 'nchar-0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        tdSql.error(
            '''insert into table_3 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-0', 'nchar-01234', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))

        tdSql.execute(
            '''insert into table_3 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-012', 'nchar-0123', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts - 500))
        sql = '''select * from table_3 where ts = %d ;''' % (self.ts - 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, -2147483647)
        tdSql.checkData(0, 2, -9223372036854775807)
        tdSql.checkData(0, 3, -32767)
        tdSql.checkData(0, 4, -127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-012')
        tdSql.checkData(0, 7, 'nchar-0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:44.090')
        sql = '''select * from stable_1 where loc = 'table_3' and ts = %d ;''' % (
            self.ts - 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, -2147483647)
        tdSql.checkData(0, 2, -9223372036854775807)
        tdSql.checkData(0, 3, -32767)
        tdSql.checkData(0, 4, -127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-012')
        tdSql.checkData(0, 7, 'nchar-0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:44.090')

        tdSql.error(
            '''insert into table_3 values( %d , 2147483648, 9223372036854775807, 32767, 127, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into table_3 values( %d , 2147483647, 9223372036854775808, 32767, 127, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into table_3 values( %d , 2147483647, 9223372036854775807, 32768, 127, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into table_3 values( %d , 2147483647, 9223372036854775807, 32767, 128, 0, 'binary+0', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into table_3 values( %d , 2147483647, 9223372036854775807, 32767, 127, 0, 'binary+0123', 'nchar+0', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        tdSql.error(
            '''insert into table_3 values( %d , 2147483647, 9223372036854775807, 32767, 127, 0, 'binary+0', 'nchar+01234', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))

        tdSql.execute(
            '''insert into table_3 values( %d , 2147483647, 9223372036854775807, 32767, 127, 0, 'binary+012', 'nchar+0123', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        sql = '''select * from table_3 where ts = %d ;''' % (self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 2147483647)
        tdSql.checkData(0, 2, 9223372036854775807)
        tdSql.checkData(0, 3, 32767)
        tdSql.checkData(0, 4, 127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+012')
        tdSql.checkData(0, 7, 'nchar+0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:44.090')
        sql = '''select * from stable_1 where loc = 'table_3' and ts = %d ;''' % (
            self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, 2147483647)
        tdSql.checkData(0, 2, 9223372036854775807)
        tdSql.checkData(0, 3, 32767)
        tdSql.checkData(0, 4, 127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary+012')
        tdSql.checkData(0, 7, 'nchar+0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:44.090')
        tdSql.execute(
            '''insert into table_3 values( %d , -2147483647, -9223372036854775807, -32767, -127, 0, 'binary-012', 'nchar-0123', 0.000000, 0.000000, 1600000000000);'''
            % (self.ts + 500))
        sql = '''select * from table_3 where ts = %d ;''' % (self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, -2147483647)
        tdSql.checkData(0, 2, -9223372036854775807)
        tdSql.checkData(0, 3, -32767)
        tdSql.checkData(0, 4, -127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-012')
        tdSql.checkData(0, 7, 'nchar-0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')
        sql = '''select * from stable_1 where loc = 'table_3' and ts = %d ;''' % (
            self.ts + 500)
        tdSql.query(sql)
        tdSql.checkData(0, 1, -2147483647)
        tdSql.checkData(0, 2, -9223372036854775807)
        tdSql.checkData(0, 3, -32767)
        tdSql.checkData(0, 4, -127)
        tdSql.checkData(0, 5, 'False')
        tdSql.checkData(0, 6, 'binary-012')
        tdSql.checkData(0, 7, 'nchar-0123')
        tdSql.checkData(0, 8, 0)
        tdSql.checkData(0, 9, 0)
        tdSql.checkData(0, 10, '2020-09-13 20:26:40.000')

        tdLog.info("========== 4096 regular_table ==========")
        sql = '''insert into regular_table_4096_3 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4095 )
                values('2020-09-13 20:26:40.000' , 1 , 501 , 101 , 1501 , 2001 , 1 , 3001 , '3501' , '3801' ,'2020-09-13 20:26:44.090','1600000000000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from regular_table_4096_3 where ts ='2020-09-13 20:26:40.000';"
        )
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4095, '1600000000000')

        sql = '''insert into regular_table_4096_3 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4095 )
                values('2020-09-10 20:26:40.000' , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL);'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from regular_table_4096_3 where ts ='2020-09-10 20:26:40.000';"
        )
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4095, '1500000000000')

        sql = '''insert into regular_table_4096_3 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4095 )
                values('2020-09-13 20:26:40.000' , 2 , 502 , 102 , 1502 , 2002 , 0 , 3002 , '3502' , '3802' ,'2020-09-13 20:26:44.092','1600000002000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from regular_table_4096_3 where ts ='2020-09-13 20:26:40.000';"
        )
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 2)
        tdSql.checkData(0, 501, 502)
        tdSql.checkData(0, 1001, 102)
        tdSql.checkData(0, 1501, 1502)
        tdSql.checkData(0, 2001, 2002)
        tdSql.checkData(0, 2501, 'False')
        tdSql.checkData(0, 3001, 3002)
        tdSql.checkData(0, 3501, '3502')
        tdSql.checkData(0, 3801, '3802')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.092')
        tdSql.checkData(0, 4095, '1600000002000')

        tdLog.info("========== 4096 stable ==========")
        sql = '''insert into table_4096_3 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4093 )
                values('2020-09-13 20:26:40.000' , 1 , 501 , 101 , 1501 , 2001 , 1 , 3001 , '3501' , '3801' ,'2020-09-13 20:26:44.090','1600000000000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from table_4096_3 where ts ='2020-09-13 20:26:40.000';")
        tdSql.checkCols(4094)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4093, '1600000000000')
        tdSql.query(
            "select * from stable_4096_3 where ts ='2020-09-13 20:26:40.000';")
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.090')
        tdSql.checkData(0, 4093, '1600000000000')

        sql = '''insert into table_4096_3 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4093 )
                values('2020-09-10 20:26:40.000' , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL , NULL);'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from table_4096_3 where ts ='2020-09-10 20:26:40.000';")
        tdSql.checkCols(4094)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4093, '1500000000000')
        tdSql.query(
            "select * from stable_4096_3 where ts ='2020-09-10 20:26:40.000';")
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 1)
        tdSql.checkData(0, 501, 501)
        tdSql.checkData(0, 1001, 101)
        tdSql.checkData(0, 1501, 1501)
        tdSql.checkData(0, 2001, 2001)
        tdSql.checkData(0, 2501, 'True')
        tdSql.checkData(0, 3001, 3001)
        tdSql.checkData(0, 3501, '3501')
        tdSql.checkData(0, 3801, '3801')
        tdSql.checkData(0, 4091, '2020-09-10 20:26:44.090')
        tdSql.checkData(0, 4093, '1500000000000')

        sql = '''insert into table_4096_3 (ts , int_1,smallint_501 , tinyint_1001 , double_1501 , float_2001 , bool_2501 ,
                bigint_3001 , nchar_3501 , binary_3801 , timestamp_4091 , col4093 )
                values('2020-09-13 20:26:40.000' , 2 , 502 , 102 , 1502 , 2002 , 0 , 3002 , '3502' , '3802' ,'2020-09-13 20:26:44.092','1600000002000');'''
        tdSql.execute(sql)
        tdSql.query(
            "select * from table_4096_3 where ts ='2020-09-13 20:26:40.000';")
        tdSql.checkCols(4094)
        tdSql.checkData(0, 1, 2)
        tdSql.checkData(0, 501, 502)
        tdSql.checkData(0, 1001, 102)
        tdSql.checkData(0, 1501, 1502)
        tdSql.checkData(0, 2001, 2002)
        tdSql.checkData(0, 2501, 'False')
        tdSql.checkData(0, 3001, 3002)
        tdSql.checkData(0, 3501, '3502')
        tdSql.checkData(0, 3801, '3802')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.092')
        tdSql.checkData(0, 4093, '1600000002000')
        tdSql.query(
            "select * from stable_4096_3 where ts ='2020-09-13 20:26:40.000';")
        tdSql.checkCols(4096)
        tdSql.checkData(0, 1, 2)
        tdSql.checkData(0, 501, 502)
        tdSql.checkData(0, 1001, 102)
        tdSql.checkData(0, 1501, 1502)
        tdSql.checkData(0, 2001, 2002)
        tdSql.checkData(0, 2501, 'False')
        tdSql.checkData(0, 3001, 3002)
        tdSql.checkData(0, 3501, '3502')
        tdSql.checkData(0, 3801, '3802')
        tdSql.checkData(0, 4091, '2020-09-13 20:26:44.092')
        tdSql.checkData(0, 4093, '1600000002000')

        endTime = time.time()
        print("total time %ds" % (endTime - startTime))

    def stop(self):
        tdSql.close()
        tdLog.success("%s successfully executed" % __file__)


tdCases.addWindows(__file__, TDTestCase())
tdCases.addLinux(__file__, TDTestCase())