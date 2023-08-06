
# coding:utf-8

import _env
from misc import config
import time
import re
import os
import hashlib
import subprocess
from merge import _merge

from os import mkdir
from shutil import copyfile
from os.path import isdir,islink,abspath,exists,dirname,join

import zweb

cmd_css = "['java', '-jar', join(dirname(abspath(zweb.__file__)),'utils','yuicompressor.jar'), '--charset=utf-8', '--type', 'css', fn, '-o', outfile]"
cmd_js = "['uglifyjs', '-o',outfile ,fn]"

getmd5 = lambda fn : hashlib.md5(fn).hexdigest()
getutime = lambda fn : os.stat(fn)[8]

def update(fn,t):
    os.utime(fn,(t,t))

def clear_old(path,utime):
    ''' 清理过期文件 '''
    for i in os.listdir(path):
        fn = join(path,i)
        if getutime(fn) < utime:
            os.remove(fn)
        
def minify(fn,out,cmd):
    ''' 压缩 css '''
    h = getmd5(fn)
    outfile = out + h
    if not exists(outfile) or getutime(outfile) < getutime(fn):
        try:
            returncode = subprocess.call(eval(cmd))
            if returncode:
                raise
        except Exception:
            print('compressor error : %s '%(fn))
            copyfile(fn, outfile)
        print fn
    else:
        update(outfile,time.time())

    return h

def do(path,cmd,out_dir,is_minify=True,prefix=''):
    """ 遍历 css/js 目录，生成压缩文件并返回生成列表 """
    for i in os.listdir(path):
        if i == '_build': continue
        fn = join(path, i)
        if isdir(fn) and not islink(fn):
            ret = do(fn,cmd,out_dir,is_minify,i + '_')
            for r in ret:
                yield r
        else:
            if fn.rsplit('.')[-1] in ['js','css']:
                if is_minify:
                    # 返回压缩后路径
                    yield [prefix + re.sub(r'\.css$|\.js$','',i), minify(fn,out_dir,cmd)]
                else:
                    # 此时返回原始路径
                    yield [prefix + re.sub(r'\.css$|\.js$','',i), re.sub(_env.PREFIX+'(/js|/css)/','', fn)]

def write_header(f):
    f.write('import _env\n')
    f.write('import misc.boot.css_js.merge\n')
    f.write('from misc.boot.css_js.merge import *\n')
    f.write('from misc.config import DEBUG\n')
    f.write('\n')

def write_footer(f):
    f.write('\n')
    f.write('update_namespace(globals())\n')
    f.write('load = lambda s : misc.boot.css_js.merge._load(s)\n')
    f.write('\n')

def make(prefix,_dir, appname, cmd, tmplstr, conf_name="merge.conf"):
    o_build = prefix + '/_build/'

    if not exists(o_build):
        mkdir(o_build)

    # 合并 css/js 文件
    _path = join(prefix,appname,'merge.conf')
    if exists(_path):
        _merge(_path,re.sub('//$','/',_dir+appname+'/'))

    # 生成 css/js 配置
    ret_debug = []

    for i in do(join(prefix,appname), cmd, o_build, False, appname):
        _tmpl = "    %s = '"+tmplstr+"'\n"
        ret_debug.append(_tmpl % (i[0],config.FS_URL, _dir+appname+i[1]))

    ret_online = []

    for i in do(join(prefix,appname),cmd, o_build, True, appname):
        _tmpl = "    %s = '"+tmplstr+"'\n"
        ret_online.append(_tmpl % (i[0],config.FS_URL, _dir+'/_build/' + i[1]))

    return ret_debug,ret_online

def main():

    utime = int(time.time())
    _prefix_js  = join(_env.PREFIX,'js/')
    _prefix_css = join(_env.PREFIX,'css/')

    # make css
    lst = ['']
    for i in os.listdir(_prefix_css):
        if isdir(_prefix_css+i) and islink(_prefix_css+i):
            lst.append(i)

    ret = map(lambda x : make(_prefix_css, '/css/', x, cmd_css, '<link href="%s%s" rel="stylesheet" type="text/css">'), lst)

    f = open(_prefix_css+'_hash_.py','w')
    write_header(f)

    f.write('if DEBUG:\n')
    map(lambda i : f.write(''.join(i[0])), ret)

    f.write('else:\n')
    map(lambda i : f.write(''.join(i[1])), ret)

    write_footer(f)
    f.close()

    print('Configure CSS done.')

    # make js
    lst = ['']
    for i in os.listdir(_prefix_js):
        if isdir(_prefix_css+i):
            lst.append(i)

    ret = map(lambda x : make(_prefix_js, '/js/', x, cmd_js, '<script src="%s%s"></script>'), lst)

    f = open(_prefix_js+'_hash_.py','w')
    write_header(f)

    f.write('if DEBUG:\n')
    map(lambda i : f.write(''.join(i[0])), ret)

    f.write('else:\n')
    map(lambda i : f.write(''.join(i[1])), ret)

    write_footer(f)
    f.close()

    print('Configure JS done.')

    # 清理旧文件
    clear_old(_prefix_css + '/_build/', utime)
    clear_old(_prefix_js  + '/_build/', utime)

    print('Old files removed.')

if __name__ == '__main__':
    main()

