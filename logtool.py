#!/usr/bin/python
#encoding:utf-8

import sys
import getopt
import paramiko
import re
import os
import string
from datetime import datetime
from datetime import timedelta

#配置LOG等级
LOG_LEVELS = ['DEBUG','INFO','WARN','ERROR','FATAL']


#配置模块信息
#keystone
KEYSTONE_IP = ['10.95.200.179']
KEYSTONE_USER = 'root'
KEYSTONE_PASSWD = 'root'
KEYSTONE_MANAGE = '/var/log/keystone/keystone-manage.log'
KEYSTONE_MAIN = '/var/log/keystone/main.log'
#glance
GLANCE_IP = ['10.95.200.179']
GLANCE_USER = 'root'
GLANCE_PASSWD = 'root'
GLANCE_API = '/var/log/glance/glance-api.log'
GLANCE_REGISTRY = '/var/log/glance/glance-registry.log'
#cinder
CINDER_IP = ['10.95.200.179']
CINDER_USER = 'root'
CINDER_PASSWD = 'root'
CINDER_API = '/var/log/cinder/cinder-api.log'
CINDER_SCHEDULER = '/var/log/cinder/cinder-scheduler.log'
#nova
NOVA_IP = ['10.95.200.179','10.95.20.66']
NOVA_USER = 'root'
NOVA_PASSWD = 'root'
NOVA_API = '/var/log/nova/nova-api.log'
NOVA_CONDUCTOR = '/var/log/nova/nova-conductor.log'
NOVA_MANAGE = '/var/log/nova/nova-manage.log'
NOVA_SCHEDULER = '/var/log/nova/nova-scheduler.log'
#nova-compute
NOVA_COMPUTE_IP = ['10.95.20.66']
NOVA_COMPUTE_USER = 'root'
NOVA_COMPUTE_PASSWD = 'root'
NOVA_COMPUTE = '/var/log/nova/nova-compute.log'

#时间点默认为当前时间
time_point = datetime.now()

#命令开关
m_opt = False
t_opt = False
a_opt = False
start_opt = False
end_opt = False
l_opt = False
server_opt = False

#帮助信息
def usage():  
    print """Options: 
            -m                  module name             "-m nova-api"
            -t                  time point              " '2015-08-14 18:00:00'"
            -a                  time around             "-a 10h"  "-a +10m" "-a -10d"
            -l                  level                   "-level warn" "-leval warn:error"
            --start             start time              "--start '2015-08-14 18:00:00' "
            --end               end time                "--end '2015-08-14 18:00:00' "
            --server            server ip               "--server 10.95.200.179"
            -h, --help          help info               "-h" ""--help" """

#转换时间格式
def parse_datetime(arg):
    try:
        return datetime.strptime(arg,'%Y-%m-%d %H:%M:%S')
    except ValueError,err:
        print 'ERROR:datetime formart error\n'
        usage()
        sys.exit(1)

#获取命令行
try:
    opts,args = getopt.getopt(sys.argv[1:],"m:t:a:l:h",["help","start=","server=","end="])
except getopt.GetoptError,err:
    print str(err)
    usage()
    sys.exit(1)
#处理文件名称
filename = ''
#解析命令行参数    
for o,a in opts:
    if o in ("-h","--help"):
        usage()
        sys.exit()
    if o in ("-m"):
        m_opt = True
        module_name = a.upper().replace('-','_')
        filename = filename + 'm:' + a +'%'
        if a == "nova-compute":
            module = module_name
        else:
            module = module_name.split('_')[0]
    if o in ("-t"):
        t_opt = True
        time_point = parse_datetime(a)
        filename = filename + 't:' + a.replace(' ',',') + '%'
    if o in ("-a"):
        a_opt = True
        time_around = a 
        filename = filename + 'a:' + a + '%'
    if o in ("--server"):
        s_opt = True
        server_ip = a
        filename = filename + 'server:' + a + '%'
    if o in ("--start"):
        start_opt = True
        start_time = parse_datetime(a)
        filename = filename + 'start:' + a.replace(' ',',') + '%'
    if o in ("--end"):
        end_opt = True
        end_time = parse_datetime(a)
        filename = filename + 'end:' + a.replace(' ',',') + '%'
    if o in ("-l"):
        l_opt = True
        levels = a.split(':')
        filename = filename + 'l:' + a + '%'

#检查命令行格式
if not m_opt:
    print "Missing -m option"
    sys.exit()
if t_opt:
    if not a_opt:
        print "-t need -a option"
        sys.exit()
    if start_opt or end_opt:
        print "-t --start --end can't exist at the same time"
        sys.exit()
if a_opt:
    if start_opt or end_opt:
        print "-a --start --end can't exist at the same time"
        sys.exit()
else:
    if not start_opt:
        print "need -t -a --start --end options"
        sys.exit()
if start_opt or end_opt:
    if not (start_opt and end_opt):
        print "missing start or end time"
        sys.exit()

#参数处理
#处理时间参数-t -a --start --end
if a_opt:
    if time_around[0] == '+':
        if time_around[-1] == 'd':
            date = time_point + timedelta(days=int(time_around[1:len(time_around)-1]))
            end_time = date.strftime('%Y-%m-%d %H:%M:%S')
            start_time = time_point.strftime('%Y-%m-%d %H:%M:%S')
        if time_around[-1] == 'h':
            date = time_point + timedelta(hours=int(time_around[1:len(time_around)-1]))
            end_time = date.strftime('%Y-%m-%d %H:%M:%S')
            start_time = time_point.strftime('%Y-%m-%d %H:%M:%S')
        if time_around[-1] == 'm':
            date = time_point + timedelta(minutes=int(time_around[1:len(time_around)-1]))
            end_time = date.strftime('%Y-%m-%d %H:%M:%S')
            start_time = time_point.strftime('%Y-%m-%d %H:%M:%S')
    elif time_around[0] == '-':
        if time_around[-1] == 'd': 
            date = time_point - timedelta(days=int(time_around[1:len(time_around)-1]))
            start_time = date.strftime('%Y-%m-%d %H:%M:%S')
            end_time = time_point.strftime('%Y-%m-%d %H:%M:%S')
        if time_around[-1] == 'h':
            date = time_point - timedelta(hours=int(time_around[1:len(time_around)-1]))
            start_time = date.strftime('%Y-%m-%d %H:%M:%S')
            end_time = time_point.strftime('%Y-%m-%d %H:%M:%S')
        if time_around[-1] == 'm':
            date = time_point - timedelta(minutes=int(time_around[1:len(time_around)-1]))
            start_time = date.strftime('%Y-%m-%d %H:%M:%S')
            end_time = time_point.strftime('%Y-%m-%d %H:%M:%S')
    else:
        if time_around[-1] == 'd': 
            date1 = time_point + timedelta(days=int(time_around[0:len(time_around)-1]))
            date2 = time_point - timedelta(days=int(time_around[0:len(time_around)-1]))
            end_time = date1.strftime('%Y-%m-%d %H:%M:%S')
            start_time = date2.strftime('%Y-%m-%d %H:%M:%S')
        if time_around[-1] == 'h':
            date1 = time_point + timedelta(hours=int(time_around[0:len(time_around)-1]))
            date2 = time_point - timedelta(hours=int(time_around[0:len(time_around)-1]))
            end_time = date1.strftime('%Y-%m-%d %H:%M:%S')
            start_time = date2.strftime('%Y-%m-%d %H:%M:%S')
        if time_around[-1] == 'm':
            date1 = time_point + timedelta(minutes=int(time_around[0:len(time_around)-1]))
            date2 = time_point - timedelta(minutes=int(time_around[0:len(time_around)-1]))
            end_time = date1.strftime('%Y-%m-%d %H:%M:%S')
            start_time = date2.strftime('%Y-%m-%d %H:%M:%S')

#处理 -l 参数
if not l_opt:
    levels = LOG_LEVELS
#处理 -s 参数
if not server_opt:
    server_ip = eval(module + '_IP')

#配置文件路径
filepath = os.getcwd()
filename = filename + 'time:' + datetime.now().strftime('%Y-%m-%d,%H:%M:%S')
log_path = os.path.join(filepath,filename)
os.mknod(log_path)

#配置时间格式
start_time = parse_datetime(start_time)
end_time = parse_datetime(end_time)

#SSH远程连接参数处理
user = eval(module + '_USER')
passwd = eval(module + '_PASSWD')
log_dir = eval(module_name)
command = 'cat ' + log_dir
cmd = 'vim ' + log_path

#SSH远程连接
def ssh_connect(ip, user, passwd, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip,22,user,passwd)
    stdin,stdout,stderr = ssh.exec_command(command)
    log = stdout.readlines()
    ssh.close()
    return log


#匹配log文件
def print_match_logs(log, start_time, end_time, levels, ip):
    f = open(log_path,'a')
    string = "["+ip+"]"+"\n"
    f.write(string)
    for line in log:
        m = re.match('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.\d+\s\d+\s(\w+)', line)
        if m:
            timestr = m.group(1)
            levelstr = m.group(2)
            try:
                cur_time = parse_datetime(timestr)
                if cur_time >= start_time and cur_time <= end_time and levelstr in levels:
                    f.write(line)
            except ValueError:
                pass
    f.write("\n")
    f.close()


#判断是否设定服务IP地址
if server_opt:
    log = ssh_connect(server_ip,user,passwd,command)
    print_match_logs(log, start_time, end_time, levels, server_ip)
    os.system(cmd)
else:
    for ip in server_ip:
        log = ssh_connect(ip,user,passwd,command)
        print_match_logs(log, start_time, end_time, levels, ip)
    os.system(cmd)

    
