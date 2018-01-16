
import os, sys
"""
    下面这段代码要求日志文件，也即exCodOut.log，与本文件(mylog.py)的父目录在同一文件夹下面
"""
# 本句 os.path.realpath( sys.argv[0] ) 获取本文件所在的实际完整路径，然后分割取第一部分，去除文件名，仅留下路径
ScriptPath = os.path.split( os.path.realpath( sys.argv[0] ) )[0]
# 本句根据前面的路径获取父路径的父路径(也就是sysFc的父路径)
ScriptPath = os.path.abspath(os.path.join(ScriptPath,".."))
from logSf10 import crLog

logger = crLog( fname= os.path.abspath(os.path.join(ScriptPath,"exCodOut.log")) )
logger.info('Succeed defination logger')