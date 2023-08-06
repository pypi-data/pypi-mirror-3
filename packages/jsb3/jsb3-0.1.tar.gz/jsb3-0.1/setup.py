#!/usr/bin/env python3
#
#

target = "jsb3" # BHJTW change this to /var/cache/jsb on debian

import os

try: from setuptools import setup
except: print("i need setuptools to properly install JSB3") ; os._exit(1)

upload = []

def uploadfiles(dir):
    upl = []
    if not os.path.isdir(dir): print("%s does not exist" % dir) ; os._exit(1)
    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if not os.path.isdir(d):
            if file.endswith(".pyc"):
                continue
            upl.append(d)
    return upl

def uploadlist(dir):
    upl = []

    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if os.path.isdir(d):   
            upl.extend(uploadlist(d))
        else:
            if file.endswith(".pyc"):
                continue
            upl.append(d)

    return upl

setup(
    name='jsb3',
    version='0.1',
    url='http://jsb3.googlecode.com/',
    download_url="http://code.google.com/p/jsb3/downloads", 
    author='Bart Thate',
    author_email='bthate@gmail.com',
    description='JSONBOT 3 on Python 3',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    scripts=['bin/jsb3',
             'bin/jsb3-irc'],
    packages=['jsb3',
              'jsb3.lib', 
              'jsb3.drivers',
              'jsb3.drivers.console',
              'jsb3.drivers.irc',
              'jsb3.utils',
              'jsb3.plugs',
              'jsb3.plugs.core',
           ],
    long_description = """ To get it right ;] """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Communications :: Chat',
        'Topic :: Software Development :: Libraries :: Python Modules'],
)
