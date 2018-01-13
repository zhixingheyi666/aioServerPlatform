# _*_coding:utf-8_*_

__author__ = 'Master Wang'
# 并不理解"处处异步",但是先仿照着写上用用看
import asyncio
# self#
# 程序中用到了深度复制，这里引进相应模块
from copy import deepcopy

# self#
# 为方便分步测试，这里直接引入数据库操纵语句。
from orm import select

# 为自定义的模块添加搜索路径
import sys

sysFc = 'D:\\python_learn\\sysFc'
sys.path.append(sysFc)

from logSf10 import crLog

logger = crLog(fname='D:\桌面\exCodOut.log')
# logger = crLog(fname = 'D:\桌面\handlers.log')
logger.info('Succeed')


@asyncio.coroutine
def codeen(searchMeta, colName='line', tableName='fline_code', database='fortest', **kw):
    sqlI = 'select hashid, flid from ' + tableName + ' where ' + colName + ' regexp "' + searchMeta + '"'
    origin = yield from select(sqlI, '', database=database)
    if len(origin) != 0:
        row = deepcopy(origin[0])
        row['flid'] = [[row['flid']]]
        # preResult存储查询结果域，是一个list，他的每一个元素是dict，
        # 每个元素的第一个键为hashid，表示不同的文件，第二键为list，list的内部元素依然是list(表示查询到的flid按域范围分的组)
        preResult = [row]
        # 可以看出很多查询结果按照前后5行的标准是重复的，可以合并的。
        # 合并算法：如果两个flid的值相差为11或比11小，则认为两个域值接续或者重合
        # 否则，视为两个独立的结果输出。
        # 合并结果#
        for oi in origin:
            # 通过mysql测试，lineNum(记录代码在源文件中第几行的数字，数据库列名为flid)超范围查询不会报错
            # 查询结果先按照lineNum排序，然后按照下面算法合并结果
            lineNum = oi['flid']
            mNew = 1
            for pri in preResult:
                if pri['hashid'] == oi['hashid']:
                    if lineNum - pri['flid'][-1][-1] > 11:
                        pri['flid'].append([lineNum])
                    else:
                        pri['flid'][-1].append(lineNum)
                    mNew = 0
            # 如果上面循环完毕，不存在hashid与li['hashid']相等(mNew为1)，则发现新文件内容，用下面语句向rs添加
            if mNew:
                row = deepcopy(oi)
                row['flid'] = [[lineNum]]
                preResult.append(row)
        logger.info(str(origin[:10]))
        # 根据整理好的flid范围重新检索需要的结果
        result = []
        sqlII = 'select flid, line from ' + tableName + ' where hashid = ? and flid between ? and ? '
        for pri in preResult:
            for numi in pri['flid']:
                data = yield from select(sqlII, (pri['hashid'], numi[0] - 5, numi[-1] + 5), database='fortest')
                result.append(data)
    elif len(origin) == 0:
        result = [[{'flid': -1, 'line': 'No match result!'}]]
    else:
        result = [[{'flid': -2, 'line': "Unknown Errors! \nModule: dataengine \nFunction: codeen(searchMeta, colName='line', tableName='fline_code', database='fortest', **kw)"}]]
    return result
