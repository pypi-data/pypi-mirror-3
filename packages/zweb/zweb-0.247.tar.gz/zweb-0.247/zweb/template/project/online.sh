PREFIX=$(cd "$(dirname "$0")"; pwd)

python $PREFIX/misc/boot/css_js/make.py 

PROGRAM=$PREFIX/misc/boot/dev.py
ps x -u $USER|ack $PROGRAM|awk  '{print $1}'|xargs kill

sudo supervisorctl restart ${PWD##*/}_$USER:*

