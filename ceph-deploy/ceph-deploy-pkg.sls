ceph:
    pkg.installed:
        - name: ceph

ceph-deploy:
    pkg.installed:
        - name: ceph-deploy


ceph-dir:
    cmd.run: 
        - name: mkdir /root/ceph
        - unless: test -d /root/ceph
