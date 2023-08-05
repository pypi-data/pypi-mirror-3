#!/usr/bin/python

# Disk usage controller


##################################################################

Ident = "disk-alarm.  Vers 2.7 - L.Fini Dec. 2011"

CONFIG_CODE = 15    # Change when structure of configuration changes

def copyright():
  print
  print Ident
  print """
Copyright (C) 2011  Luca Fini

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

A copy of the GNU General Public License can be found at:
<http://www.gnu.org/licenses/>.
"""

def noConfig():
  print
  print "******************************************************"
  print "Configuration file is not readable or obsolete. "
  print
  print "Use:"
  print "     python disk-alarm.py -c   to configure"
  print
  print "     python disk-alarm.py -h   to get help"
  print "******************************************************"

def usage(conf):
  print
  print
  print Ident, "on:", os.uname()[1]
  print """
This procedure executes the command 'df -ka' and parses the output to find
the data occupation of disks."""
  print """
When any disk capacity is under the configured treshold, a warning message 
is sent to a list of e-mail addresses.

Usage: 
         python disk-alarm.py [-c] [-h] [-t] [-q]
         
Where: 
        -q     Quiet mode (do not show info on stdout)
        -t     Send only test email to configured addresses
        -c     Create or modify configuration
        -h     Print this page and exit
        -l     Print license notice and exit

Usually it should be run periodically (e.g.: from cron) with no options.

"""
  if conf:
    print "Current configuration:"
    print "  Config file : %s" % cfgFileName()
    print "  Config.Vers.: %d" % conf.cfgcode
    print "     Disk list: %s" % ', '.join(conf.ctl_list)
    print "      Treshold: %d%%" % perc(conf.guard)
    print "  E-mail addrs: %s"% ', '.join(conf.mail_to)
    print "   Mail server: %s" % conf.mserver
    print "   Sender addr: %s" % conf.mail_from
    print
    if conf.cfgcode != CONFIG_CODE: noConfig()

  else:
    noConfig()

import sys,os
import pickle
import subprocess as sub
import smtplib
import time
from email.MIMEText import MIMEText

df_cmd = "df -ka"


Verbose=True

class Config:
  def __init__(self):
    self.ctl_list=[]
    self.mail_to=[]
    self.sdomain=''
    self.mail_from=''
    self.mserver='localhost'
    self.cfgcode=CONFIG_CODE
    self.guard=0.1

class Info(object):
  def __init__(self):
    self.b=[]
    self.dosend=False

  def newInfo(self,title):
    l="INF: %s"%title
    self.append(l)

  def newWarning(self,title):
    l="WNG: %s"%title
    self.append('')
    self.append(l)
    self.dosend=True

  def newError(self,title):
    l="ERR: %s"%title
    self.append('')
    self.append(l)
    self.dosend=True

  def append(self,l):
    self.b.append(l)

  def printout(self):
    print
    for k in self.b:
      print k

def email(conf,subj,text):
  if isinstance(text,(list,tuple)): body = '\n'.join(text)
  else: body=text

  if isinstance(conf.mail_to,(list,tuple)): tostr = ','.join(conf.mail_to)
  else: tostr=conf.mail_to

## Prepare message 
  mail = MIMEText(body)
  mail['From'] = conf.mail_from
  mail['Subject'] = subj
  mail['To'] = tostr

## Sendit
  smtp = smtplib.SMTP(conf.mserver)
  smtp.sendmail(conf.mail_from, conf.mail_to, mail.as_string())
 
  smtp.quit()

  if Verbose:
    print
    print "Mail message sent to:",tostr
    print


def perc(x):
  return int(x*100.+.5)

def cfgFileName():
  home=os.environ.get('HOME','')
  return os.path.join(home,'.disk-alarm')

def yesno(text):
  a=raw_input(text)
  if a and a[0].lower() == 'y':
    a=True
  else:
    a=False
  return a

def getConfig(silent=False):
  fname=cfgFileName()
  try:
    fd=open(fname)
    conf=pickle.load(fd)
    fd.close()
  except:
    if not silent: noConfig()
    conf=None
  else:
    conf.mail_from='disk-alarm@%s'%conf.sdomain

    if not hasattr(conf,'cfgcode') or conf.cfgcode!=CONFIG_CODE:
      if not silent: noConfig()
      conf=None

  return conf

def doConfig():
  oldconf=getConfig(silent=True)
  if oldconf:
    print "\ndisk-alarm has been configured previously. If you proceed"
    print "previous configuration will be overridden."
    a=yesno("\nOK to proceed [y/N]: ")
    if not a: return
    conf=oldconf
  else:
    conf=Config()

  if conf.ctl_list:
    print "\nCurrent disk list: %s" % ', '.join(conf.ctl_list)
    a=yesno("Do you want to modify the list [y/N]? ")
  else:
    a=True
  if a:
    df_table=readDF()
    print
    print "Select disks to monitor:\n"
    n=0
    keys=df_table.keys()
    lnk=len(keys)
    for i in range(lnk):
      k=keys[i]
      print "%2d. %s (FS: %s)" % (i+1,k,df_table[k][4])
  
    retry=True
    while retry:
      l=raw_input("\nComma separated list (e.g.: 1,2,4): ")
  
      flds=l.split(',')
      if len(flds)==0:
        print "Nothing done"
        return

      selected=[]
      try:
        idx=map(lambda x: int(x)-1,flds)
        for i in range(lnk):
          if i in idx: selected.append(keys[i])
      except:
        print "Invalid list"
        retry=True
      else:
        retry=False
 
    conf.ctl_list=selected

  retry=True
  while retry:
    prc=raw_input("\nTreshold %% (enter to confirm %d): "%perc(conf.guard))
    if not prc:
      prc=perc(conf.guard)
    else:
      prc=int(prc)
    if prc<1 or prc > 99:
      print "Range should be 1..99"
    else:
      retry=False
  conf.guard=prc/100.

  if conf.mail_to:
    print "\nCurrent notify list: %s"%conf.mail_to
    a=yesno("Do you want to modify the list [y/N]? ")
  else:
    a=True

  if a:
    print "\nList of notify e-mail addresses (comma separated)"
    ls=raw_input(" : ")
    mto=ls.split(',')
    conf.mail_to=map(lambda x: x.strip(),mto)

  if conf.sdomain:
    print "\nCurrent mail sender domain: %s"%conf.sdomain
    a=yesno("Do you want to modify it [y/N]? ")
  else:
    a=True

  if a:
    msv=raw_input("\nMail sender domain: ")
    conf.sdomain=msv.strip()

  a=raw_input("\nMail server (enter to confirm: %s): "%conf.mserver)
  if a: conf.mserver=a.strip()

  conf.cfgcode=CONFIG_CODE

  try:
    fd=open(cfgFileName(),'wb')
    pickle.dump(conf,fd)
    fd.close()
  except:
    print "\nCannot write configuration to file: %s"%cfgFileName()
  else:
    print '\nConfiguration successfully written to file: %s\n'%cfgFileName()
    print 'You may verify with "python disk-alarm.py -h"\n'

  return
  

def readDF():
  global info

  pp=sub.Popen(df_cmd,shell=True,stdout=sub.PIPE)

  if pp is None:
    info.newError('Executing: %s'%df_cmd)
    return

  df_table={}
  while 1:
    ll=pp.stdout.readline().strip()
    if not ll: break
    flds=ll.split()
    if len(flds) < 6:
      ll=pp.stdout.readline().strip()
      flds.extend(ll.split())
    dname=flds[0]
    if '/' in dname:
      df_table[dname]=flds[1:]
  return df_table

def main():
  global Verbose
  global info

  if '-q' in sys.argv: Verbose=False

  if '-c' in sys.argv:
    doConfig()
    sys.exit()

  if '-h' in sys.argv:
    conf=getConfig(silent=True)
    usage(conf)
    sys.exit()

  if '-l' in sys.argv:
    copyright()
    sys.exit()


  conf=getConfig()

  if not conf:
    sys.exit()
    
  info=Info()
  info.newInfo("This is %s on %s - %s"%(Ident,os.uname()[1],time.asctime()))

  if '-t' in sys.argv:
    info.newInfo("Configuration details:")
    info.newInfo("   Disk list: %s" % ', '.join(conf.ctl_list))
    info.newInfo("    Treshold: %d%%" % perc(conf.guard))
    info.newInfo("E-mail addrs: %s"% ', '.join(conf.mail_to))
    info.newInfo(" Mail server: %s" % conf.mserver)
    if Verbose: info.printout()
    email(conf,'Test message from %s'%os.uname()[1],info.b)
    sys.exit()
    
  df_table=readDF()

  if not df_table:
    if Verbose: info.printout()
    if info.dosend: email(conf,'DISK USAGE WARNING from %s'%os.uname()[1],info.b)
    sys.exit()

  ctl_table={}
  for k in df_table:
    if k in conf.ctl_list:
      ctl_table[k]=df_table[k]

  vv=ctl_table.keys()
  notf=filter(lambda x: not ctl_table[x], vv)  # Get keys for False values
  for k in notf:
    info.newWarning("disk not found - %s"%k)

  yesf=filter(lambda x: ctl_table[x], vv)  # Get keys for True values

  for k in yesf:
    values=ctl_table[k]
    if len(values)<4:
      info.newError('on line "%s"' % k)
    total=float(values[0])
    used=float(values[1])
    available=float(values[2])
    frac=available/total
    info.newInfo("Disk: %s (KB) - Tot: %.0f  Used: %.0f  Avail: %.0f (%d%%)"%(k,total,used,available,perc(frac)))
    if frac < conf.guard:
      info.newWarning('Disk %s (FS: %s). Free space: %.0f KB (%d%%) IS UNDER %d%%!!'%(k,values[4],available,perc(frac),perc(conf.guard)))

  if Verbose: info.printout()
  if info.dosend: 
    email(conf,'DISK USAGE WARNING from %s'%os.uname()[1],info.b)
  else:
    if Verbose:
      print
      print "No mail message sent"
      print


if __name__ == '__main__': main()
