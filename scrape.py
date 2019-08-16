import socket
import numpy
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import os
import sys


if not os.path.exists(os.getcwd() + '/demos'):
    os.makedirs(os.getcwd() + '/demos')

os.chdir(os.getcwd() + '/demos')

origpath = os.getcwd()

url = 'http://qtvapi.quakeworld.nu/api/v1/servers'

response = requests.get(url)

json_response = response.json()
list_of_servers = []
list_of_urls = []

for o in json_response['Servers'][0]['GameStates']:
    if o['IpAddress'] not in list_of_servers:
        list_of_servers.append(o['IpAddress'])

scount = 0

for s in list_of_servers:
    scount += 1
    total_bytes = sum(
        os.path.getsize(os.path.join(dirpath, filename)) for dirpath, dirnames, filenames in os.walk(origpath) for
        filename in filenames)
    if total_bytes >= 30000000000:
        print('30GB reached')
        sys.exit()
    else:
        print('Working on server ' + s + ' (' + (str)(scount) + '/' + (str)(
            len(list_of_servers)) + ')' + ' - total downloaded ' + (str)(
            numpy.ceil((total_bytes / (1024 * 1024)))) + ' MiB')
    try:
        response = requests.get('http://' + s + ':28000/demos', timeout=5)
    except TimeoutError:
        continue;
    except socket.error:
        continue;
    soup = BeautifulSoup(response.text, "html.parser")

    for t in soup.find_all('a'):
        link = t['href']
        if '.mvd' in link and \
                'watch.qtv' not in link and \
                    (link.startswith('/dl/demos/2on2') or
                     link.startswith('/dl/demos/4on4')):
            if link.startswith('/dl/demos/2on2'):
                mode = '2on2'
            else:
                mode = '4on4'

            if 'dm2' in link:
                map_name = 'dm2'
            if 'dm3' in link:
                map_name = 'dm3'
            if 'dm4' in link:
                map_name = 'dm4'
            if 'dm6' in link:
                map_name = 'dm6'
            if 'e1m2' in link:
                map_name = 'e1m2'
            if 'aerowalk' in link:
                map_name = 'aerowalk'
            if 'ztndm3' in link:
                map_name = 'ztndm3'
            if map_name:
                url = urllib.parse.unquote('http://' + s + ':28000' + link)
                list_of_urls.append((url, mode, map_name, s))
                map_name = ''
olds = ''
scount = 0
for t in list_of_urls:
    url = t[0]
    mode = t[1]
    map_name = t[2]
    s = t[3]
    if not os.path.exists(os.getcwd() + '/' + mode + '/' + map_name):
        os.makedirs(os.getcwd() + '/' + mode + '/' + map_name)
    os.chdir(os.getcwd() + '/' + mode + '/' + map_name)
    if os.path.exists(os.getcwd() + '/' + url.split('/')[-1]):
        print("File " + os.getcwd() + '/' + url.split('/')[-1] + " exists, skipping.")
        if olds != s:
            print('Next server: ' + s + ' - total downloaded ' + (str)(
                numpy.ceil((total_bytes / (1024 * 1024)))) + ' MiB')
        os.chdir(origpath)
        olds = s
        continue
    try:
        myfile = requests.get(url, timeout=5)
    except TimeoutError:
        continue;
    except socket.error:
        continue;
    open(url.split('/')[-1], 'wb').write(myfile.content)
    # fname = wget.download(url, bar=None)
    print(os.getcwd() + '/' + url.split('/')[-1] + ' (' + (str)(list_of_urls.index(t)) + '/' + (str)(len(list_of_urls))
          + ') ' + '-> Working on ' + s + ' (' + (str)(list_of_servers.index(s)) + '/' + (str)(len(list_of_servers)) + ')'
          )
    time.sleep(0.5)
    os.chdir(origpath)

    total_bytes = sum(
        os.path.getsize(os.path.join(dirpath, filename)) for dirpath, dirnames, filenames in os.walk(origpath) for
        filename in filenames)
    if total_bytes >= 30000000000:
        print('30GB reached')
        sys.exit()
    if olds != s:
        print('Next server: ' + s + ' - total downloaded ' + (str)(
            numpy.ceil((total_bytes / (1024 * 1024)))) + ' MiB')
    olds = s
