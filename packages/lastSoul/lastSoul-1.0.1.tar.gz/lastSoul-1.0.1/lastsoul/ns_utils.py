import urllib.request, urllib.parse, urllib.error
import time
import socket
import queue
import re
import config
from threading import Condition
from config import std_answer, usercmd_handler
import logging

log = logging.getLogger('')

def change_status(thread, newstatus):
  newstatus = urllib.parse.quote(newstatus)
  thread.add_queueout("state %s" % newstatus)

def send_msg(thread, username, msg):
  username = username.split(' ')[0]
  msg = urllib.parse.quote(msg)
  thread.add_queueout("user_cmd msg_user %s msg %s" % (username, msg))

def watch_user(thread, usernames, callback):
  usercmd_userscoped_handler = r"user_cmd "\
      +r"(\d+):(\w+):(\d+)/(\d+):(%s)@([^:]+):([^:]+):([^:]+):(\w+) " % '|'.join(usernames)
  watchhandler = usercmd_userscoped_handler + r"\| (login|logout|state)([^\Z]+)\Z"
  thread.register_handler(watchhandler, callback)
  thread.add_queueout("user_cmd watch_log_user {%s}" % ','.join(usernames))

def get_status(thread, usernames):
  finished = Condition()
  userinfo = []

  def finished_recv(thread, m):
    thread.forget_handler(finished_recv)
    thread.forget_handler(internal_recv)
    finished.acquire()
    finished.notify()
    finished.release()
    pass

  def internal_recv(thread, m):
    userinfo.append(dict(socknum=m.group(1), username=m.group(2), ip=m.group(3),
      login_time=int(m.group(4)), update_time=int(m.group(5)),
      low_t=int(m.group(6)), hi_t=int(m.group(7)), wtype=m.group(8),
      location=m.group(9), group=m.group(10), status=m.group(11),
      userdata=m.group(12)))
    pass

  handler = r"(\d+) (\w+) ([^ ]+) (\d+) (\d+) (\d+) (\d+) ([^ ]+) ([^ ]+) (\w+) ([^ ]+) ([^ ]+)"
  thread.register_handler(handler, internal_recv)
  thread.register_handler(std_answer, finished_recv)
  thread.add_queueout("list_users {%s}" % ','.join(usernames))
  finished.acquire()
  finished.wait()
  finished.release()
  return (userinfo)
