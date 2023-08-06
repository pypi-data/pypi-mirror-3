from socketThread import socketThread
import threading
import re
import queue
import logging

log = logging.getLogger('')

class	processThread(threading.Thread):
  def __init__(self, threadID, name):
    super(processThread, self).__init__()
    log.debug("Creating")
    self.daemon = True
    self.running = False
    self.socketThread = None
    self.threadID = threadID
    self.name = name
    self.wait = False
    self.authed = False
    self.q_in = queue.Queue()
    self.q_out = queue.Queue()
    self.q_inLock = threading.Lock()
    self.q_outLock = threading.Lock()
    self.funcsLock = threading.Lock()
    self.waitLock = threading.Condition()
    self.inputs = []
    self.funcs = []
    pass

  def process_in(self, data):
    self.inputs.append(data)
    pass

  def process_out(self, data):
    self.socketThread.add_queueout(data+'\n')
    pass

  def register_handler(self, match, func):
    self.funcsLock.acquire()
    log.debug("func %s registered" % func)
    self.funcs.append([match, func])
    self.funcsLock.release()
    pass

  def forget_handler(self, func):
    self.funcsLock.acquire()
    for i, (match, funcname) in enumerate(self.funcs):
      if func is funcname:
        self.funcs.pop(i)
        log.debug("%s forgotten" % func)
        break
    self.funcsLock.release()

  def add_queuein(self, data):
    if len(data):
      self.q_inLock.acquire()
      self.q_in.put(data)
      self.q_inLock.release()
      self.wakeup()

  def add_queueout(self, data):
    if len(data):
      self.q_outLock.acquire()
      self.q_out.put(data)
      self.q_outLock.release()
      self.wakeup()

  def check_enter(self):
    for input in enumerate(self.inputs):
      found = False
      for func in self.funcs:
        m = re.match(func[0], input[1])
        if m:
          log.debug("Match found with [%s], calling %s" % (input[1], func[1]))
          if func[1]:
            func[1](self, m)
            found = True
      if found:
        self.inputs.pop(input[0])

  def recv(self, data):
    if self.running:
      self.add_queuein(data)

  def stop(self):
    self.running = False
    self.wakeup()

  def wakeup(self):
    log.debug("Waking up")
    self.waitLock.acquire()
    self.waitLock.notify()
    self.waitLock.release()
    self.wait = False

  def nothing_to_do(self):
    self.q_outLock.acquire()
    qout = not self.q_out.empty()
    self.q_outLock.release()
    self.q_inLock.acquire()
    qin = not self.q_in.empty()
    self.q_inLock.release()
    wait = qout or qin or self.wait
    return (not wait)

  def run(self):
    log.debug("Starting")
    self.running = True

    while self.running:
      self.q_inLock.acquire()
      if not self.q_in.empty():
        data = self.q_in.get()
        self.q_inLock.release()
        self.process_in(data)
      else:
        self.q_inLock.release()

      self.q_outLock.acquire()
      if not self.q_out.empty():
        data = self.q_out.get()
        self.q_outLock.release()
        self.process_out(data)
      else:
        self.q_outLock.release()

      self.check_enter()
      if self.nothing_to_do():
        self.waitLock.acquire()
        self.waitLock.wait()
        self.waitLock.release()

    self.socketThread.running = False
    log.debug("Exiting")
    pass
