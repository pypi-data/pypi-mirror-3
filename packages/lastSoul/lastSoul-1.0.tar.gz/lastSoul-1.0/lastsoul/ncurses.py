#! /bin/env python
#

from config import usercmd_handler
from _version import __version__
import config
import curses
import urllib.request, urllib.parse, urllib.error
import time
import sys
import select
import logging
import ns_utils

log = logging.getLogger('')

def main(thread):
  msgs = []
  dest = []
  usermsg = []
  friends = []
  field = 0

  def refresh():
    stdscr.refresh()
    statuswin.refresh()
    txtwin.refresh()
    dstwin.clear()
    dstwin.addstr(0, 0, ''.join(dest))
    dstwin.refresh()
    msgwin.erase()
    msgwin.addstr(0, 0, ''.join(usermsg))
    msgwin.refresh()
    friendswin.clear()
    friendswin.border(curses.ACS_VLINE, curses.ACS_VLINE,
        curses.ACS_HLINE, curses.ACS_HLINE,
        curses.ACS_TTEE, curses.ACS_RTEE,
        curses.ACS_BTEE, curses.ACS_RTEE)
    for i, friend in enumerate(friends):
      friendswin.addstr(1 + i, 1, friend['username'] + ':' + friend['status'])
    friendswin.refresh()

  def sendmsg(thread):
    ns_utils.send_msg(thread, ''.join(dest), ''.join(usermsg))
    refresh()

  def recv_watch(thread, m):
    groups = m.groups()
    newstatus = None
    if groups[9] == 'state':
      newstatus = groups[10].split(':')[0]
    elif groups[9] == 'logout':
      newstatus = "logout"
    else:
      newstatus = "connecting"
    friendinfo = dict(socknum=int(groups[0]), usertype=groups[1],\
        low_t=int(groups[2]), hi_t=int(groups[3]), username=groups[4],\
        ip=groups[5], wtype=groups[6], location=groups[7], usergroup=groups[8],\
        status=newstatus)
    for i, friend in enumerate(friends):
      if friend['username'] == friendinfo['username']:
        log.debug("Updating status of %s" % friendinfo['username'])
        if newstatus == "logout":
          friends.pop(i)
        else:
          friends[i] = friendinfo
        refresh()
        return
    log.debug("New status for %s" % friendinfo['username'])
    if newstatus != "logout":
      friends.append(friendinfo)
    refresh()

  def recv_private_msg(thread, m):
    msgdata = dict(socknum=int(m.group(1)), usertype=m.group(2), low_t=int(m.group(3)),\
        hi_t=int(m.group(4)), username=m.group(5), ip=m.group(6),\
        workstation=m.group(7), location=m.group(8),\
        group=m.group(9), msg=m.group(10))
    msgs.append(msgdata)
    while len(msgs) >= txtwin.getmaxyx()[0] - 1:
      msgs.pop(0)
    for i, msg in enumerate(msgs):
      txtwin.addstr(1 + i, 1, "(%s):%s" % (msg['username'], urllib.parse.unquote(msg['msg'])))
    refresh()

  privmsg_handler = usercmd_handler + r"\| msg (\S+) dst=(\S+)"
  thread.register_handler(privmsg_handler, recv_private_msg)
  try:
    stdscr = curses.initscr()
    curses.noecho(); stdscr.keypad(1); curses.cbreak()
    curses.curs_set(0)
    stdscr.border()
    size = stdscr.getmaxyx()
    statuswin = curses.newwin(1, size[1] - 2, 1, 1)
    statuswin.addstr(0, 0, "lastSoul v%s" % __version__, curses.A_BOLD)
    txtwin = curses.newwin(size[0] - 4, 0, 2, 0)
    txtwin.border(curses.ACS_VLINE, curses.ACS_VLINE,\
        curses.ACS_HLINE, curses.ACS_HLINE,\
        curses.ACS_LTEE, curses.ACS_RTEE,\
        curses.ACS_LTEE, curses.ACS_RTEE)
    msgwin = curses.newwin(1, int(size[1] / 4 * 3 - 1), size[0] - 2, int(size[1] / 4))
    dstwin = curses.newwin(1, int(size[1] / 4 - 2), size[0] - 2, 1)
    friendswin = curses.newwin(txtwin.getmaxyx()[0], 0,\
        2, int(size[1] / 4 * 3 + 2))
    oldtimestamp = 0
    while (True):
      timestamp = time.time()
      refresh()
      try:
        fd = select.select([sys.stdin], [], [], 0.5)[0]
      except select.error:
        fd = None
      if fd:
        c = fd[0].read(1)
        if ord(c) == 0x7F:
          if field and len(dest):
            dest.pop()
          else:
            if len(usermsg):
              usermsg.pop()
        elif ord(c) == 0x9:
          field = not field
        elif ord(c) == 0xD:
          sendmsg(thread)
          usermsg = []
        else:
          if field:
            dest.append(c)
          else:
            usermsg.append(c)
      if (oldtimestamp < timestamp - 60):
        statusresp = ns_utils.get_status(thread,
            (config.get_config("Auth", "login"),))
        for userinfo in statusresp:
          statussize = statuswin.getmaxyx()
          statuswin.addstr(0, statussize[1] - 1 - len(userinfo['status']),
              userinfo['status'])
        oldtimestamp = timestamp
  except Exception as e:
    log.critical("Exception caught : %s" % e)
    raise e
  finally:
    curses.nocbreak(); stdscr.keypad(0); curses.echo()
    curses.endwin()

