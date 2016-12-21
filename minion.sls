#clean yum * #
rm_other_repo:
  cmd.run: 
      - name: rm -rfv /etc/yum.repos.d/*

pel_repo:
  file.managed:
    - name: /etc/yum.repos.d/yovole_yum_ceph.repo
    - source: salt://ceph/system/yum/yovole_yum_ceph.repo
  cmd.run:
    - name: yum clean all && yum makecache 
#install salt-minion
salt-minion:
  pkg.installed:
    - name: salt-minion
    - require:
      - file: /etc/yum.repos.d/yovole_yum_ceph.repo
  file.managed:
    - name: /etc/salt/minion
    - source: salt://files/minion/minion
    - require:
      - pkg: salt-minion
  service.running:
    - name: salt-minion
    - enable: True
    - require:
      - file: /etc/salt/minion

# install vim 
vim:
  pkg:
    - installed
    - name: vim-enhanced
  file.managed:
    - name: /root/.vimrc
    - source: salt://files/system/vimrc
    - user: root
    - mode: 644
    - require:
      - pkg: vim

# disable firewalld
firewalld:
    service:
      - dead
      - disable: True
      - pkg:
        - removed
        - name: firewalld
      #- cmd.run:
      #    - name: yum remove firewalld -y && systemctl disable firewalld
