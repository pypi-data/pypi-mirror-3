#! /bin/env python3
#

from handlers import init_handlers
from processThread import processThread
from socketThread import socketThread
import ns_utils
import time
import logging
import config
import ncurses
import pyqt

log = logging.getLogger('')

pthread = processThread(1, "processThread")
sthread = socketThread(2, "socketThread", pthread.recv)
init_handlers(pthread)
pthread.socketThread = sthread
sthread.processThread = pthread
sthread.start()
while not sthread.running:
  time.sleep(0.1)
pthread.start()
while not pthread.authed:
  time.sleep(0.1)
ns_utils.change_status(pthread, "actif")
time.sleep(1)

try:
  if config.args.do_ncurses:
    ncurses.main(pthread)
  elif config.args.do_pyqt:
    pyqt.main(pthread)
  else:
    while (True):
      time.sleep(1)
      cmd = input("Cmd>")
      pthread.add_queueout(cmd)
except (KeyboardInterrupt, SystemExit):
  log.info("Exiting")
except:
  log.critical("Exception caught")
  raise
finally:
  pthread.add_queueout("exit")
  while not pthread.q_out.empty():
    time.sleep(1)
  pthread.stop()
  sthread.stop()
  pthread.join()
  sthread.join()
