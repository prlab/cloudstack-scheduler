import cloudstack as cs
import logging
import uuid
from copy import copy
from collections import defaultdict
import datetime
import ConfigParser

from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler


class Scheduler:

  scheduler = None #The apscheduler scheduler
  mycs = None #The Cloudstack api wrapper
  jobs = defaultdict(list) #list of the scheduled jobs {username, domainid, zone, template, service_offering, network, name, start_date, end_date, deployjobid, destroyjobid, vmid, ip}
  maxmemory=0 #max memory that can be used by the scheduler
  api_url="" #The api url of Cloudstack
  api_key="" #The api key of the admin user
  secret_key="" #The secret key of the admin user

  def __init__(self, path):
      self.readconfig(path)
      self.scheduler=self.initScheduler()
      self.mycs=self.auth_api(self.api_url, self.api_key, self.secret_key)

  def readconfig(self, path):
      settings = ConfigParser.ConfigParser()
      settings.read(path)
      self.maxmemory=int(settings.get('global', 'maxmemory'))
      self.api_url=settings.get('global', 'api_url')
      self.api_key=settings.get('global', 'api_key')
      self.secret_key=settings.get('global', 'secret_key')

  def initScheduler(self):

    jobstores = {
      'default':MemoryJobStore()
    }

    executors = {
      'default': {'type': 'threadpool', 'max_workers': 20},
    }

    job_defaults = {
      'coalesce': False,
      'max_instances': 3
    }

    scheduler = BackgroundScheduler()
    scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone="Europe/Athens")
    #scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    scheduler.start()
    #logging.basicConfig()

    return scheduler

  def auth_api(self, api_url, apikey, secretkey):
    myus = cs.ApiKeySession()
    mycs = cs.CloudStack(api_url, myus)
    mycs.open(apikey=apikey, secretkey=secretkey)
    return mycs

  def getServOffName(self, id):
        rs = self.mycs.listServiceOfferings(id=id)
        return rs['serviceoffering'][0]['name']

  def getServOffMem(self, id):
        rs = self.mycs.listServiceOfferings(id=id)
        return rs['serviceoffering'][0]['memory']

  def getTemplName(self, id):
        rs = self.mycs.listTemplates(id=id, templatefilter="executable")
        return rs['template'][0]['displaytext']

  def getZoneName(self, id):
        rs = self.mycs.listZones(id=id)
        return rs['zone'][0]['name']

  def getNetName(self, id):
        rs = self.mycs.listNetworks(id=id)
        return rs['network'][0]['name']

  def getIP(self, id):
        rs = self.mycs.listNics(virtualmachineid=id)
        return rs['nic'][0]['ipaddress']

  def getuserquota(self, user):
      rs = self.mycs.listResourceLimits(account=user.username, domainid=user.domainid)
      for resource in rs['resourcelimit']:
          if (resource['resourcetype'] == "9"):
            return resource['max']

  def listjobs(self, user=None):
      response=[]
      for key, value in self.jobs.iteritems():
	  vm = defaultdict()
          if user != None and value[0] != user.username:
              continue
          vm['id'] = key
          vm['user'] = value[0]
          vm['zone'] = self.getZoneName(value[2])
          vm['template'] = self.getTemplName(value[3])
          vm['serv'] = self.getServOffName(value[4])
          vm['net'] = self.getNetName(value[5])
          vm['name'] = value[6]
          vm['start'] = value[7]
          vm['end'] = value[8]
          if datetime.datetime.now() > value[7]:
              vm['ip'] = value[12]
          response.append(vm.copy())

      return response

  def deployvm(self, account, domainid, serviceid, templateid, networkid, zoneid, name, uid):
    rs = self.mycs.deployVirtualMachine(serviceofferingid=serviceid, templateid=templateid, zoneid=zoneid, networkids=networkid, account=account, domainid=domainid, name=name, displayname=name)
    id = rs['id']
    self.jobs[uid].append(id)
    self.jobs[uid].append(self.getIP(id))

  def destroyvm(self, uid):
    vmid = self.jobs[uid][11]
    self.mycs.destroyVirtualMachine(id=vmid)
    del self.jobs[uid]

  def addvm(self, user, zone, template, service, network, name, startdate, enddate):
    uid=str(uuid.uuid4())
    username = copy(user.username)
    domainid = copy(user.domainid)

    self.jobs[uid].append(username)
    self.jobs[uid].append(domainid)
    self.jobs[uid].append(zone)
    self.jobs[uid].append(template)
    self.jobs[uid].append(service)
    self.jobs[uid].append(network)
    self.jobs[uid].append(name)
    self.jobs[uid].append(startdate)
    self.jobs[uid].append(enddate)

    deployljob = self.scheduler.add_job(self.deployvm,'date',run_date=startdate,kwargs={"account":username, "domainid":domainid, "serviceid":service, "templateid":template, "zoneid":zone, "networkid":network, "name":name, "uid":uid})
    destroyjob = self.scheduler.add_job(self.destroyvm, 'date', run_date=enddate, kwargs={"uid":uid})

    self.jobs[uid].append(deployljob.id)
    self.jobs[uid].append(destroyjob.id)

  def cancel(self, uid):
      if datetime.datetime.now() > self.jobs[uid][7]:
          self.scheduler.remove_job(self.jobs[uid][10])
          self.destroyvm(uid)
      else:
          self.scheduler.remove_job(self.jobs[uid][9])
          self.scheduler.remove_job(self.jobs[uid][10])
          del self.jobs[uid]

  def schedulevm(self, user, zone, template, service, network, name, startdate, enddate, duration):
      userquoata=self.getuserquota(user)
      vmmem=self.getServOffMem(service)
      while enddate - startdate >= duration:
          totalmemory=vmmem
          usermemory=vmmem
          for key, vm in self.jobs.iteritems():
              if vm[7] <= startdate + duration and vm[8] >= startdate:
                  totalmemory += self.getServOffMem(vm[4])
                  if user.username == vm[0]:
                    usermemory += self.getServOffMem(vm[4])
          if totalmemory <= self.maxmemory and usermemory <= userquoata:
              #print "DEBUG: Adding vm with name \"" + name + "\" to be created at " + str(startdate) + " and to be destroyed at " + str(startdate+duration)
              self.addvm(user, zone, template, service, network, name, startdate, startdate+duration)
              return 1
          startdate = startdate + duration + datetime.timedelta(minutes=15)
      return 0



ADMIN=1
USER=2
AUTHFAILURE=0

class User:

  username = None #The username of the user
  mycs = None #The Cloudstack api wrapper
  domainid = None #The domainid of the user
  usertype = None #The usertype of the user

  def auth(self, api_url, username, password):
    self.username = username
    myus = cs.UsernameSession()
    self.mycs = cs.CloudStack(api_url, myus)
    self.mycs.open(username=username, password=password)
    if myus.sessionkey != None:
        self.domainid = myus.domainid
        self.userid = myus.userid
        if myus.type == "0" :
            self.usertype = USER
            return True
        elif myus.type == "1" :
            self.usertype = ADMIN
            return True
        else:
            return False
    else:
        return False


  def listServOff(self):
    response=[]
    rs = self.mycs.listServiceOfferings()
    for sv in rs['serviceoffering']:
      response.append({'id':sv['id'],'name':sv['name']})
    return response

  def listTempl(self):
    response=[]
    rs = self.mycs.listTemplates(templatefilter="executable")
    for tm in rs['template']:
      response.append({'id':tm['id'],'name':tm['displaytext']})
    return response

  def listZones(self):
    response=[]
    rs = self.mycs.listZones()
    for tm in rs['zone']:
      response.append({'id':tm['id'],'name':tm['name']})
    return response

  def listNet(self):
    response=[]
    rs = self.mycs.listNetworks()
    for tm in rs['network']:
      response.append({'id':tm['id'],'name':tm['name']})
    return response
