##motd
motd:
  file.managed:
     - name: /root/motd.sh
     - source: salt://files/system/motd.sh
     - user: root
     - mode: 755
  cmd.run:
    - name: /root/motd.sh
    - user: root
    - watch:
      - file: /root/motd.sh
###vim
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
###firewalld
firewalld:
  service:
    - dead
    - disable: True
  pkg:
    - removed
    - name: firewalld

#chronyd#
chronyd:
  service.running:
    - name: chronyd
    - enable: True

###ssh_config
ssh_config:
    file.managed:
        - name: /etc/ssh/ssh_config 
        - source: salt://ceph/system/sshd/ssh_config
        - user: root
        - group: root
        - mode: 644

    service.running:
        - name: sshd
        - restart: True
        - watch:
            - file: /etc/ssh/ssh_config
        
#add ssh key
ssh-key-pri:
    cmd.run:
        - name: mkdir /root/.ssh/ 
        - unless: test -d /root/.ssh/ 
    file.managed:
        - name: /root/.ssh/id_rsa 
        - source: salt://ceph/system/key/id_rsa
        - mode: 600
        - user: root
        - group: root

ssh-key-pub:
    file.managed:
        - name: /root/.ssh/id_rsa.pub
        - source: salt://ceph/system/key/id_rsa.pub
        - mode: 644
        - user: root
        - group: root

ssh-key-authorized_keys:
    file.managed:
        - name: /root/.ssh/authorized_keys
        - source: salt://ceph/system/key/id_rsa.pub
        - user: root
        - group: root
        - mode: 400

#chronyd#
chronyds:
    service.running:
        - name: chronyd
        - enable: True
