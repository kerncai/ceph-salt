include:
    - ceph.ceph-deploy.ceph-deploy-pkg

/root/ceph/ceph.conf:
  file.managed:
    - source: salt://ceph/ceph-deploy/mon/ceph.conf
    - user: root
    - group: root
    - mode: 644
    - template: jinja
    - defaults:
        mon_ip: {{ pillar['ceph']['mon_ip'] }}
        mon_host: {{ pillar['ceph']['mon_host'] }}
        public_network: {{ pillar['ceph']['public_network'] }}

ceph-mon:
  service.running:
      - name: ceph-mon@{{ pillar['ceph']['mon_host'] }}
      - enable: True
      - restart: True
      - watch:
          - file: /root/ceph/ceph.conf

/root/ceph/create_or_add_mon.py:
    file.managed:
        - source: salt://ceph/ceph-deploy/mon/create_or_add_mon.py
        - user: root
        - group: root
        - mode: 755
        - template: jinja
        - defaults:
            ceph_deploy: {{ pillar['ceph']['ceph_deploy'] }}
            mon_ip: {{ pillar['ceph']['mon_ip'] }}
            mon_host: {{ pillar['ceph']['mon_host'] }}
            public_network: {{ pillar['ceph']['public_network'] }}
    cmd.run:
        - name: /root/ceph/create_or_add_mon.py
