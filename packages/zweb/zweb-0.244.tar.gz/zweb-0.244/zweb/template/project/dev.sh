PREFIX=$(cd "$(dirname "$0")"; pwd)
ps x -u $USER|ack /boot/dev.py|ack python|awk  '{print $1}'|xargs kill

cd $PREFIX/misc/boot
supervisorctl shutdown

python $PREFIX/misc/boot/css_js/make.py 
python $PREFIX/misc/boot/dev.py

