#!/usr/bin/env python
# coding=utf-8
#        > File Name: create_or_add_osd.py
#        > Author: kerncai
#        > Email: kernkerncai@gmail.com
#        > Created Time: Mon 19 Dec 2016 03:05:33 PM CST
#########################################################
import os
import re
import sys
import commands
import subprocess

class action:

    def __init__(self):
        #参数均通过salt pillar来获取定义数据
        self.ceph_delpoy_server = "{{ceph_delpoy_server}}"
        self.ceph_node = "{{ceph_node}}"
        self.ceph_dir = "{{ceph_dir}}"
        self.df_status_cmd = "df -h |grep -vE 'Filesystem|tmpfs'| awk '{print $1}'"
        self.lsblk_status_cmd = "lsblk -rdn|grep -vE 'rom|K|M'|awk '{print $1}'"
        self.journal_size = "{{osd_journal_size}}"          #如果为0，则直接使用ssd来安装osd
        self.journal_num = "{{osd_journal_num}}"           #如果为0，则通过size大小来判定
        self.hdd_min_size = "{{osd_hdd_min_size}}"
        self.hdd_max_size = "{{osd_hdd_max_size}}"
        self.ssd_min_size = "{{osd_ssd_min_size}}"
        self.ssd_max_size = "{{osd_ssd_max_size}}"
    
    def Check_journal_size(self):
        #获取journal_size的大小，后续会使用
        if self.journal_size == "0":
            return 0
        else:
            return 1

    def CheckDf(self):
        #df -h 检测到的挂载分区
        df_status_cmd = self.df_status_cmd
        p = list(commands.getstatusoutput(df_status_cmd))[1].split()
        return p

    def CheckFdisk(self):
        #lsblk检测到的所有磁盘
        lsblk_status_cmd = self.lsblk_status_cmd
        p = list(commands.getstatusoutput(lsblk_status_cmd))[1].split()
        return p
    
    def DiffDisk(self):
        #比对，去除挂载盘
        osd_disk = []
        df_status_disk = self.CheckDf()
        fdisk_status_disk = self.CheckFdisk()
        for i in fdisk_status_disk:
            s = "/dev/%s" %i
            isTar = 0
            for j in df_status_disk:
                if filter(str.isalpha,s) == filter(str.isalpha,j):
                    isTar = 1
                else:
                    pass
            if isTar == 0 :
                osd_disk.append(s)
        return sorted(osd_disk)

    def CheckDisk(self):
        #检测盘符位是否有断位
        num_range = len(self.DiffDisk())-1
        start_str = list(self.DiffDisk()[0])[-1]
        end_str = list(self.DiffDisk()[-1])[-1]
        str_num = ord(end_str) - ord(start_str)
        if num_range == str_num:
            return 1
        else:
            return 0
    
    def CompletionDisk(self):
        #构造硬盘相关参数，获取硬盘大小用作后续判定
        disk_dict = []
        osd_disk = self.DiffDisk()
        p = subprocess.Popen(["lsblk -rdn|grep -vE 'rom|K|M'|awk '{print $1,1024*$4}'"],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            shell = True)
        out = p.stdout.read()
        regex = re.compile("(\w+) (\d+)", re.IGNORECASE)
        for i in regex.findall(out):
            isTar = 0
            disk_name = '/dev/%s' %list(i)[0]
            disk_size = list(i)[1]
            for disk in osd_disk:
                if disk == disk_name:
                    isTar = 1
            if isTar == 1:
                disk_dict.append({'disk_name':disk_name,'disk_size':disk_size})
        return sorted(disk_dict)

    def CompletionDisk_fdisk(self):
        #第二种以fdisk取值，可能存在异常，暂时停用
        disk_dict = []
        osd_disk = self.DiffDisk()
        p = subprocess.Popen(["fdisk -l"],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            shell = True)
        out = p.stdout.read()
        regex = re.compile("Disk /dev/(\w+): (\d+.\d+)*", re.IGNORECASE)
        for i in regex.findall(out):
            isTar = 0
            disk_name = '/dev/%s' %list(i)[0]
            disk_size = list(i)[1]
            for disk in osd_disk:
                if disk == disk_name:
                    isTar = 1
            if isTar == 1:
                disk_dict.append({'disk_name':disk_name,'disk_size':disk_size})
        return sorted(disk_dict)

    def DefineDiskssd(self):
        #通过size来判定是否为ssd
        disk_dict = self.CompletionDisk()
        ssd_dict = []
        for ssd in disk_dict:
            if self.ssd_min_size < ssd['disk_size'] < self.ssd_max_size:
                ssd_dict.append(ssd)
        return sorted(ssd_dict)

    def DefineDiskhdd(self):
        #通过size来判定是否为ssd
        disk_dict = self.CompletionDisk()
        hdd_dict = []
        for hdd in disk_dict:
            if self.hdd_min_size < hdd['disk_size'] < self.hdd_max_size:
                hdd_dict.append(hdd['disk_name'])
        return sorted(hdd_dict)
              
    def SpliceDisk(self):
        #拼接磁盘，顺序获取ssd以及相应的hdd
        ssd_dict = self.DefineDiskssd()
        hdd_dict = sorted(self.DefineDiskhdd())
        ssdnum = len(ssd_dict)
        ssd_hdd_list = []
        i = -1
        k = 0
        while (i < ssdnum-1):
            i += 1
            ssd_size = ssd_dict[i]['disk_size']
            if self.journal_num != "0":
                num_osd_data = int(self.journal_num)
            else:
                num_osd_data = int(ssd_size)/int(self.journal_size)
            hdd_osd_list = hdd_dict[k:(num_osd_data)+k]
            k += num_osd_data
            ssd_name = ssd_dict[i]['disk_name']
            ssd_hdd_list.append({'ssd':ssd_name,'hdd':hdd_osd_list})
        return ssd_hdd_list
    
    def CreateOsd_ssd(self):
        #直接通过ssd创建osd
        ssd_list = self.DefineDiskssd()
        for ssd in ssd_list:
            ssd_name = ssd['disk_name']
            create_osd_cmd = "ssh -l -n root@%s 'cd %s;ceph-deploy --overwrite-conf osd create --zap-disk --fs-type xfs %s:%s'" %(self.ceph_delpoy_server,self.ceph_dir,self.ceph_node,ssd_name)
            print create_osd_cmd

    def CreateOsd_ssd_hdd(self):
        #ssd结合hdd创建osd
        osd_ssd_hdd_list  = self.SpliceDisk()
        for ssd in osd_ssd_hdd_list:
            for hdd in ssd['hdd']:
                ssd_name = ssd['ssd']
                create_osd_cmd = "ssh -l -n root@%s 'cd %s;ceph-deploy --overwrite-conf osd create --zap-disk --fs-type xfs %s:%s:%s'" %(self.ceph_delpoy_server,self.ceph_dir,self.ceph_node,hdd,ssd_name)
                print create_osd_cmd
                os.system(create_osd_cmd)

    def Osd_status(self):
        #获取osd tree 状态
        osd_status_cmd = "ssh -l -n root@%s 'ceph osd tree' " %self.ceph_delpoy_server
        print osd_status_cmd
        os.system(osd_status_cmd)

if __name__ == '__main__':
    run = action()
    if run.CheckDisk() == 1:
        if run.Check_journal_size() == 0:
            run.CreateOsd_ssd()
        else:
            run.CreateOsd_ssd_hdd()
        run.Osd_status()
    else:
        print 'the disk num is error.exit.'
        sys.exit(1)
    del run

