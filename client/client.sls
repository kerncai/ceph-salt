#add ssh key

ssh-key-authorized_keys:
    file.managed:
        - name: /root/.ssh/authorized_keys
        - source: salt://ceph/system/key/id_rsa.pub
        - user: root
        - group: root
        - mode: 400

client-ceph:
    pkg.installed:
        - name: ceph

ceph-common:
    pkg.installed:
        - name: ceph-common
