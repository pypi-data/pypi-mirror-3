#!/usr/bin/python

import sys
import urllib
import urllib2
import re
import time
import memegrab
try:
  import simplejson
except ImportError:
  import json as simplejson #No speedups :(
  print 'You should install simplejson for faster parsing'
import os
from BeautifulSoup import BeautifulSoup

"""
(C) 2012, Kunal Mehta, under the MIT License

Syntax: python subdown.py subreddit[,subreddit] pages

"""


class Downloader:
  """
  Custom downloaders for different websites.
  Right now all traffic is directed through "Raw" which simply downloads the raw image file.
  """
  
  def __init__(self, reddit):
    self.help = "Sorry, %s doesn't work yet :("
    self.reddit = reddit
  def Imgur(self, link):
    if '.' in link.split('/')[-1]: #raw link but no i. prefix
      self.Raw(link)
      return
    html = self.page_grab(link)
    x = re.findall('<link rel="image_src" href="http://i.imgur.com/(.*?)" />', html)
    try:
      ilink = 'http://i.imgur.com/%s' %(x[0])
    except IndexError:
      print link
      return
    self.Raw(ilink)
  def Tumblr(self, link):
    print self.help %(link)
  def Raw(self, link):
    print 'Downloading %s' %(link)
    link = link.split('?')[0]
    filename = link.split('/')[-1]
    if filename == '':
      filename = 'lol.txt'
    try:
      img = self.page_grab(link)    
    except IOError,e:
      print 'IOError: %s' %(str(e))
      return
    f = open(self.reddit +'/'+ filename, 'w')
    f.write(img)
    f.close()
  def Twitter(self, link):
    print self.help %(link)
  def Pagebin(self, link):
    html = self.page_grab(link)
    x=re.findall('<img alt="(.*?)" src="(.*?)" style="width: (.*?)px; height: (.*?)px; " />', html)
    try:
      iimgur = x[0][1]
      self.Raw(iimgur)
    except KeyError:
      print "Can't parse pagebin.com HTML page :("
      print "Report %s a bug please!" %(link)
  def bolt(self, link):
    html = self.page_grab(link)
    x = re.findall('<img src="(.*?)"', html)
    try:
      imglink = x[0]
    except IndexError:
      print link
      return
    self.Raw(imglink)
  def qkme(self, link):
    memegrab.get_image_qm(memegrab.read_url(link), self.reddit+'/')
  def All(self, link):
    #verify it is an html page, not a raw image.
    open = urllib2.urlopen(link)
    headers = open.info().headers
    open.close()
    for header in headers:
      if header.lower().startswith('content-type'):
        #right header
        is_html = 'text/html' in header
    if not is_html: #means it is most likely an image
      self.Raw(link)
      return
    print 'Skipping %s since it is an HTML page.' %(link)
    return #Don't download html pages
    ### THIS FUNCTION IS NOT READY YET
    html = self.page_grab(link)
    soup = BeautifulSoup(html)
    imgs = soup.findAll('img')
    for img in imgs:
      try:
        url = img['src']
        self.Raw(url)
      except:
        pass
  def page_grab(self, link):
    obj = urllib.urlopen(link)
    html = obj.read()
    obj.close()
    return html



class Client:

  def __init__(self, name, pages):
    self.name = name
    self.headers = {
      'User-agent': 'subdown2 by /u/legoktm -- https://github.com/legoktm/subdown2'
    }
    self.pages = pages
    self.r = 'r/%s' %(self.name)
    print 'Starting %s' %(self.r)
    self.dl = Downloader(self.name)
    try:
      os.mkdir(self.name.lower())
    except OSError:
      pass
    
  def parse(self, page):
    print 'Grabbing page %s of %s from %s' %(page, self.pages, self.r)
    if page != 1:
      url = 'http://reddit.com/%s/.json?after=%s' %(self.r, self.after)
    else:
      url = 'http://reddit.com/%s/.json' %(self.r)
    req = urllib2.Request(url, headers=self.headers)
    obj = urllib2.urlopen(req)
    text = obj.read()
    obj.close()
    try:
      data = simplejson.loads(text)
    except simplejson.decoder.JSONDecodeError:
      print text
      sys.exit(1)
    try:
      self.after = data['data']['after']
      items = data['data']['children']
    except KeyError:
      try:
        if data['error'] == 429:
          print 'Too many requests on the reddit API, taking a break for a minute'
          time.sleep(60)
          self.parse(page)
          return
      except KeyError:
        print data    
        sys.exit(1)
    for item in items:
      item2 = item['data']
      #print item2
      if item2['domain'] == 'imgur.com':
        self.dl.Imgur(item2['url'])
      elif item2['domain'] == 'i.imgur.com':
        self.dl.Raw(item2['url'])
      elif item2['domain'] == 'twitter.com':
        self.dl.Twitter(item2['url'])
      elif item2['domain'] == 'pagebin.com':
        self.dl.Pagebin(item2['url'])
      elif 'media.tumblr.com' in item2['domain']:
        self.dl.Raw(item2['url'])
      elif 'self.' in item2['domain']:
        print 'Skipping self post: "%s"' %(item2['title'])
      elif (item2['domain'] == 'quickmeme.com') or (item2['domain'] == 'qkme.me'):
        self.dl.qkme(item2['url'])
      else: #Download all the images on the page
        self.dl.All(item2['url'])    
  def run(self):
    for pg in range(1,self.pages+1):
      self.parse(pg)


def main():
  subreddits = sys.argv[1]
  if len(sys.argv) == 3:
    pg = int(sys.argv[2])
  else:
    pg = 1
  for subreddit in subreddits.split(','):
    app = Client(subreddit,pg)
    app.run()

if __name__ == "__main__":
  main()