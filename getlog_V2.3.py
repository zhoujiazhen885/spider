#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

2017-8-21 V2.1 该程序用来收集服务器上的日志信息，用以替代人工去服务器查询关键字的工作。
               该版比第一版新增多进程功能。周佳振，上海浦东张江职场。
2017-8-23 V2.2 Adding the feather of every system can use this python program
               Jiazhen Zhou , Danyang Jiangsu.
               MAC的程序汉字要正常显示到LINUX上，需要先通过UE转换成Unicode格式。

"""
import os
import subprocess
import sys
from multiprocessing import Pool


# 获取用户输入
def getInputWords():
    componentName = raw_input("请输入要查找的组件名(如APP/WEB，与配置文件名称一致)或者要查找的服务器IP地址，如果要查询全部请输入ALL:").upper()
    keyWord = raw_input("请输入要查找的日志关键字:")
    systemName = raw_input("Please input the system's name ,which should be the same as the conf name :").lower()
    return componentName, keyWord, systemName


# 根据用户输入，读取配置文件，输出IP和日志文件路径
def exportConf(componentName, systemName):
    # checking if the system's config has been existed!
    systemName = systemName.replace('-','_') + '.conf'
    confName = '/wls/bankdplyop/zhoujz/getlog/conf/'+systemName
    checkConfFile = subprocess.Popen("cat %s" % confName,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #判断配置文件是否存在
    f = checkConfFile.stdout.read()
    if f :
        print f
        pass
    else:
        print "The conf file is not existed, please check!"
        sys.exit(0)
    # componentName
    # 查找所有服务器
    if componentName == 'ALL':
        # 将ip和logFile匹配成字段
        dict1 = {}
        lines = open(confName)
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
        # 将ip和logFile匹配成字段
        dict1 = {}
        lines = open(confName)
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
            item = [(componentName, dict1[componentName])]
            dict1 = dict(item)
            return dict1
        else:
            print "你输入的IP不是该系统的服务器"

    # 按组件查找
    else:
        dict1 = {}
        ssh1 = subprocess.Popen("grep %s /wls/bankdplyop/zhoujz/getlog/conf/icss_cccs_csi.conf" % componentName,
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        f = ssh1.stdout.read()
        f = f.split(':')[1]
        f = f.split(',')
        for value in f:
            ip = value.split('|')[0]
            logFile = value.split('|')[1]
            dict1[ip] = logFile
        return dict1


# 查找日志
def searchLog(ip, searchLogFile, keyWord, name):
    print 'Children process %s.' % os.getpid()
    #    start = time.time()
    #    print "The starting time is %0.2f " % start
    #    time.sleep(1)
    #    end = time.time()
    #    print 'Task %s runs %0.2f seconds.' % (name, (end - start))
    #    logFile = dictIpLogfile[ip]
    print "The child process is serach the host %s and the file %s " % (ip, searchLogFile)
    values1 = (ip, keyWord, searchLogFile)
    ssh2 = subprocess.Popen(
        "export DEPLOY_PASSWORD=deploy;deploytool dremotecmd -s icss_cccs_csi -i %s 'grep -n %s %s '" % values1,
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    f = ssh2.stdout.read()
    fError = ssh2.stderr.read()
    #    print "the f: %s" %f
    #    print "the fError: %s" %fError
    # 日志名是systemName-ip.temp
    templog = tempLogDir + systemName + '-' + ip + '.temp'
    print templog
    ssh3 = subprocess.Popen("touch %s" % templog, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    templogWrite = open(templog, 'w')
    templogWrite.write(f)
    templogWrite.close()


# 清理临时日志，并整合成一个整体日志
def collectLog():
    # 整合后的日志文件名
    logFile = '/wls/bankdplyop/zhoujz/getlog/log/' + systemName + '.log'
    ssh1 = subprocess.Popen("cat %s" % logFile, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if ssh1.stdout:
        ssh2 = subprocess.Popen("rm %s" % logFile, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        pass
    # 找到临时目录的临时文件，即以temp结尾的文件
    ssh3 = subprocess.Popen("ls -l %s" % tempLogDir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    f = ssh3.stdout.read().split(' ')
    print f
    for x in f:
        n = x.find('temp')
        # 判断取出来的文件名中是否包含"temp"
        if n != -1:
            # x为取出来的临时日志文件名
            x = x[0:n + 4]
            print "The collectLog has search the templog is : %s" % x
            # 临时日志文件绝对路径
            tempLogFile = tempLogDir + x
            # 将临时日志的文件内容整合到一个日志文件中
            ssh4 = subprocess.Popen("cat %s >> %s" % (tempLogFile, logFile), shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            ssh5 = subprocess.Popen("rm %s" % tempLogFile, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            pass
    print "All logs have been written to the file %s !" % logFile

if __name__ == '__main__':
    # 日志文件名目录
    tempLogDir = '/wls/bankdplyop/zhoujz/getlog/log/temp/'
    # 获取用户输入
    componentName, keyWord, systemName = getInputWords()
    print componentName, keyWord, systemName


        # 配置文件目录
#    conf = '/wls/bankdplyop/zhoujz/getlog/conf/icss_cccs_csi.conf'


    # 输出要查找的IP和日志文件目录
    dictIpLogfile = exportConf(componentName, systemName)
    print dictIpLogfile

    n = len(dictIpLogfile)
    print 'Total number is %s' % n
    # 利用多进程查找日志
    print 'Parent process %s.' % os.getpid()
    p = Pool(10)
    listIpLogfile = dictIpLogfile.items()
    for i in range(n):
        print i
        l = listIpLogfile[i]
        print l[0], l[1]
        p.apply_async(searchLog, args=(l[0], l[1], keyWord, i))

    print 'Waiting for all subprocesses done...'
    p.close()
    p.join()
    print 'All subprocesses done.'
    # 清理临时日志，并整合成一个完整的日志
    collectLog()













