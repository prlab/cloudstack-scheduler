#!/bin/python

import sys
sys.path.append('../libs/')

from schcs import *

s = Scheduler("./config.ini")
api_url = s.api_url

username="test"
password="test"

u = User()
login = u.auth(api_url,username,password)
if login != True and u.usertype != USER:
    exit()

serv = u.listServOff()
for service in serv:
    print "Found service offering with id: " + service['id'] +  " and name: " + service['name']


temp = u.listTempl()
for template in temp:
    print "Found template with id: " + template['id'] +  " and name: " + template['name']

zon = u.listZones()
for zone in zon:
    print "Found zone with id: " + zone['id'] +  " and name: " + zone['name']


name = "test-vm"
servid = "b6501e75-0b43-487d-89ed-117ff03350fe"
tempid = "05a11b78-3679-11e4-9550-e6d31998de48"
zonid = "7193052f-ff2f-4ce7-a2d0-48dd9251ae30"
start = datetime.datetime(2017, 2, 1, 12, 30)
end = datetime.datetime(2017, 2, 8, 12, 30)
duration = datetime.timedelta(days = 4, hours=12)
print "Scheduling vm with name \"" + name + "\" to be created between " + str(start) + " and  " + str(end) + " with duration " + str(duration)
res = s.schedulevm(u, zonid, tempid, servid, name, start, end, duration)
if res == 0:
    print "Failed to find available time slot to host the vm!"

jobs = s.listjobs()
for job in jobs:
    out = "Scheduled job with id: " + job['id'] + " to create vm at: " + str(job['start']) + " and destroy it at: " + str(job['end']) + " with name: " + job['name'] + " , zone: " + job['zone'] + " , template: " + job['template'] + " , service offering: " + job['serv']
    if 'ip' in job:
        out = out + " and ip: " + job['ip']
    out = out + " for user: " + job['user']
    print out

jobs = s.listjobs(u)
for job in jobs:
    out = "Scheduled job with id: " + job['id'] + " to create vm at: " + str(job['start']) + " and destroy it at: " + str(job['end']) + " with name: " + job['name'] + " , zone: " + job['zone'] + " , template: " + job['template'] + " , service offering: " + job['serv']
    if 'ip' in job:
        out = out + " and ip: " + job['ip']
    out = out + " for user: " + job['user']
    print out

s.cancel(jobs[0]['id'])

jobs = s.listjobs()
for job in jobs:
    out = "Scheduled job with id: " + job['id'] + " to create vm at: " + str(job['start']) + " and destroy it at: " + str(job['end']) + " with name: " + job['name'] + " , zone: " + job['zone'] + " , template: " + job['template'] + " , service offering: " + job['serv']
    if 'ip' in job:
        out = out + " and ip: " + job['ip']
    out = out + " for user: " + job['user']
    print out
