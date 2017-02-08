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

startdate = datetime.datetime.now() +  datetime.timedelta(minutes = 2)
enddate = datetime.datetime.now() +  datetime.timedelta(days = 7)
duration = datetime.timedelta(minutes = 1)

print "\n\n--- User " + username1 + " ---"

u = User()
login = u.auth(api_url,username1,password1)
if login != True and u.usertype != USER:
    exit()
else:
    print "\nSuccessfully authenticated user: " + username1

print "\nService offerings:"
serv = u.listServOff()
for service in serv:
    print "Found service offering with id: " + service['id'] +  " and name: " + service['name']

print "\nTemplates:"
temp = u.listTempl()
for template in temp:
     print "Found template with id: " + template['id'] +  " and name: " + template['name']

print "\nZones:"
zon = u.listZones()
for zone in zon:
    print "Found zone with id: " + zone['id'] +  " and name: " + zone['name']

print "\nNetworks:"
net = u.listNet()
for network in net:
	    print "Found network  with id: " + network['id'] +  " and name: " + network['name']

name = username1 + "-vm"
print "\nScheduling vm with name \"" + name + "\" to be created between " + str(startdate) + " and " + str(enddate) + " with duration " + str(duration)
res = s.schedulevm(u, zon[0]['id'], temp[0]['id'], serv[1]['id'], net[1]['id'], name, startdate, enddate, duration)
if res == 0:
    print "Failed to find slot!"

print "\n\n--- User " + username2 + " ---"

u = User()
login = u.auth(api_url,username2,password2)
if login != True and u.usertype != USER:
    exit()
else:
    print "\nSuccessfully authenticated user: " + username2

print "\nService offerings:"
serv = u.listServOff()
for service in serv:
    print "Found service offering with id: " + service['id'] +  " and name: " + service['name']

print "\nTemplates:"
temp = u.listTempl()
for template in temp:
     print "Found template with id: " + template['id'] +  " and name: " + template['name']

print "\nZones:"
zon = u.listZones()
for zone in zon:
    print "Found zone with id: " + zone['id'] +  " and name: " + zone['name']

print "\nNetworks:"
net = u.listNet()
for network in net:
	    print "Found network  with id: " + network['id'] +  " and name: " + network['name']

name = username2 + "-vm"
print "\nScheduling vm with name \"" + name + "\" to be created between " + str(startdate) + " and " + str(enddate) + " with duration " + str(duration)
res = s.schedulevm(u, zon[0]['id'], temp[0]['id'], serv[1]['id'], net[1]['id'], name, startdate, enddate, duration)
if res == 0:
    print "Failed to find slot!"

print "\n\nScehduled jobs for all users:"
jobs = s.listjobs()
for job in jobs:
    out = "\nScheduled job with id: " + job['id'] + " to create vm at: " + str(job['start']) + " and destroy it at: " + str(job['end']) + " with name: " + job['name'] + " , zone: " + job['zone'] + " , template: " + job['template'] + " , service offering: " + job['serv'] + " , network: " + job['net']
    if 'ip' in job:
        out = out + " and ip: " + job['ip']
    out = out + " for user: " + job['user']
    print out


exit=False
selection="0"

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
