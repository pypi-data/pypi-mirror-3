#!/usr/bin/env python
# -*- coding: utf-8 -*-
from _env import PREFIX
from _host_user import host_user_config_iter

import re
from mako.template import Template
from os import mkdir
from os.path import join, dirname, exists, isdir

_CONFIG_DIR = join(PREFIX, 'misc/config/nginx')
with open(join(dirname(__file__),"nginx.conf")) as conf:
    tmpl = conf.read()
T = Template(tmpl)


for host, user, config in host_user_config_iter():
    CONFIG_DIR = join(_CONFIG_DIR, host)
    
    if not exists(CONFIG_DIR):
        mkdir(CONFIG_DIR)
    port_range = range(config.PORT, config.PORT+config.PROCESS_NUM)
    conf = T.render(
        host=config.SITE_DOMAIN,
        name=config.SITE_DOMAIN.replace(".","_"),
        ports=port_range,
        static=join(PREFIX,"html"),
        fs_domain = config.FS_DOMAIN,
        online_host = config.SITE_DOMAIN in config.ONLINE_DOMAIN
    )

    with open(join(CONFIG_DIR, '%s.conf' % config.username),'w') as f:
        f.write(conf)


print('created nginx configure files at %s' % _CONFIG_DIR)

