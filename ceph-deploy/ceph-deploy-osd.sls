include:
    - ceph.ceph-deploy.ceph-deploy-pkg

/root/ceph/ceph.conf:
  file.managed:
    - source: salt://ceph/ceph-deploy/osd/ceph.conf
    - user: root
    - group: root
    - mode: 644
    - template: jinja
    - defaults:
        mon_ip: {{ pillar['ceph']['mon_ip'] }}
        mon_host: {{ pillar['ceph']['mon_host'] }}
        public_network: {{ pillar['ceph']['public_network'] }}
        osd_journal_size: {{ pillar['ceph']['osd_journal_size'] }}

/root/ceph/create_or_add_osd.py:
    file.managed:
        - source: salt://ceph/ceph-deploy/osd/create_or_add_osd.py
        - user: root
        - group: root
        - mode: 755
        - template: jinja
        - defaults:
            ceph_delpoy_server: {{ pillar['ceph']['ceph_deploy'] }}
            mon_ip: {{ pillar['ceph']['mon_ip'] }}
            ceph_node: {{ pillar['ceph']['ceph_node'] }}
            ceph_dir: {{ pillar['ceph']['ceph_dir'] }}
            osd_journal_num: {{ pillar['ceph']['osd_journal_num'] }}
            osd_journal_size: {{ pillar['ceph']['osd_journal_size'] }}
            osd_hdd_min_size: {{ pillar['ceph']['osd_hdd_min_size'] }}
            osd_hdd_max_size: {{ pillar['ceph']['osd_hdd_max_size'] }}
            osd_ssd_min_size: {{ pillar['ceph']['osd_ssd_min_size'] }}
            osd_ssd_max_size: {{ pillar['ceph']['osd_ssd_max_size'] }}

