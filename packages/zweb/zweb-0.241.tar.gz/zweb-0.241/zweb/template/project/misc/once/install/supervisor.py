# coding:utf-8

import _env
from _host_user import host_user_config_iter 
from os import mkdir
from os.path import abspath, dirname, join, exists

_CONFIG_DIR = join(_env.PREFIX, 'misc/boot','supervisor')

for host, user, o in host_user_config_iter():
    CONFIG_DIR = join(_CONFIG_DIR, o.hostname)

    if not exists(CONFIG_DIR):
        mkdir(CONFIG_DIR)

    # supervisor

    port = str(o.PORT)
    procsnum = o.PROCESS_NUM

    conf = '''; supervisor.

    [supervisord]

    [inet_http_server]
    port = 9011

    [supervisorctl]
    serverurl=http://localhost:9011

    [rpcinterface:supervisor]
    supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

    [group:zweb-app]
    programs=zweb

    [program:zweb]
    command=python online.py -port=%s%%(process_num)02d
    process_name=%%(program_name)s_%%(process_num)02d
    directory=.
    autorestart=true
    redirect_stderr=true
    stdout_logfile=/var/log/zweb/%s/base-%%(process_num)02d.log
    stdout_logfile_maxbytes=500MB
    stdout_logfile_backups=50
    stdout_capture_maxbytes=1MB
    stdout_events_enabled=false
    loglevel=warn
    numprocs_start=%s
    numprocs=%d

    ''' % (o.SITE_DOMAIN, port[:-2], port[-2:], procsnum)

    f = open(join(CONFIG_DIR, '%s.conf' % o.username), 'w')
    f.write(conf)
    f.close()

print('created supervisor configure file at %s' % _CONFIG_DIR)


