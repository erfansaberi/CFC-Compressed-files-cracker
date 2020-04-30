import os
import config
import subprocess
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
)
import time
import shutil
import signal

app = Flask(__name__)
app.config.update(SECRET_KEY='12345678')
pids = []
endtime = 0
startedprocesses = []
processes = config.PROCESSES
runningprocesses = 0
done = 0
found = False
foundpass = 0
passwordsnum = 0
working = False
ptime = 'Not Started'
@app.route('/')
def home():
    global done, found, foundpass, processes, passwordsnum, working, time, endtime, startedprocesses
    if found:
        status = 'found'
    else:
        if done >= runningprocesses and runningprocesses != 0:
            status = 'notfound'
        elif working:
            status = 'working'
        else:
            status = 'offline'
            totalprogress = 0
    totalprogress = 0
    totalprogressmustbe = 0
    for process in startedprocesses:
        totalprogressmustbe += 100
        if process['numpasses'] != 0:
            process['progress'] = int(process['done'])/int(process['numpasses'])*100
            if process['progress'] != 0:
                format(process['progress'], '.2f')
            totalprogress += process['progress']
        if status == 'working':
            dones = int(process['done'])
            if dones != int(process['numpasses']):
                nowtime = process['until']
                passedtime = int(nowtime - endtime)
                if passedtime != 0:
                    speed = dones / passedtime #test per seconds
                    process['time'] = str(int(dones * speed))+' seconds remaining'
                else:
                    process['time'] = 'Starting'
            else:
                process['time'] = 'Finished'
        else:
                process['time'] = 'Finished'
    if totalprogress and totalprogressmustbe and not found:
        totalprogress = format(totalprogress/totalprogressmustbe * 100, '.2f')
    elif found:
        totalprogress = 100
    print(startedprocesses)
    return render_template('index.html',data={'status':status,'password':foundpass,'done':done,'processes':startedprocesses,'numprocesses':runningprocesses,'passwordsnum':passwordsnum,'totalprogress':totalprogress})


@app.route('/crack')
def crack():
    global done, foundpass, found, working, endtime, runningprocesses
    runningprocesses = 0
    working = True
    found = False
    done = 0
    passpath = request.args.get('passpath')
    if passpath:
        pass
    else:
        flash('Error in receiving password list path','danger')
        working = False
        return redirect('/')

    try:
        passwordlist = open(passpath,'r')
        passwordlist.close()
    except:
        flash('Password List not found','danger')
        working = False
        return redirect('/')
    
    zippath = str(request.args.get('zippath'))
    try:
        with open(zippath,'r') as e:
            flash('Compressed file loaded','success')
    except Exception as e:
        print(e)
        flash('Compressed file not found','danger')
        working = False
        return redirect('/')
    try:
        if splitpasslist(str(passpath)):
            flash('Password list has been loaded','success')
        else:
            flash('Error in spliting passlist','danger')
            return redirect('/')
    except:
        flash('Error in spliting passlist','danger')
        working = False
        return redirect('/')
    try:
        if os.path.splitext(zippath)[1] == '.zip':
            for i in range(processes):
                pro = subprocess.Popen(["python", "app.py", f'./lists/list{i}.txt', zippath, str(i)])
                proid = pro.pid
                print(f'Process {i} Started with pid {proid}')
                pids.append(proid)
        elif os.path.splitext(zippath)[1] == '.rar':
            for i in range(processes):
                pro = subprocess.Popen(["python", "app.py", f'./lists/list{i}.txt', zippath, str(i)])
                proid = pro.pid
                print(f'Process {i} Started with pid {proid}')
                pids.append(proid)

    except Exception as e:
        working = False
        print(e)
        flash('Error','danger')
        flash(f'{e}','danger')
        return redirect('/')

    flash('Extraction started','info')
    endtime = time.time()
    return redirect('/')

@app.route('/wait')
def wait():
    return render_template('wait.html')

@app.route('/recieve')
def recieve():
    global done, working, found, foundpass, startedprocesses
    if request.args.get('status') == 'extracted':
        done += 1
        found = True
        foundpass = request.args.get('password')
        working = False
        for process in startedprocesses:
            if process['processid'] == request.args.get('processid'):
                process['progress'] = 100
                process['found'] = True
                print(process)
                for pid in pids:
                    try:
                        os.kill(pid,signal.SIGTERM)
                    except:
                        print('Problem in killing process {pid}, please click on exit to kill all processes')
                break
    else:
        done += 1
        for processes in startedprocesses:
            if processes['processid'] == request.args.get('processid'):
                processes['progress'] = 100
                break
    return 'ok'   
    

def splitpasslist(passpath):
    global processes, passwordsnum, runningprocesses
    try:
        if os.path.exists('./lists') and os.path.isdir('./lists'):
            shutil.rmtree('./lists')
            os.mkdir('./lists')
        else:
            os.mkdir('./lists')
    except:
        print('error in creating directory')
    lines = 0
    with open(passpath,'r') as passfile:
        for line in passfile:
            lines += 1
    passwordsnum = lines
    linesperfile = int(lines / processes) + 1
    passlist = open(passpath,'r')
    try:
        for i in range(processes):
            if lines > 0:
                with open(f'./lists/list{i}.txt','w+') as filepass:
                    runningprocesses += 1
                    for i in range(0,linesperfile):
                        try:
                            filepass.write(passlist.readline())
                        except:
                            break
                    lines -= linesperfile
            if lines < linesperfile:
                linesperfile = lines
        return 1
    except Exception as e:
        print(e)
        return 0

@app.route('/errors')
def errors():
    errors = request.args.get('error')
    print(errors) 
    return 'ok'   

@app.route('/progress')
def progress():
    global startedprocesses
    now = time.time()
    for process in startedprocesses:
        if process['processid'] == request.args.get('processid'):
            process['done'] = request.args.get('testedpasswords')
            process['until'] = now
            break
    return 'ok'
@app.route('/start')
def start():
    global startedprocesses
    now = time.time()
    try:
        startedprocesses.append({'processid':request.args.get('processid'),'numpasses':request.args.get('numpasswords'),'done':0,'progress':0,'time':'not calculated','until':now})
    except Exception as e:
        flash('error')
        print(e)
    return 'ok'

app.run('localhost', 5000, debug=True)