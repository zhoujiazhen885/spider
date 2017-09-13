#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

2017-8-21 V2.0 该程序用来收集服务器上的日志信息，用以替代人工去服务器查询关键字的工作，解放人力。
该版比第一版新增多进程功能。作者-周佳振，上海。

"""
import subprocess
import os
from multiprocessing import Pool
import time
import random

# 获取用户的输入
def getInputWords():
    componentName = raw_input("请输入要查找的组件名(如APP/WEB，与配置文件名称一致）或者要查找的服务器IP地址，如果要查找全部服务器请输入(ALL):").upper()
    keyWord = raw_input("请输入要查找的日志关键字：")
    return componentName, keyWord

# 根据用户输入，读取配置文件，输出IP和日志文件全路径
def exportConf(componentName):
    # componentName
    # 查找所有服务器
    if componentName == 'ALL':
        # 将IP和logFile匹配成字典
        dict1 = {}
        lines = open(conf)
        for line in lines:
            f = line.split(':')[1]
            print f
            f = f.split(',')
            for value in f:
                ip = value.split('|')[0]
                logFile = value.split('|')[1]
                dict1[ip] = logFile
        lines.close()
        return dict1

        # 查找单台服务器
    elif componentName[0 - 2] == '10.':
        # 将IP和logFile匹配成字典
        dict1 = {}
        lines = open(conf)
        for line in lines:
            f = line.split(':')[1]
            print f
            f = f.split(',')
            for value in f:
                ip = value.split('|')[0]
                logFile = value.split('|')[1]
                dict1[ip] = logFile
        lines.close()
        if componentName in dict1:
            item =[(componentName,dict1[componentName])]
            dict1 = dict(item)
            return dict1
        else:
            print "你输入的IP不是该系统的服务器！"

    # 按组件查找
    else:
        dict1 = {}
        ssh1 = subprocess.Popen("grep %s /wls/bankdplyop/zhoujz/getlog/conf/icss_cccs_csi.conf" % componentName, shell=True,stdout=subprocess.PIPE, stderr = subprocess.PIPE)
        f = ssh1.stdout.read()
        f = f.split(':')[1]
        f = f.split(',')
        for value in f:
            ip = value.split('|')[0]
            logFile = value.split('|')[1]
            dict1[ip] = logFile
        return dict1


# 查找日志
def searchLog(ip, logFile, keyWord, name):
    print 'Children process %s.' % os.getpid()
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    print 'Task %s runs %0.2f seconds.' % (name, (end - start))
#    logFile = dictIpLogfile[ip]
    print ip, logFile
    values1 = (ip, keyWord, logFile)
    ssh2 = subprocess.Popen("export DEPLOY_PASSWORD=deploy;deploytool dremotecmd -s icss_cccs_csi -i %s 'grep -n %s %s '" % values1,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    f = ssh2.stdout.read()
    # 日志名是icss_cccs_csi.log-ip.temp
    templog = logFile + '-' + ip + '.temp'
    os.system("touch %s" % templog)
    templogWrite = open(templog, 'w')
    templogWrite.write(f)
    templogWrite.close()

#清理临时日志，并整合成一个整体日志
def collectLog():
    #找到临时目录下的临时文件，即以temp名为结尾的文件
    ssh3 = subprocess.Popen("ls -l %s" %tempLogDir,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    f = ssh3.stdout.read().split(' ')
    print f
    for x in f:
        n = x.find('temp')
        #判断取出来的文件名中是否包含'temp'
        if n != -1:
            #x为取出来的临时日志文件名
            x = x[0:n+4]
            print x
            #临时日志文件绝对路径
            tempLogFile = tempLogDir + '/' + x
            #将临时日志的文件内容合并到一个日志文件中
            ssh4 = subprocess.Popen("cat %s >> %s" %(tempLogFile,logFile),shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        else:
            pass



if __name__ == '__main__':
    #日志文件名目录
    tempLogDir = '/wls/bankdplyop/zhoujz/getlog/log/temp'
    #整合后的日志文件名
    logFile = '/wls/bankdplyop/zhoujz/getlog/log/icss_cccs_csi.log'
    ssh4 = subprocess.Popen("cat %s" %logFile,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if ssh4.stdout != []:
        ssh5 = subprocess.Popen("rm %s" %logFile,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        pass

    # 配置文件目录
    conf = '/wls/bankdplyop/zhoujz/getlog/conf/icss_cccs_csi.conf'
    # 获取用户输入
    componentName, keyWord = getInputWords()
    # 输出要查找的IP和日志文件目录
    dictIpLogfile = exportConf(componentName)
    n = len(dictIpLogfile)
    print n
    # 利用多进程查找日志
    print 'Parent process %s.' % os.getpid()
    p = Pool(4)
    listIpLogfile = dictIpLogfile.items()
    for i in range(n):
        l = listIpLogfile[i]
        logFile = dictIpLogfile[ip]
        p.apply_async(searchLog, args=(l[0], l[1], i))
    
    print 'Waiting for all subprocesses done...'
    p.close()
    p.join()
    print 'All subprocesses done.'
    #清理临时日志，并整合成一个最终的完整日志
    collectLog()
    print "All logs have been written to the file %s !" %logFile












