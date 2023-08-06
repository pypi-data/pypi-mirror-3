import re
import hashlib
import urllib.request, urllib.parse, urllib.error
from config import get_config, std_answer, usercmd_handler
import logging

log = logging.getLogger('')

def recv_private_msg(thread, m):
  msgdata = dict(socknum=int(m.group(1)), usertype=m.group(2), low_t=int(m.group(3)),\
      hi_t=int(m.group(4)), username=m.group(5), ip=m.group(6),\
      workstation=m.group(7), location=m.group(8),\
      group=m.group(9), msg=m.group(10))
  log.info("Message recieved from "+ msgdata['username'] + "@" +\
    msgdata['location'] + ":" + msgdata['msg'])

def recv_dotnetSoul(thread, m):
  msgdata = dict(socknum=int(m.group(1)), usertype=m.group(2), low_t=int(m.group(3)),\
      hi_t=int(m.group(4)), username=m.group(5), ip=m.group(6),\
      workstation=m.group(7), location=m.group(8),\
      group=m.group(9), action=m.group(10), unused1=m.group(11))
  log.info("User " + msgdata['username'] + " " + msgdata['action'])

def recv_ping(thread, m):
  answer = int(m.group(1))
  log.info("Sending back ping %d" % answer)
  thread.add_queueout("ping %d " % answer)

def recv_auth(thread, m):
  auth = None

  def calc_auth(auth):
    username = get_config("Auth", "login")
    passwd = get_config("Auth", "passwd")
    tohash = "%s-%s/%s%s" % (auth['md5'], auth['myip'], auth['myport'], passwd)
    repmd5 = hashlib.md5(tohash.encode('ascii')).hexdigest()
    udata = urllib.parse.quote(get_config("Misc", "userdata"))
    userlocation = urllib.parse.quote(get_config("Misc", "location"))
    return (dict(username=username, md5=repmd5, userdata=udata, location=userlocation))

  def stage_two(thread, m):
    if m.group(1) != '002':
      raise ValueError(m.group(2))
    thread.forget_handler(stage_two)
    answ = calc_auth(auth)
    msg = "ext_user_log %s %s %s %s"\
      % (answ['username'], answ['md5'], answ['location'], answ['userdata'])
    thread.register_handler(std_answer, stage_three)
    thread.add_queueout(msg)
    pass

  def stage_three(thread, m):
    if m.group(1) != '002':
      raise ValueError(m.group(2))
    thread.forget_handler(stage_three)
    log.info("Authed sucessfully")
    thread.add_queueout("state connection")
    thread.authed = True
    pass

  auth = dict(socknum=int(m.group(1)), md5=m.group(2), myip=m.group(3),
    myport=int(m.group(4)), timestmp=int(m.group(5)))
  thread.register_handler(std_answer, stage_two)
  thread.add_queueout("auth_ag ext_user none none")
  pass


def init_handlers(thread):
  auth_handler = r"salut (\d+) (\w+) (\S+) (\d+) (\d+)"
  ping_handler = r"ping (\d+)"
  privmsg_handler = usercmd_handler + r"\| msg (\S+) dst=(\S+)"
  dotnetSoul_handler = usercmd_handler + r"\| dotnetSoul_(\S+) (\S+) dst=(\S+)"

  thread.register_handler(auth_handler, recv_auth)
  thread.register_handler(privmsg_handler, recv_private_msg)
  thread.register_handler(ping_handler, recv_ping)
  thread.register_handler(dotnetSoul_handler, recv_dotnetSoul)
