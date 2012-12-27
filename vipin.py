#!/usr/bin/env python

from PIL import Image,ImageEnhance,ImageFilter
import sys, urllib2, os, errno, shutil, glob, argparse, cookielib, urllib
from StringIO import StringIO
from time import sleep
from zipfile import ZipFile, is_zipfile
from svm import *
from svmutil import *
import chasvm

loginUrl='http://www.vipin.us/login.do'
imageCodeUrl='http://www.vipin.us/imagecode.jsp?v=login'

successfulUrl='http://www.vipin.us/home.do'
configFileUrl='http://www.vipin.us/download-mac.do?xtag=en'

tblk=os.path.expanduser("~") + '/Library/Application Support/Tunnelblick/Configurations/%s.tblk/Contents/Resources/'
tblkConfigs=['US-speed', 'US-stable', 'optimized']

def getUrlOpener():
  cookie = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie), urllib2.HTTPHandler())
  opener.addheaders = [('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:18.0) Gecko/20100101 Firefox/18.0')]
  return opener

def crackImgCode(opener):
  captchaImg = StringIO(opener.open(imageCodeUrl).read())
  imgcode = chasvm.predict(captchaImg, 'vipin.m')
  return imgcode

def login(username, password, opener=getUrlOpener()):
  data = urllib.urlencode({'user.username': username, 'user.password': password, 'imgcode': crackImgCode(opener)})
  print data
  home = opener.open(loginUrl, data)
  if(home.geturl() != successfulUrl):
    print 'cannot login: ' + home.geturl()
    sleep(1)
    opener.close
    login(username, password, getUrlOpener())
  print "successful logined"
  return opener  

def downloadAndExtractConfigFileIntoTunnelblickResource(opener):
  config = opener.open(configFileUrl).read()
  zipfile = ZipFile(StringIO(config)) 
  resc = {name: zipfile.read(name) for name in zipfile.namelist()}
  for name in resc:
    basename, ext = os.path.splitext(name)
    if ext == '.ovpn':
      writeToFile('config.ovpn', [tblk % basename], resc[name])
      if (basename == 'US-speed'):
        writeToFile('config.ovpn', [tblk % 'optimized'], resc[name])
    else:
      writeToFile(name,[tblk % t for t in tblkConfigs], resc[name])
  opener.close()

def writeToFile(filename, dirs, content):
  for d in dirs:
    file = open(d + filename, 'w')
    print 'Writing %s file...' % file.name
    file.write(content)
    file.close()

def parseArgs():
  parser = argparse.ArgumentParser(description='Extract vipin.us openvpn port from config file')
  parser.add_argument('-u', '--username', dest='username', action='store', default='', help='username')
  parser.add_argument('-p', '--password', dest='password', action='store', default='', help='password')

  args = parser.parse_args()
  if args.username and not args.password:
    print >> sys.stderr, "Password required when username is specified"
    sys.exit(1)
  return args

def main():
  args = parseArgs()
  opener = login(args.username, args.password)
  downloadAndExtractConfigFileIntoTunnelblickResource(opener)

if __name__ == '__main__':
  main()
