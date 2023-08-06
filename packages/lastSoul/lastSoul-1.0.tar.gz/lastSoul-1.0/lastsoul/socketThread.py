import threading
import queue
from config import get_config
import socket
import time
import logging

log = logging.getLogger('')

class outThread(threading.Thread):
  def __init__(self, socket, socketLock):
    super(outThread, self).__init__()
    log.debug("Creating")
    self.name = "socketThread:outThread"
    self.running = True
    self.s = socket
    self.s_lock = socketLock
    self.q_out = queue.Queue()
    self.q_outLock = threading.Lock()
    self.waitLock = threading.Condition()
    pass

  def wakeup(self):
    self.waitLock.acquire()
    self.waitLock.notify()
    self.waitLock.release()

  def run(self):
    log.debug("Starting")
    while self.running:
      self.q_outLock.acquire()
      if not self.q_out.empty():
        data = bytes(self.q_out.get(), 'ascii')
        log.info("Sending [%s\\n]" % data[:-1])
        self.q_outLock.release()
        self.s_lock.acquire()
        self.s.sendall(data)
        self.s_lock.release()
      else:
        self.q_outLock.release()

      self.waitLock.acquire()
      self.waitLock.wait()
      self.waitLock.release()
    log.debug("Exiting")
    pass

class inThread(threading.Thread):
  def __init__(self, socket, socketLock, recv_handler):
    super(inThread, self).__init__()
    log.debug("Creating")
    self.name = "socketThread:inThread"
    self.running = True
    self.s = socket
    self.s_lock = socketLock
    self.recv_handler = recv_handler
    pass

  def run(self):
    log.debug("Starting")
    while self.running:
      self.s_lock.acquire()
      self.s.setblocking(False)
      data = None
      try:
        data = str(self.s.recv(1024), 'ascii')
        self.s.setblocking(True)
        self.s_lock.release()
      except socket.error:
        self.s.setblocking(True)
        self.s_lock.release()
        time.sleep(0.1)
      if data:
        for line in data.split('\n'):
          if line:
            log.info("Recieved [%s\\n]" % line)
            self.recv_handler(line)
    log.debug("Exiting")
    pass

class socketThread(threading.Thread):
  def __init__(self, threadID, name, recv_handler):
    super(socketThread, self).__init__()
    log.debug("Creating")
    self.daemon = True
    self.running = False
    self.processThread = None
    self.threadID = threadID
    self.name = name
    self.s = self.init_socket()
    self.s_lock = threading.Lock()
    self.recv_handler = recv_handler
    self.q_out = queue.Queue()
    pass

  def init_socket(self):
    s = None
    HOST = get_config("Connection", "server")
    PORT = int(get_config("Connection", "port"))
    log.info("Connecting to %s:%s" % (HOST, PORT))
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
      af, socktype, proto, canonname, sa = res
      try:
        s = socket.socket(af, socktype, proto)
      except socket.error as msg:
        s = None
        continue
      try:
        s.connect(sa)
      except socket.error as msg:
        s.close()
        s = None
        continue
      break
    if s is None:
      raise IOError("Couln't connect to server")
    return (s)

  def add_queueout(self, data):
    self.outThread.q_outLock.acquire()
    self.outThread.q_out.put(data)
    self.outThread.q_outLock.release()
    self.outThread.wakeup()
    pass

  def stop(self):
    self.inThread.running = False
    self.outThread.running = False
    self.outThread.wakeup()

  def run(self):
    log.debug("Starting")
    self.outThread = outThread(self.s, self.s_lock)
    self.inThread = inThread(self.s, self.s_lock, self.recv_handler)
    self.running = True
    while not self.processThread.running:
      time.sleep(0.1)
    self.outThread.start()
    self.inThread.start()
    self.inThread.join()
    self.outThread.join()
    self.s.close()
    log.debug("Exiting")
