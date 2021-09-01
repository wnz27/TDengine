###################################################################
#       Copyright (c) 2016 by TAOS Technologies, Inc.
#             All rights reserved.
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
from util.log import *
from util.cases import *
from util.sql import *
from util.dnodes import *


class TDTestCase:
    def init(self, conn, logSql):
        tdLog.debug("start to execute %s" % __file__)
        tdSql.init(conn.cursor(), logSql)

    def run(self):
        self.ntables = 1
        self.startTime = 1520000010000

        tdSql.prepare()

        tdLog.info("================= step1")
        tdLog.info("create 1 table")
        tdSql.execute('create table tb1 (ts timestamp, speed int)')
        tdLog.info("one block can import 38 records")

        tdLog.info("================= step2")
        tdLog.info("import 76 sequential data")
        startTime = self.startTime
        sqlcmd = ['import into tb1 values']
        for rid in range(1, 11):
            sqlcmd.append('(%ld, %d)' % (startTime + rid, rid))
        for rid in range(15, 81):
            sqlcmd.append('(%ld, %d)' % (startTime + rid, rid))
        tdSql.execute(" ".join(sqlcmd))

        tdLog.info("================= step3")
        tdSql.query('select * from tb1')
        tdSql.checkRows(76)

        tdLog.info("================= step4")
        tdLog.info("import 20 data before with partly overlap")
        startTime = self.startTime - 5
        sqlcmd = ['import into tb1 values']
        for rid in range(1, 21):
            sqlcmd.append('(%ld, %d)' % (startTime + rid, rid))
        tdSql.execute(" ".join(sqlcmd))

        tdLog.info("================= step5")
        tdSql.query('select * from tb1')
        tdSql.checkRows(85)

    def stop(self):
        tdSql.close()
        tdLog.success("%s successfully executed" % __file__)


tdCases.addWindows(__file__, TDTestCase())
tdCases.addLinux(__file__, TDTestCase())
