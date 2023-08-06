#!/usr/bin/env python
#
#

target = "boty" # BHJTW change this to /var/cache/jsb on debian

import os

try: from setuptools import setup
except: print "i need setuptools to properly install BOTY" ; os._exit(1)

upload = []

def uploadfiles(dir):
    upl = []
    if not os.path.isdir(dir): print "%s does not exist" % dir ; os._exit(1)
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
    name='boty',
    version='0.1',
    url='http://boty.googlecode.com/',
    download_url="http://code.google.com/p/boty/downloads", 
    author='Bart Thate',
    author_email='bthate@gmail.com',
    description='Time Flies',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    scripts=['bin/boty',],
    packages=['boty',],
    long_description = """ -=- always wanted to be a bird -=- """,
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
    requires=['jsb', ]
)
