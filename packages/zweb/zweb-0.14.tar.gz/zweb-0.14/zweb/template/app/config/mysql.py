#coding:utf-8
import _env
from os.path import dirname, basename,abspath

MYSQL_DB = basename(dirname(dirname(abspath(__file__))))

MYSQL_TABLE = (
    #"table_name",
)

MYSQL_CONFIG = {
    MYSQL_DB : MYSQL_TABLE
}

