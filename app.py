from zipfile import ZipFile
from rarfile import RarFile
import os
import sys
import requests
numpasswords = 0

def crackzip(filepath,passwd):
    i = 0
    with ZipFile(filepath, 'r') as zipObj:
        for password in passwd:
            i += 1
            try:
                zipObj.extractall(path='./extractedfile', members=None, pwd=password.rstrip('\n').encode())
                print('\n===================')
                print('zip file extracted!')
                print('===================\n')
                requests.get(f'http://localhost:5000/recieve?status=extracted&password={password}&processid={processid}')
                return ''
            except:
                pass
            try:
                if i%20 == 0:
                    requests.get(f'http://localhost:5000/progress?processid={processid}&numpasswords={numpasswords}&testedpasswords={i}')
            except Exception as e:
                requests.get(f'http://localhost:5000/errors?error={e}')
        requests.get('http://localhost:5000/recieve?status=failed')
        requests.get(f'http://localhost:5000/progress?processid={processid}&numpasswords={numpasswords}&testedpasswords={i}')


def crackrar(filepath,passwd):
    i = 0
    with RarFile(filepath,'r') as rarObj:
        for password in passwd:
            i += 1
            try:
                rarObj.extractall(path='./extractedfile', members=None, pwd=password.rstrip('\n'))
                print('\n===================')
                print('rar file extracted!')
                print('===================\n')
                requests.get(f'http://localhost:5000/recieve?status=extracted&password={password}&processid={processid}')
                return ''
            except:
                pass
            try:
                if i%20 == 0:
                    requests.get(f'http://localhost:5000/progress?processid={processid}&numpasswords={numpasswords}&testedpasswords={i}')
            except Exception as e:
                requests.get(f'http://localhost:5000/errors?error={e}')
        requests.get('http://localhost:5000/recieve?status=failed')
        requests.get(f'http://localhost:5000/progress?processid={processid}&numpasswords={numpasswords}&testedpasswords={i}')

def getnumpasswords(passpath):
    num = 0
    with open(passpath,'r') as passlist:
        for line in passlist:
            num += 1
    return num


try:
    zippath = sys.argv[2]
    passpath = sys.argv[1]
    processid = sys.argv[3]
    if os.path.splitext(zippath)[1] == '.zip':
        numpasswords = getnumpasswords(passpath)
        requests.get(f'http://localhost:5000/start?processid={processid}&numpasswords={numpasswords}')
        passwd = open(passpath)
        crackzip(zippath,passwd)
        passwd.close()
    elif os.path.splitext(zippath)[1] == '.rar':
        numpasswords = getnumpasswords(passpath)
        requests.get(f'http://localhost:5000/start?processid={processid}&numpasswords={numpasswords}')
        passwd = open(passpath)
        crackrar(zippath,passwd)
        passwd.close()
except Exception as e:
    requests.get(f'http://localhost:5000/errors?error={e}')