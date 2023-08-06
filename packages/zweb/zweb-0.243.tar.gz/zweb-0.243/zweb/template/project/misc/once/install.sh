PREFIX=$(cd "$(dirname "$0")"; pwd)
cd $PREFIX/install
python nginx.py
python supervisor.py 
