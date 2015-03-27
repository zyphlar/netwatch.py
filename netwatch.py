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
import socket, struct
from netaddr import *
import nmap
# Regex
import re
# Unicode
import locale

# Configure Unicode
locale.setlocale(locale.LC_ALL, '')
encoding = locale.getpreferredencoding()

class Pinger:
  internet_log = []
  router_log = []
  count = 11 # start at 11 so the scan will run next time

  def run(self):
    # Run network scan every 12 runs (60 seconds)
    if self.count%12 == 0:
      self.stdscr.clear() # clear window every scan run (not every run)

      scan_results = self.scan_network(self.router_host+"/24")
      self.draw_scan(scan_results,6)
      self.count = 1

    # Increment counter for scan
    self.count += 1

    # Draw internet graph
    internet_latency = self.ping(self.internet_host,self.internet_log)
    self.draw_log("Internet:",self.internet_host,self.internet_log,internet_latency,0)

    # Draw router graph
    router_latency = self.ping(self.router_host,self.router_log)
    self.draw_log("Router:",self.router_host,self.router_log,router_latency,3)

    # Schedule next run
    GObject.timeout_add_seconds(self.timeout, self.run)

    self.stdscr.refresh() # output drawing to screen

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

  def draw_log(self,title,subtitle,log,latency,line):
 
    # Draw internet heading on specified line
    self.stdscr.addstr(line,0,title, self.COL_DEFAULT)
    self.stdscr.addstr(line,len(title)+1,subtitle, self.COL_MUTE)
    interpret = self.interpret_ping(latency)
    heading = str(round(latency/1000,3))+" second lag ("+interpret['subjective']+")"
    right_align = self.ping_log_max_size-len(heading)
    self.stdscr.addstr(line,right_align,heading, interpret['color'])

    # Draw graph on next line
    for idx,entry in enumerate(log):
      self.stdscr.addstr(line+1,idx,entry['graph'].encode(encoding), entry['color'])

  def draw_scan(self,scan,line):
    self.stdscr.addstr(line,0,"WiFi:", self.COL_DEFAULT)

    count = 1
    for host, detail in scan:
#      if detail['state'] == "up":
#        color = self.COL_GOOD
#      else:
#        color = self.COL_BAD
      color = self.COL_MUTE
      self.stdscr.addstr(line+count,0,str(host),color)
      count += 1

  def interpret_ping(self, ping):
    ping = float(ping)
    if ping == -1:
      graph = "E "#u'\u2847' # Error
      color = self.COL_BAD
      subjective = "Down"
    elif ping < 30:
      graph = u'\u2840'
      color = self.COL_GOOD
      subjective = "Great"
    elif ping < 70:
      graph = u'\u2844'
      color = self.COL_GOOD
      subjective = "Good"
    elif ping < 120:
      graph = u'\u2846'
      color = self.COL_WARN
      subjective = "Fair"
    else:
      graph = u'\u2847'
      color = self.COL_BAD
      subjective = "Poor"
    return {'graph': graph, 'color': color, 'subjective': subjective, 'ping': float(ping)}

  def get_default_gateway_linux(self):
    # Read the default gateway directly from /proc.
    with open("/proc/net/route") as fh:
      for line in fh:
        fields = line.strip().split()
        if fields[1] != '00000000' or not int(fields[3], 16) & 2:
          continue

        return str(socket.inet_ntoa(struct.pack("<L", int(fields[2], 16))))

  def scan_network(self,subnet):
      nm = nmap.PortScanner()
      nm.scan(hosts=subnet, arguments='-n -sP')
      hosts_list = [(x, nm[x]['status']) for x in nm.all_hosts()]

      return hosts_list

  def __init__(self, stdscr):
    # Parameters
    self.internet_host = "8.8.8.8"
    self.router_host = self.get_default_gateway_linux()
    self.timeout = 5 # Ping frequency
 
    # Create color constants
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_WHITE, -1)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)
    curses.init_pair(5, curses.COLOR_WHITE, -1)

    self.COL_BAD = curses.color_pair(1)
    self.COL_GOOD = curses.color_pair(2)
    self.COL_DEFAULT = curses.color_pair(3)|curses.A_BOLD
    self.COL_WARN = curses.color_pair(4)
    self.COL_MUTE = curses.color_pair(5)|curses.A_DIM

    # Initialize screen
    self.stdscr = stdscr
    self.window_size = stdscr.getmaxyx() # returns an array [height,width]
    self.ping_log_max_size = self.window_size[1] # max width

    # Hide cursor
    curses.curs_set(0)

    # start the ping process
    self.run()

    # Keep running until ctrl+c
    self.loop = GLib.MainLoop()
    self.loop.run()

def main(stdscr):
  # Initialize runtime class
  pinger = Pinger(stdscr)

if __name__ == '__main__':
  curses.wrapper(main)

