#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetWatch.py -- A health dashboard for your network
# Copyright 2015 Will Bradley
#

# Command-line GUI
import curses
import curses.wrapper
# Timer
from gi.repository import GLib, GObject
# Pinging
import subprocess
# Regex
import re
# Unicode
import locale
locale.setlocale(locale.LC_ALL, '')
encoding = locale.getpreferredencoding()

# Variables
host = "8.8.8.8"
ping_frequency = 5

class Pinger:
  ping_log = []
  paused = False
  autostart = False
  icon_height = 22

  def ping(self):
    self.draw()
    ping = subprocess.Popen(
        ["ping", "-c", "1", host],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE
    )
    out, error = ping.communicate()
    m = re.search('time=(.*) ms', out)
    if error or m == None:
      self.log_ping(-1)
    else:
      latency = "%.2f" % float(m.group(1))
      self.log_ping(latency)
    self.count += 1
    GObject.timeout_add_seconds(self.timeout, self.ping)
    self.stdscr.addstr(0,0,"Internet: "+str(latency), curses.color_pair(3))
    self.draw()

  def draw(self):
    for i,p in enumerate(self.ping_log):
      if float(p) == -1:
        graph = "E "#u'\u2847' # Error
        color = curses.color_pair(1)
      elif float(p) < 30:
        graph = u'\u2840'
        color = curses.color_pair(2)
      elif float(p) < 100:
        graph = u'\u2844'
        color = curses.color_pair(2)
      elif float(p) < 200:
        graph = u'\u2846'
        color = curses.color_pair(1)
      else:
        graph = u'\u2847'
        color = curses.color_pair(1)
      self.stdscr.addstr(1,i,graph.encode(encoding), color)

    self.stdscr.refresh()

  def log_ping(self, value):
    self.ping_log.append(float(value))
    #self.update_log_menu()
    # limit the size of the log
    if len(self.ping_log) >= self.ping_log_max_size:
      # remove the earliest ping, not the latest
      self.ping_log.pop(0) 

  def __init__(self, stdscr):
    # start the ping process
    self.stdscr = stdscr
    self.window_size = stdscr.getmaxyx() # returns an array [height,width]
    self.ping_log_max_size = self.window_size[1] # max width
    self.timeout = ping_frequency
    self.count = 1
    self.ping()
    self.loop = GLib.MainLoop()
    self.loop.run()


def main(stdscr):

  curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK);
  curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK);
  curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK);

  pinger = Pinger(stdscr)

if __name__ == '__main__':
  curses.wrapper(main)

