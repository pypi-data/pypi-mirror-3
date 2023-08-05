#Copyright (C) 2011  Mario Gallegos

#This file is part of mariosCrawler.

#mariosCrawler is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
        links = [ link [ 'href'] for link in soup_code . findAll ('a')
             if link . has_key ('href') ]
    except urllib2.URLError:
        if level==1:
            print "HTTP error bad URL, try again with another URL, example: http://www.twitter.com"
        return		
    except (HTMLParser.HTMLParseError,ValueError): 
        if level==1:
            print "HTTP error bad URL, try again with another URL, example: http://www.twitter.com"
        return  
    for link in links:
        if link.startswith("www"):
            link="http://"+link
        if link.startswith("//"):
            link="http:"+link
        else:    
            if not link.startswith("www") and not link.startswith("http"):
                if link.startswith("/"):
                    if url.endswith("/"):
                        link=url+link.replace('/', '', 1)
                    else:
                        link=url+link
                else:
                    if url.endswith("/"):
                        link=url+link
                    else:
                        link=url+"/"+link
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
