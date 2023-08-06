#!/usr/bin/python
# -*- coding: latin9 -*-

from PyQt4 import QtGui, QtCore
from queue import Queue
from config import usercmd_handler, get_config
from _version import __version__
from time import gmtime, strftime
import ns_utils
import urllib.request, urllib.parse, urllib.error
import logging

log = logging.getLogger('')

class UIbridge(QtCore.QThread):
  def __init__(self):
    super(UIbridge, self).__init__()
    self.q_exec = Queue()
    self.mutex = QtCore.QMutex()
    self.cond = QtCore.QWaitCondition()
    self.running = True
    self.wait = False
    pass

  def __del__(self):
    self.wait()
    pass

  def add_to_queue(self, signal, *args):
    self.mutex.lock()
    self.q_exec.put((signal, args))
    self.wait = False
    self.cond.wakeAll()
    self.mutex.unlock()
    pass

  def process(self, data):
    signal = data[0]
    args = data[1]
    signal.emit(*args)
    pass

  def run(self):
    while self.running:
      self.mutex.lock()
      if not self.q_exec.empty():
        data = self.q_exec.get()
        self.mutex.unlock()
        self.process(data)
      else:
        self.mutex.unlock()
      if self.wait:
        self.mutex.lock()
        self.cond.wait(self.mutex)
        self.mutex.unlock()
      self.wait = True
    pass

class mainWindow(QtGui.QMainWindow):
  addTab_signal = QtCore.pyqtSignal(dict)

  def __init__(self, title, thread):
    super(mainWindow, self).__init__()
    self.thread = thread
    self.initUI(title)
    self.tablist = []
    self.bridge = UIbridge()
    self.bridge.start()
    pass

  def send(self):
    title = self.tabs.tabText(self.tabs.currentIndex())
    if title is not "Home":
      widgets = None
      for username, curwidgets in self.tablist:
        if username == title:
          widgets = curwidgets
          break
        pass
      msgbar = widgets['msgbar']
      msg = msgbar.text()
      ns_utils.send_msg(self.thread, title, msg)
      msgbar.setText('')
      recvzone = widgets['recvzone']
      curtime = strftime("[%H:%M:%S]", gmtime())
      echo = "->(" + curtime + " " + title + ") " + msg
      recvzone.append(echo)
      self.show()
    pass

  def newMsgTab(self, title):
    main = QtGui.QGroupBox()
    layout = QtGui.QGridLayout()
    layout.setSpacing(10)

    recvzone = QtGui.QTextEdit(main)
    recvzone.setReadOnly(True)
    layout.addWidget(recvzone, 0, 0, 9, 2)

    msgbar = QtGui.QLineEdit(main)
    sendbutton = QtGui.QPushButton("Send", main)
    msgbar.connect(msgbar, QtCore.SIGNAL("returnPressed()"), self.send)
    sendbutton.clicked.connect(self.send)

    layout.addWidget(msgbar, 10, 0)
    layout.addWidget(sendbutton, 10, 1)
    main.setLayout(layout)

    self.tabs.addTab(main, title)
    widgets = dict(main=main, recvzone=recvzone, sendbutton=sendbutton,
        msgbar=msgbar)
    return (widgets)

  def addTab(self, msgdata):
    widgets = None
    for username, curwidgets in self.tablist:
      if username == msgdata['username']:
        widgets = curwidgets
        break
      pass
    curtime = strftime("[%H:%M:%S]", gmtime())
    msg = curtime + " " + msgdata['username'] + ":" + urllib.parse.unquote(msgdata['msg'])
    if not widgets:
      widgets = self.newMsgTab(msgdata['username'])
      self.tablist.append((msgdata['username'], widgets))
      pass
    widgets['recvzone'].append(msg)
    self.show()
    pass

  def recv_private_msg(self, thread, m):
    msgdata = dict(socknum=int(m.group(1)), usertype=m.group(2), low_t=int(m.group(3)),\
        hi_t=int(m.group(4)), username=m.group(5), ip=m.group(6),\
        workstation=m.group(7), location=m.group(8),\
        group=m.group(9), msg=m.group(10))

    try:
      self.addTab_signal.disconnect(self.addTab)
    except TypeError:
      pass
    self.addTab_signal.connect(self.addTab)
    self.bridge.add_to_queue(self.addTab_signal, msgdata)
    pass

  def updateUserSpace(self, userinfowidget, username):
    userinfowidget.setTitle(username)
    children = userinfowidget.findChildren(QtGui.QLabel)
    try:
      userinfo = ns_utils.get_status(self.thread, (str(username),))[0]
    except IndexError:
      userinfo = None
    for i, child in enumerate(children):
      if child.__class__.__name__ == "QLabel":
        title = child.text().split(' :')[0]
        if userinfo:
          info = userinfo[str(title)]
        else:
          info = "Disconnected"
        child.setText(title + " :  " + str(info))
      pass

  def handle_listclick(self, item):
    username = item.text()
    self.updateUserSpace(self.userinfo, username)
    pass

  def handle_listdoubleclick(self, item):
    listusername = item.text()
    widgets = None
    for username, curwidgets in self.tablist:
      if username == listusername:
        widgets = curwidgets
        break
      pass
    if not widgets:
      widgets = self.newMsgTab(listusername)
      self.tablist.append((listusername, widgets))
    self.tabs.setCurrentWidget(widgets['main'])

  def initUI(self, title):
    def initHome(self):
      def initUserSpace(self, parent):
        layout = QtGui.QGridLayout()
        layout.setSpacing(25)
        layout.addWidget(QtGui.QLabel("socknum :", parent), 0, 0)
        layout.addWidget(QtGui.QLabel("username :", parent), 1, 0)
        layout.addWidget(QtGui.QLabel("ip :", parent), 0, 1)
        layout.addWidget(QtGui.QLabel("login_time :", parent), 2, 0)
        layout.addWidget(QtGui.QLabel("update_time :", parent), 2, 1)
        layout.addWidget(QtGui.QLabel("low_t :", parent), 5, 0)
        layout.addWidget(QtGui.QLabel("hi_t :", parent), 5, 1)
        layout.addWidget(QtGui.QLabel("wtype :", parent), 6, 0)
        layout.addWidget(QtGui.QLabel("location :", parent), 3, 0)
        layout.addWidget(QtGui.QLabel("group :", parent), 1, 1)
        layout.addWidget(QtGui.QLabel("status :", parent), 4, 0, 1, 3)
        layout.addWidget(QtGui.QLabel("userdata :", parent), 3, 1)
        parent.setLayout(layout)
        pass

      self.home = QtGui.QGroupBox(title)
      self.homelayout = QtGui.QGridLayout()
      self.homelayout.setSpacing(5)

      self.selfinfo = QtGui.QGroupBox("You", self.home)
      initUserSpace(self, self.selfinfo)

      self.userinfo = QtGui.QGroupBox("username", self.home)
      initUserSpace(self, self.userinfo)

      self.homelayout.addWidget(self.selfinfo, 0, 0, 1, 10)
      self.homelayout.addWidget(self.userinfo, 1, 0, 1, 10)

      self.friendlist = QtGui.QListWidget(self.home)
      friends = get_config("Misc", "watch").split(", ")
      self.friendlist.insertItems(0, friends)
      self.friendlist.itemClicked.connect(self.handle_listclick)
      self.friendlist.itemDoubleClicked.connect(self.handle_listdoubleclick)
      self.homelayout.addWidget(self.friendlist, 0, 11, 2, 1)
      self.home.setLayout(self.homelayout)
      pass

    initHome(self)
    self.updateUserSpace(self.selfinfo, get_config("Auth", "login"))
    self.tabs = QtGui.QTabWidget()
    self.tabs.addTab(self.home, "Home")

    close = QtGui.QAction(QtGui.QIcon('ressources/application-exit-2.png'), 'Close', self)
    close.triggered.connect(QtGui.qApp.quit)

    self.bar = self.addToolBar('Actions')
    self.bar.addAction(close)

    self.setGeometry(100, 100, 800, 600)
    self.setWindowTitle(title)
    self.setCentralWidget(self.tabs)
    privmsg_handler = usercmd_handler + r"\| msg (\S+) dst=(\S+)"
    self.thread.register_handler(privmsg_handler, self.recv_private_msg)
    self.show()
    pass
  pass

def main(thread):
  app = QtGui.QApplication([])
  win = mainWindow("lastSoul v%s" % __version__, thread)
  app.exec_()
  pass

if __name__ == '__main__':
  main(None)
