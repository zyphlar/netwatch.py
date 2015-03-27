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
internet_host = "8.8.8.8"
ping_frequency = 5

class Pinger:
  internet_log = []

  def run(self):
    internet_latency = self.ping(internet_host,self.internet_log)
    self.draw("Internet:",self.internet_log,internet_latency,0)

    # Schedule next run
    GObject.timeout_add_seconds(self.timeout, self.run)


  def ping(self,host,log):

    # Do the ping
    ping = subprocess.Popen(
        ["ping", "-c", "1", host],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE
    )
    out, error = ping.communicate()
    m = re.search('time=(.*) ms', out)

    if error or m == None:
      latency = 9999
      logged = -1
    else:
      latency = float(m.group(1))
      logged = latency

    # store [graph, color, subjective] in array
    log.append(self.interpret_ping(float(logged)))

    # limit the size of the log
    if len(log) >= self.ping_log_max_size:
      # remove the earliest ping, not the latest
      log.pop(0) 

    return latency

  def draw(self,title,log,latency,line):
 
    # Draw internet heading on specified line
    self.stdscr.addstr(line,0,title, curses.color_pair(3))
    interpret = self.interpret_ping(latency)
    self.stdscr.addstr(line,10,interpret['subjective'], interpret['color'])
    right_align = self.ping_log_max_size-16
    self.stdscr.addstr(line,right_align,str(round(latency/1000,3))+" second lag", interpret['color'])

    # Draw graph on next line
    for idx,entry in enumerate(log):
      self.stdscr.addstr(line+1,idx,entry['graph'].encode(encoding), entry['color'])
    self.stdscr.refresh()

  def interpret_ping(self, ping):
    ping = float(ping)
    if ping == -1:
      graph = "E "#u'\u2847' # Error
      color = curses.color_pair(1)
      subjective = "Down"
    elif ping < 30:
      graph = u'\u2840'
      color = curses.color_pair(2)
      subjective = "Great"
    elif ping < 70:
      graph = u'\u2844'
      color = curses.color_pair(2)
      subjective = "Good"
    elif ping < 120:
      graph = u'\u2846'
      color = curses.color_pair(1)
      subjective = "Fair"
    else:
      graph = u'\u2847'
      color = curses.color_pair(1)
      subjective = "Poor"
    return {'graph': graph, 'color': color, 'subjective': subjective, 'ping': float(ping)}

  def __init__(self, stdscr):
    # initialize screen and parameters
    self.stdscr = stdscr
    self.window_size = stdscr.getmaxyx() # returns an array [height,width]
    self.ping_log_max_size = self.window_size[1] # max width
    self.timeout = ping_frequency

    # start the ping process
    self.run()

    self.loop = GLib.MainLoop()
    self.loop.run()


def main(stdscr):

  # Initialize color pairs
  curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
  curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
  curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

  # Create runtime class
  pinger = Pinger(stdscr)

if __name__ == '__main__':
  curses.wrapper(main)

