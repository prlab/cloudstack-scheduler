#!/bin/python

import sys
sys.path.append('../libs/')

from schcs import *

s = Scheduler("./config.ini")
api_url = s.api_url

users = list()

#User test1
username1="test"
password1="test"

#User test2
username2="test2"
password2="test2"

#User test3
username3="test3"
password3="test3"

u1 = User()
login = u1.auth(api_url,username1,password1)
if login != True and u1.usertype != USER:
    exit()
users.append(u1)

u2 = User()
login = u2.auth(api_url,username2,password2)
if login != True and u2.usertype != USER:
    exit()
users.append(u2)

u3 = User()
login = u3.auth(api_url,username3,password3)
if login != True and u3.usertype != USER:
    exit()
users.append(u3)

servid = "badba0a6-6337-487c-9301-9fd93b42a1d6"
tempid = "05a11b78-3679-11e4-9550-e6d31998de48"
zonid = "7193052f-ff2f-4ce7-a2d0-48dd9251ae30"
netid = "bcb79122-7df0-4b09-a8ba-4606e07eeeaa"
startdate = datetime.datetime.now() +  datetime.timedelta(minutes = 15)
stopdate = datetime.datetime.now() +  datetime.timedelta(days= 7)
duration = datetime.timedelta(days = 3)

for user in users:
    for vmnum in range(1, 12):
        vmname = user.username + "-" + "vm" + str(vmnum)
        res = s.schedulevm(user, zonid, tempid, servid, netid, vmname, startdate, stopdate, duration)
        if res == False:
            print "Failed to find available slot for vm with name \"" + vmname + "\" to be created between " + str(startdate) + " and " + str(stopdate) + " with duration " + str(duration)
        else:
            print "Scheduling vm with name \"" + vmname + "\" to be created between " + str(startdate) + " and " + str(stopdate) + " with duration " + str(duration)

while exit!=True:
  print "\n1. List jobs for all users\nq. Exit"
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

  elif selection=="q":
    exit=True
