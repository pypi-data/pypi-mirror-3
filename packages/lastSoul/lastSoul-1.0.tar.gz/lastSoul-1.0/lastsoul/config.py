import configparser
import os
import logging
import argparse

aparser = argparse.ArgumentParser(description='Python full-scale client for'\
    +'   NetSoul by lastmikoi')
aparser.add_argument('--debug', dest='lvl', action='store_const',\
    const=logging.DEBUG, default=logging.INFO, help='turns on DEBUG level logging')
aparser.add_argument('--logtostderr', dest='to_file', action='store_const',\
    const=False, default=True, help='display logging messages to stderr instead'\
    +'of writing to file')
aparser.add_argument('--ncurses', dest='do_ncurses', action='store_const',\
    const=True, default=False, help='run with ncurses interface')
aparser.add_argument('--pyqt', dest='do_pyqt', action='store_const',\
    const=True, default=False, help='run with PyQt interface')
args = aparser.parse_args()

FORMAT = \
    "[%(levelname)s]%(asctime)s|%(threadName)s:%(message)s|%(filename)s@Line#%(lineno)d"

if args.to_file:
  logging.basicConfig(filename=os.environ['HOME'] + "/.lastsoul.log",level=args.lvl,format=FORMAT)
else:
  logging.basicConfig(level=args.lvl,format=FORMAT)
std_answer = r"rep (\d+) -- ([^\Z]+)"
usercmd_handler = r"user_cmd "\
    +r"(\d+):(\w+):(\d+)/(\d+):(\w+)@([^:]+):([^:]+):([^:]+):(\w+) "

def get_config(section_name, item_name):
  try:
    config = configparser.ConfigParser()
    config.read(os.environ['HOME'] + '/.lastsoul.cfg')
    ret = config.get(section_name, item_name)
  except configparser.Error:
    return (None)
  return (ret)
