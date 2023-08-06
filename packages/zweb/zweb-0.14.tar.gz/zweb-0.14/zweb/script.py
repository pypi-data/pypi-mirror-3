#coding:utf-8
import clint
from clint.textui import puts, indent
from optparse import OptionParser, make_option
from os.path import abspath, dirname, join, exists
from os import symlink, chmod
from glob import glob
#import shutil
import envoy
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def _create(template, name):
    from zweb import template as _template
    path = join(dirname(abspath(_template.__file__)), template)
    envoy.run('mkdir %s'%name)
    envoy.run("tar zxvf %s.tgz -C %s"%(path, name))
    print 'created sucess , please :'
    print '\tcd %s'%join(abspath('.'), name)

option_list = [

    make_option(
        '-a', '--app', dest='app', type="string", nargs=1,
        help='在项目中创建一个app'
    ),
    make_option(
        '-p', '--project', 
        dest='project',
        type="string", nargs=1,
        help='创建一个项目'
    ),
]
parser = OptionParser(option_list=option_list)


def main():
    (option, args) = parser.parse_args()

    if option.project:
        name = option.project
        _create("project", name)
        for i in glob("%s/*.sh"%name): 
            chmod(i, 0755)

    elif option.app:
        if exists("app"):
            name = option.app
            _create("app", "app/%s"%name)
            for i in ("model", "css", "js", "html", "config"):
                symlink("../app/%s/%s"%(name, i), "%s/%s"%(i,name))
        else:
            print "no exist dir app"
    else:
        parser.print_help()

