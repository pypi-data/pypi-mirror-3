#!/usr/bin/python
#reverse online md5 cracker by Dr@G 
#----------------------------------------------------------------------------------------------------------------
import urllib,re,sys
from re import search
from socket import *
#----------------------------------------------------------------------------------------------------------------
try:
    #------------------------------------------------------------------------------------------------------------
    user_hash= raw_input('Enter Hash:~# ')
    #------------------------------------------------------------------------------------------------------------
    print 'http://md5.gromweb.com/'
    readurl=urllib.urlopen('http://md5.gromweb.com/query/'+user_hash)
    response=readurl.read()
    print user_hash+'::'+ response
    #------------------------------------------------------------------------------------------------------------
    print 'http://md5.hashcracking.com/'
    readurl=urllib.urlopen('http://md5.hashcracking.com/search.php?md5='+user_hash)
    response=readurl.read()
    manipulated_response=response.split()
    mrid=len(manipulated_response)-1
    print user_hash+'::'+ manipulated_response[mrid]
    #------------------------------------------------------------------------------------------------------------
    print 'http://md5.thekaine.de/'
    readurl=urllib.urlopen('http://md5.thekaine.de/?hash='+user_hash)
    response=readurl.read()
    line=re.compile('<td colspan="2"><br><br><b>'+'\S+'+'\s+'+'\S+'+'\s+')
    found_s=line.search(response).group()
    password_=found_s[27:-25]
    print user_hash+'::'+ password_
    #------------------------------------------------------------------------------------------------------------
    print 'http://md5.my-addr.com/'
    values_p=urllib.urlencode({'md5':user_hash})
    readurl=urllib.urlopen("http://md5.my-addr.com/md5_decrypt-md5_cracker_online/md5_decoder_tool.php",values_p)
    response=readurl.read()
    line=re.compile('Hashed string'+'\S+'+'\s+'+'\S+'+'\s+'+'\S+')
    found_response=line.search(response).group()
    list_found_response=found_response.split()
    password_=list_found_response[2][:-6]
    print user_hash + '::' + password_
    #------------------------------------------------------------------------------------------------------------
    print 'http://md5.net/'
    values_p=urllib.urlencode({'hash':user_hash})
    readurl=urllib.urlopen("http://www.md5.net/cracker.php",values_p)
    response=readurl.read()
    match = search (r'<input type="text" id="hash" size="32" value="[^"]*"/>', response)
    password_=match.group().split('"')[7]
    print user_hash + '::' + password_
    #------------------------------------------------------------------------------------------------------------
    print 'http://hashchecker.com/'
    values_p=urllib.urlencode({'search_field':user_hash})
    readurl=urllib.urlopen("http://hashchecker.com/index.php?_sls=search_hash",values_p)
    response=readurl.read()
    line=re.compile('Your md5 hash is :'+'\S+'+'\s+'+'\S+'+'\s+'+'\S+')
    found_response=line.search(response).group()
    list_found_response=found_response.split()
    password_=list_found_response[6][3:-4]
    print user_hash + '::' + password_
    #------------------------------------------------------------------------------------------------------------
except:
    pass

    
