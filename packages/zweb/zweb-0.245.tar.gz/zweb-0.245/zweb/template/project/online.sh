PREFIX=$(cd "$(dirname "$0")"; pwd)

python $PREFIX/misc/boot/css_js/make.py 

cd $PREFIX/misc/boot
supervisorctl shutdown
supervisord
