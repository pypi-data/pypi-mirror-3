 #! /usr/bin/python
 # -*- coding: utf-8 -*-
import urllib2
import argparse
import HTMLParser
from BeautifulSoup import BeautifulSoup as Soup

def getLinks(level,asterisks,url):
 try:
  raw_code = _opener . open (url).read()
  soup_code = Soup ( raw_code )
  links = [ link [ 'href'] for link
   in soup_code . findAll ('a')
   if link . has_key ('href') ]
 except urllib2.URLError:
  if level==1:
   print "HTTP error bad URL, try again with another URL"
  return		
 except (HTMLParser.HTMLParseError,ValueError): 
  return  
 for link in links:
  print asterisks+" "+link
  if level<deep:
   getLinks(level+1,asterisks+'*',link)
      
parser = argparse . ArgumentParser ( description = "Web crawler arguments" )
parser . add_argument ( 'url' , nargs =1 ,help = 'target URL')
parser . add_argument ( '-n' ,'--number-of-levels' , type = int , default =1 , help = 'How deep the craaaawl will go')
args = parser . parse_args()
target_url = args.url.pop()
deep=args.number_of_levels

user_agent = " Mozilla /5.0 ( X11 ; U ; Linux x86_64 ; en - US ) AppleWebKit /534.7 ( KHTML , like Gecko ) Chrome/7.0.517.41 Safari /534.7"
_opener = urllib2 . build_opener ()
_opener . addheaders = [( 'User - agent' , user_agent ) ]
getLinks(1,"*",target_url)
