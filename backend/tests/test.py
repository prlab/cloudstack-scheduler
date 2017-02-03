#!/bin/python

import sys
sys.path.append('../libs/')

from schcs import *

s = Scheduler("./config.ini")
api_url = s.api_url

""".................................."""
#User test1
username1="test"
password1="test"

#User test2
username2="test2"
password2="test2"
""".................................."""

print "\n\n--- User " + username1 + " ---"

u = User()
login = u.auth(api_url,username1,password1)
if login != True and u.usertype != USER:
    exit()

serv = u.listServOff()
temp = u.listTempl()
zon = u.listZones()
net = u.listNet()

name = username1 + "-" + str(uuid.uuid4())
date1 = datetime.datetime.now() +  datetime.timedelta(seconds = 10)
date2 = datetime.datetime.now() +  datetime.timedelta(seconds = 60)
duration = datetime.timedelta(seconds = 40)
print "Scheduling vm with name \"" + name + "\" to be created between " + str(date1) + " and " + str(date2) + " with duration " + str(duration)
res = s.schedulevm(u, zon[0]['id'], temp[0]['id'], serv[0]['id'], net[0]['id'], name, date1, date2, duration)
if res == 0:
    print "Failed to find slot!"



print "\n\n--- User " + username2 + " ---"

u = User()
login = u.auth(api_url,username2,password2)
if login != True and u.usertype != USER:
    exit()

serv = u.listServOff()
temp = u.listTempl()
zon = u.listZones()
net = u.listNet()

name = username2 + "-" + str(uuid.uuid4())
date1 = datetime.datetime.now() +  datetime.timedelta(seconds = 20)
date2 = datetime.datetime.now() +  datetime.timedelta(minutes = 90)
duration = datetime.timedelta(seconds = 40)
print "Scheduling vm with name \"" + name + "\" to be created between " + str(date1) + " and " + str(date2) + " with duration " + str(duration)
res = s.schedulevm(u, zon[0]['id'], temp[0]['id'], serv[0]['id'], net[0]['id'], name, date1, date2, duration)
if res == 0:
    print "Failed to find slot"



exit=False
selection="0"

while exit!=True:
  print "\n1. List jobs for all users\n2. List jobs for user \"test2\"\n3. Cancel the first job of user \"test2\"\nq. Exit"
  selection=raw_input("Select: ")

  if selection=="1":
    print "\nScehduled jobs for all users:"
    jobs = s.listjobs()
    for job in jobs:
        out = "\nScheduled job with id: " + job['id'] + " to create vm at: " + str(job['start']) + " and destroy it at: " + str(job['end']) + " with name: " + job['name'] + " , zone: " + job['zone'] + " , template: " + job['template'] + " , service offering: " + job['serv'] + " , network: " + job['net']
        if 'ip' in job:
            out = out + " and ip: " + job['ip']
        out = out + " for user: " + job['user']
        print out

  if selection=="2":
      print "\nScehduled jobs for user \"" + username2 + "\":"
      jobs = s.listjobs(u)
      for job in jobs:
          out = "\nScheduled job with id: " + job['id'] + " to create vm at: " + str(job['start']) + " and destroy it at: " + str(job['end']) + " with name: " + job['name'] + " , zone: " + job['zone'] + " , template: " + job['template'] + " , service offering: " + job['serv'] + " , network: " + job['net']
          if 'ip' in job:
              out = out + " and ip: " + job['ip']
          out = out + " for user: " + job['user']
          print out

  if selection=="3":
      print "\nCanceling the first job of user \"" + username2 + "\""
      jobs = s.listjobs(u)
      s.cancel(jobs[0]['id'])

  elif selection=="q":
    exit=True
