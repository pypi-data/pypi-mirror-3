#!/usr/bin/python

"""
This class defines an object that knows how to create, update, and report on a Round Robin Database file that tracks bandwidth usage via /proc/net/dev.
NOTE = tested on RedHat 5 and 6 only
REQUIREMENTS = class requires rrdtool, rrdtool-python RPMs, as well as python-daemon-1.5.5 from PyPI
"""

#IMPORTS#
import rrdtool
import sys
import os
import time
import datetime
from operator import itemgetter
import daemon
import lockfile
import signal

#ENV#
os.environ['TZ'] = 'UTC'
time.tzset()

class bandwidthTracker:
  
  #CLASS VARS#
  workingDir = '/var/lib/bandwidthMonitor/'
  db = workingDir + 'eth0.rrd'
  deviceFile = '/proc/net/dev'



  def __init__(self):
    """
    On object initialization, class first checks for existence of the RRD file. 
    If TRUE, it populates dictionary attributes with existing data for reporting.
    If FALSE, it creates the RRD file and populates what will be empty dictionaries
    """
    #initialize empty dictionaries to hold data
    self.dictDays = {}
    self.dictMonths = {}

    if os.path.isdir(self.workingDir) != True : os.mkdir(self.workingDir)
    if os.path.isfile(self.db) != True:
      self.rrdCreate()
      self.dictInit()
    else:
      self.dictInit()




  def rrdCreate(self):
    """
    This method creates the rrd file, with appropriate settings to accomadate one year of data with 60 second updates.
    NOTE: currently the methods do not rely on either of the RRA's that summarize by hour or day, due to undesireable assumptions made by rrdtool concerning days with incomplete data.
    """

    rrdtool.create(self.db, "--step", "60", "--start", '0',
                        "DS:rxRate:COUNTER:120:U:U",
                        "DS:txRate:COUNTER:120:U:U",
                        "RRA:AVERAGE:0.5:1:525600",    # 1 year - every 1 min
                        "RRA:AVERAGE:0.5:60:8760",     # 1 year - every 1 hour
                        "RRA:AVERAGE:0.5:1440:365")    # 1 year - every day



  
  def dictInit(self, daysQuery=365):
    """
    This method reads the rrd and creates two dictionaries, key=day and key=month.  These will be used for reporting via various sorts.
    """
    #initialize instance attributes for fresh data
    self.dictDays = {}
    self.dictMonths = {}

    for i in range(daysQuery,-1,-1):
      day = str(i)
      x = rrdtool.fetch(self.db, 'AVERAGE', '-r 60', '-s 00:00 -' + day + 'd', '-e 23:59 -' + day + 'd')
      date = datetime.date.fromtimestamp(x[0][0])
      rxBps = 0
      txBps = 0
      totalBps = 0
      minutes = 0
      dataPresent = False
  
      for i in x[2]: #loop through all entries for day, and ceate totals for values
        if i[0] != None and i[1] != None:
          rxBps += i[0]
          txBps += i[1]
          totalBps += (i[0] + i[1])
          minutes += 1
          dataPresent = True

      if dataPresent == True: #if any entries present for day, execute creation of dictionary entries
        rxMB = rxBps * 60 / 1024 / 1024
        rxGB = rxBps * 60 / 1024 / 1024 / 1024
        txMB = txBps * 60 / 1024 / 1024
        txGB = txBps * 60 / 1024 / 1024 / 1024
        totalMB = totalBps * 60 / 1024 / 1024
        totalGB = totalBps * 60 / 1024 / 1024 / 1024
        rateKbps = (rxBps + txBps) * 8 / minutes / 1024
        rateMbps = (rxBps + txBps) * 8 / minutes / 1024 / 1024
  
        self.dictDays[date] = [rxMB, rxGB, txMB, txGB, totalMB, totalGB, minutes, rateKbps, rateMbps]

        month = str(date.year) + "-" + str(date.month)
        if self.dictMonths.has_key(month):
          self.dictMonths[month][0] += rxMB
          self.dictMonths[month][1] += rxGB
          self.dictMonths[month][2] += txMB
          self.dictMonths[month][3] += txGB
          self.dictMonths[month][4] += totalMB
          self.dictMonths[month][5] += totalGB
          self.dictMonths[month][6] += minutes
          self.dictMonths[month][7] = (self.dictMonths[month][4] * 8 * 1024) / (self.dictMonths[month][6] * 60)
          self.dictMonths[month][8] = (self.dictMonths[month][4] * 8) / (self.dictMonths[month][6] * 60)
        else:
          self.dictMonths[month] = [rxMB, rxGB, txMB, txGB, totalMB, totalGB, minutes, rateKbps, rateMbps]



  def rrdDaemon(self):
    """
    This method daemonizes the "rrdUpdate" method.
    """

    context = daemon.DaemonContext(
      working_directory=self.workingDir,
      umask=0o002,
      pidfile=lockfile.FileLock(workingDir + 'rrdUpdate.pid'),
    )

    context.signal_map = {
      #signal.SIGTERM: function_cleanup,
      signal.SIGHUP: 'terminate',
      #signal.SIGUSR1: function_reload,
    }

    with context:
      self.rrdUpdate()




  def rrdUpdate(self):
    """
    This method updates the RRD, once per minute
    """

    while True:
      f = open(self.deviceFile, "r")
      list = f.readlines()

      for i in list:
        if i.find("eth0") != -1:
          rxNew = i.split(":")[1].split()[0]
          txNew = i.split(":")[1].split()[8]
      print 'updating: ' + rxNew + ':' + txNew
      rrdtool.update(self.db, '--', '-5h@' + rxNew + ':' + txNew)
      time.sleep(60)



  def reportDays(self):
    """
    Takes dictionary of days instance attribute, and summarizes 60 second RRPs by days.
    """

    print "    day    |       rx       |       tx       |       total       |     avg. kbps     "
    print "-----------+----------------+----------------+-------------------+-------------------"

    l = [ [ k,v[0],v[1],v[2],v[3],v[4],v[5],v[6],v[7],v[8] ] for k,v in self.dictDays.items() ]
    l.sort(key=itemgetter(0))

    for i in l:
      if i[1] <= 1000:
        print "%-11s| %9.3f rxMB" % (i[0], i[1]),
      else:
        print "%-11s| %9.3f rxGB" % (i[0], i[2]),
      if i[3] <= 1000:
        print "| %9.3f txMB" % (i[3]),
      else:
        print "| %9.3f txGB" % (i[4]),
      if i[5] <= 1000:
        print "| %9.3f totalMB" % (i[5]),
      else:
        print "| %9.3f totalGB" % (i[6]),
      print "| Avg Kbps = %.3f" % (i[8])

    print "-----------+----------------+----------------+-------------------+-------------------"




  def reportDaysByTotal(self):
    """
    Takes dictionary of days instance attribute, and summarizes 60 second RRPs by days sorted by most bandwidth used.
    """

    print "    day    |       rx       |       tx       |       total       |     avg. kbps     "
    print "-----------+----------------+----------------+-------------------+-------------------"

    l = [ [ k,v[0],v[1],v[2],v[3],v[4],v[5],v[6],v[7],v[8] ]  for k,v in self.dictDays.items()]
    l.sort(key=itemgetter(5))

    for i in l:
      if i[1] <= 1000:
        print "%-11s| %9.3f rxMB" % (i[0], i[1]),
      else:
        print "%-11s| %9.3f rxGB" % (i[0], i[2]),
      if i[3] <= 1000:
        print "| %9.3f txMB" % (i[3]),
      else:
        print "| %9.3f txGB" % (i[4]),
      if i[5] <= 1000:
        print "| %9.3f totalMB" % (i[5]),
      else:
        print "| %9.3f totalGB" % (i[6]),
      print "| Avg Kbps = %.3f" % (i[8])

    print "-----------+----------------+----------------+-------------------+-------------------"



  def reportMonths(self):
    """
    Takes dictionary of months instance attribute, and summarizes 60 second RRPs by months.
    """
  
    print "   month   |       rx       |       tx       |       total       |     avg. kbps     "
    print "-----------+----------------+----------------+-------------------+-------------------"
  
    l = [ [ k,v[0],v[1],v[2],v[3],v[4],v[5],v[6],v[7],v[8] ]  for k,v in self.dictMonths.items()]
    l.sort(key=itemgetter(0))
  
    for i in l:
      if i[1] <= 1000:
        print "%-11s| %9.3f rxMB" % (i[0], i[1]),
      else:
        print "%-11s| %9.3f rxGB" % (i[0], i[2]),
      if i[3] <= 1000:
        print "| %9.3f txMB" % (i[3]),
      else:
        print "| %9.3f txGB" % (i[4]),
      if i[5] <= 1000:
        print "| %9.3f totalMB" % (i[5]),
      else:
        print "| %9.3f totalGB" % (i[6]),
      print "| Avg Kbps = %.3f" % (i[8])
  
    print "-----------+----------------+----------------+-------------------+-------------------"
  
  
  
  
  def reportMonthsByTotal(self):
    """
    Takes dictionary of months instance attribute, and summarizes 60 second RRPs by months sorted by most usage.
    """
  
    print "   month   |       rx       |       tx       |       total       |     avg. kbps     "
    print "-----------+----------------+----------------+-------------------+-------------------"
  
    l = [ [ k,v[0],v[1],v[2],v[3],v[4],v[5],v[6],v[7],v[8] ]  for k,v in self.dictMonths.items()]
    l.sort(key=itemgetter(5))
  
    for i in l:
      if i[1] <= 1000:
        print "%-11s| %9.3f rxMB" % (i[0], i[1]),
      else:
        print "%-11s| %9.3f rxGB" % (i[0], i[2]),
      if i[3] <= 1000:
        print "| %9.3f txMB" % (i[3]),
      else:
        print "| %9.3f txGB" % (i[4]),
      if i[5] <= 1000:
        print "| %9.3f totalMB" % (i[5]),
      else:
        print "| %9.3f totalGB" % (i[6]),
      print "| Avg Kbps = %.3f" % (i[8])
  
    print "-----------+----------------+----------------+-------------------+-------------------"
  
  
  
  
  def reportTotal(self):
    """
    Takes dictionary of months instance attribute, and produces a total.
    """
  
    print "       rx       |       tx       |       total       |     avg. kbps     "
    print "----------------+----------------+-------------------+-------------------"
  
    l = [0,0,0,0,0,0,0,0,0]
    for k,v in self.dictMonths.items():
      l[0] += v[0]
      l[1] += v[1]
      l[2] += v[2]
      l[3] += v[3]
      l[4] += v[4]
      l[5] += v[5]
      l[6] += v[6]
  
    l[7] = (l[4] * 8 * 1024) / (l[6] * 60)
    l[8] = (l[4] * 8) / (l[6] * 60)
  
    if l[0] <= 1000:
      print " %9.3f rxMB" % (l[0]),
    else:
      print " %9.3f rxGB" % (l[1]),
    if l[2] <= 1000:
      print "| %9.3f txMB" % (l[2]),
    else:
      print "| %9.3f txGB" % (l[3]),
    if l[4] <= 1000:
      print "| %9.3f totalMB" % (l[4]),
    else:
      print "| %9.3f totalGB" % (l[5]),
    print "| Avg Kbps = %.3f" % (l[7])
  
    print "----------------+----------------+-------------------+-------------------"
  
