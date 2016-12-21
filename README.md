使用saltstack推送ceph配置文件，定义好ceph-deploy节点后，可以自行安装mon和osd
磁盘为顺序安装，基于磁盘size来判定ssd和hdd
除特定的配置文件外，两个核心脚本:create_or_add_mon.py   create_or_add_osd.py
由于pillar信息定义openstack-salt内，所以提前列出
pillar参数信息：
ceph:
    mon_ip: {{ grains['ip_interfaces']['eth0'][0] }}
    mon_host: {{ salt['grains.get']('id', '') }}
    public_network: 10.32.54.0/24
    ceph_deploy: ceph-kerncai-001
    osd_journal_size: 51200
    ceph_node: {{ salt['grains.get']('id','') }}
    ceph_dir: /root/ceph
    osd_journal_num: 0
    osd_hdd_min_size: 29*1024
    osd_hdd_max_size: 55*1024
    osd_ssd_min_size: 190*1024
    osd_ssd_max_size: 220*1024

目录：
/srv/salt/ceph
