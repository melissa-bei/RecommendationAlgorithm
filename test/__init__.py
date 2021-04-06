#########################################################
# 将根目录加入sys.path中,解决命令行找不到包的问题
import sys
import os
curPath = os.path.dirname(os.path.abspath(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
#########################################################
