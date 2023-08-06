
# coding:utf-8

'''

这个模块被用于动态组合静态文件。

示例代码：

a = '<link href="http://s.z32e1.tk/css/reset.css" rel="stylesheet" type="text/css">'
b = '<link href="http://s.z32e1.tk/css/_build/ba1d59b0e53d380b12b3e97a428b3314" rel="stylesheet" type="text/css">'
c = '<script src="http://s.z32e1.tk/js/_build/cca76f660e01ba7b96023a18764c30e1"></script>'

# 合并 css
print _load('a,c,b',genstr_css,swapfile_css,p_css)

# 合并 js
print _load('a,c,b,a',genstr_js,swapfile_js,p_js)
或
print _load('a,c,b')

合并后会在css/_build 或 js/_build 目录下生成一个hash文件，
并在 /tmp/ 下生成一个名为 _static_xx 的交换文件。

首次生成之后若遇到相同的生成组合，
会直接从交换文件里读取路径。

'''

import _env
from misc import config
import fcntl
import os
import re

swapfile_js = '/tmp/_static_js.swp'
swapfile_css = '/tmp/_static_css.swp'

genstr_js  = """<script src="%s%s"></script>'\n"""
genstr_css = """<link href="%s%s" rel="stylesheet" type="text/css">\n"""

p_js  = '/js/_build/'
p_css = '/css/_build/'

_getutime = lambda fn : os.stat(fn)[8]
__extract__ = lambda s : _env.PREFIX + re.search('(?:href=|src=)"(.*?)"',s.replace(config.FS_URL,'')).group(1)

def update_namespace(ns):
    globals().update(ns)
    
def _getfile_(fn):
    f = open(fn,'r')
    ret = ''.join(f.xreadlines())
    f.close()
    return ret

def _merge(rule_fn,_dir):
    f = open(rule_fn,'r')
    raw = ''.join(map(lambda s : re.sub('#.*','',s) ,f.readlines()))
    f.close()
    rules = {}
    _split = lambda s : {s[0] : re.split('\s+',s[1],re.DOTALL)}
    map(rules.update, map(_split,re.findall('\s*(.*?)\s*:\s*(.*?)\s*;',raw,re.DOTALL)))
    for i in rules:
        fn = _env.PREFIX + _dir + i
        #if os.path.exists(fn):
        #    print('merge: error file %s exist.' % fn)
        #    continue
        css_lst = map(lambda x : _env.PREFIX + _dir + x ,rules[i])
        if not os.path.exists(fn) or _getutime(fn) < max(map(_getutime,css_lst)):
            files = map(_getfile_,css_lst)
            f = open(fn,'w')
            f.write(''.join(files))
            f.close()

def _load(s,genstr=genstr_js,swapfile=swapfile_js,p_st=p_js):
    # 读取请求的css列表
    lst = list(set(map(str.strip ,s.split(','))))
    css_lst = map(__extract__,map(eval,lst))
    itemname = '_'.join(lst)

    # 若只请求一个css，直接返回链接
    if len(lst)==1:
        return eval(lst[0])

    # 在列表中查询是否已经压缩过
    if os.path.exists(swapfile):
        f = open(swapfile,'r')
        for i in f.xreadlines():
            l = i.split('::')
            if l[0] == itemname:
                return l[1]
        f.close()

    # 计算文件哈希值
    import hashlib
    h = hashlib.md5('')
    map(h.update,css_lst)
    md5 = h.hexdigest()

    fn = _env.PREFIX + p_st + md5
    if os.path.exists(fn):
        pass
    else:
        f = open(fn,'w')
        fcntl.flock(f,fcntl.LOCK_EX)
        files = map(_getfile_,css_lst)
        f.write(''.join(files))
        fcntl.flock(f,fcntl.LOCK_UN)
        f.close()

        f = open(swapfile,'a')
        fcntl.flock(f,fcntl.LOCK_EX)
        f.write(itemname+'::'+ genstr % (config.FS_URL, p_st+md5))
        fcntl.flock(f,fcntl.LOCK_UN)
        f.close()

    return genstr % (config.FS_URL, p_st+md5)

