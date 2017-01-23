#!/bin/python

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, escape, jsonify
from datetime import *
import sys
sys.path.append('../backend/libs/')
from schcs import *

s = Scheduler("./config.ini")
api_url = s.api_url

sess = defaultdict()

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
# set the secret key.  keep this really secret:
app.secret_key = 'test'

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('listvms'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        u = User()
        login = u.auth(api_url,username,password)
        if login == True:
            session['username'] = request.form['username']
            sess[username] = u
            flash('You were logged in')
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    flash('You were logged out')
    return redirect(url_for('index'))

@app.route('/newvm',  methods=['GET', 'POST'])
def newvm():
  if 'username' in session:

    username = session['username']
    u = sess[username]

    if request.method == 'POST':
        serv = request.form['service']
        temp = request.form['template']
        zone = request.form['zone']
        name = request.form['vmname']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        duration = request.form['duration']
        start_time = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
        end_time = datetime.datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
        duration_time = datetime.timedelta(minutes = int(duration))

        res = s.schedulevm(u, zone, temp, serv, name, start_time, end_time, duration_time)
        if res == 0:
            flash("Failed to find slot to schedule VM")
        return redirect(url_for('index'))

    else:
        serv = u.listServOff()
        temp = u.listTempl()
        zon = u.listZones()

        return render_template('newvm.html', serv=serv, temp=temp, zon=zon, now=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"))
  else:
    return redirect(url_for('login'))

@app.route('/listvms',  methods=['GET', 'POST'])
def listvms():
    if 'username' in session:
        username = session['username']
        u = sess[username]
        usertype = u.usertype
        if request.method == 'POST':
            id = request.form['id']
            s.cancel(id)
            return redirect(url_for('listvms'))
        elif usertype == ADMIN:
            jobs = s.listjobs()
        elif usertype == USER:
            jobs = s.listjobs(u)
        return render_template('listvms.html', jobs=jobs, usertype=usertype)
    else:
        return redirect(url_for('login'))

@app.route('/data')
def return_data():
    if 'username' in session:
        username = session['username']
        u = sess[username]
        usertype = u.usertype
        if usertype == ADMIN:
            jobs = s.listjobs()
        elif usertype == USER:
            jobs = s.listjobs(u)

        calendardata = []
        for vm in jobs:
            if  usertype == ADMIN:
                vmname = "[" + vm['user'] + "] " + vm['name']
            else:
                vmname = vm['name']
            event = {'title':vmname, 'start':vm['start'], 'end':vm['end'] }
            calendardata.append(event)
        return jsonify(calendardata)
    else:
        return redirect(url_for('login'))
