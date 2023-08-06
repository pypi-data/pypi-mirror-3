PREFIX=$(cd "$(dirname "$0")"; pwd)
ps x -u $USER|ack /boot/online.py|ack python|awk  '{print $1}'|xargs kill
ps x -u $USER|ack /boot/dev.py|ack python|awk  '{print $1}'|xargs kill
python $PREFIX/boot/dev.py
