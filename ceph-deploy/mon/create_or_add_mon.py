#!/usr/bin/env python
# coding=utf-8
#        > File Name: create_or_add_mon.py
#        > Author: kerncai
#        > Email: kernkerncai@gmail.com
#        > Created Time: Mon 19 Dec 2016 09:31:28 AM CST
#########################################################
import os
import time
import commands

class action:
    def __init__(self):
        self.hostname = '{{mon_host}}'
        self.mon_deploy = '{{ceph_deploy}}'
        self.cmd = 'ssh -l -n root@%s "ceph -s" ' %self.mon_deploy
        self.add_mon = 'ceph-deploy mon add %s' %self.hostname
        self.new_mon = 'ceph-deploy mon create-initial'
        self.ceph_dir = '/root/ceph/'

    def CheckCmd(self):
        out = commands.getstatusoutput(self.cmd)
        return list(out)

    def CheckIsEq(self):
        if self.hostname == self.mon_deploy:
            pass
        else:
            print 'not the ceph_deploy host,sleep 10 s'
            time.sleep(10)


    def CheckMon(self):
        add_mon_list = []
        p = self.CheckCmd()
        if p[0] == 0:
            mon = p[1].split('monmap')[1].split('}')[0].split('{')[1].split(',')
            isTar = 0
            for i in mon:
                if self.hostname == i.split('=')[0]:
                    isTar = 1
            if isTar == 1:
                print '%s is already add mon' %self.hostname
            else:
                add_mon_cmd = "ssh -l -n root@%s  'cd %s;%s' " %(self.mon_deploy,self.ceph_dir,self.add_mon)
                add_mon_list.append(add_mon_cmd)
        else:
            print p[1]
            if self.hostname == self.mon_deploy:
                create_new_mon = "ssh -l -n root@%s 'cd %s;%s'" %(self.mon_deploy,self.ceph_dir,self.new_mon)
                os.system(create_new_mon)
            else:
                pass
        if len(add_mon_list) > 0:
            add_mon_cmd = list(set(add_mon_list))[0]
            print add_mon_cmd
            os.system(add_mon_cmd)
        else:
            pass 
if __name__ == '__main__':
    run = action()
    run.CheckIsEq()
    run.CheckMon()
    del run
