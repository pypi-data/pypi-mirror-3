#  nexodyne.py
#  
#  Copyright 2012 ahmed youssef <xmonader@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  


__author__ = "Ahmed Youssef"
__all__ = ['Nexodyne']

from sys import argv
import urllib as ulib
import urllib2 as ulib2

try: 
    import BeautifulSoup as bs
except ImportError, e:
    print "-requires BeautifulSoup" #Fixme [use regular expressions] 
    exit(1)

def get_post_response(data, url):
    """
        Sends a POST to <url> with encoded <data {field:value}>
    """
    assert (isinstance(data, dict) and isinstance(url, str))
    try:
        data=ulib.urlencode(data)
        return ulib2.urlopen(url, data).read()
    except Exception, ex:
        return None

def get_email_icons(src):
    soup=bs.BeautifulSoup(src)
    for addr in soup.findAll('address'):
        yield addr.text
        
def get_options(src):
    soup=bs.BeautifulSoup(src)
    domains={}
    exts={}
    for select in soup.findAll("select"):
        if select.get('name')=='domain':
            for domain in select.findAll('option'):
                domains[domain.text]=domain.get('value')
        elif select.get('name')=='ext':
            for ext in select.findAll('option'):
                exts[ext.text]=ext.get('value')
    return {'domains':domains, 'exts': exts }
        

class Nexodyne(object):
    URL='http://services.nexodyne.com/email/index.php' 
    
    def __init__(self):
        self._email=None
        self._mail=None
        self._domain=None
        self._ext=None
        self._domains={}
        self._exts={}
        self.get_options()

    
    def set_email(self, email):
        self._email=email
        mail, afterat=email.split("@")
        lastdot=afterat.rfind(".")
        domain=afterat[:lastdot]
        ext=afterat[lastdot:]
        
        self._set_mail(mail)
        self._set_domain(domain)
        self._set_ext(ext)
        
    def get_email_icon(self):
        if not self._email: raise ValueError
        g=get_email_icons(get_post_response({'mail':self._mail, 'domain':self._domain, 'ext': self._ext }, Nexodyne.URL)) 
        return g.next()
        
    def _set_mail(self, mail):
        self._mail=mail
        
    def get_options(self):
        src=ulib2.urlopen(Nexodyne.URL).read()
        d=get_options(src)
        self._domains=d['domains']
        self._exts=d['exts']
        
    def _set_domain(self, domain):
        valid_domain=None
        for k in self._domains.keys():
            if k.upper()==domain.upper():
                valid_domain=k
                break
                
        if valid_domain is None:
            raise ValueError(domain+' is not in ' +str(self._domains.keys()))
        
        self._domain=valid_domain
        
    def _set_ext(self, ext):
        valid_ext=None
        for k in self._exts.keys():
            if k.upper()==ext.upper():
                valid_ext=k
                break
        if valid_ext is None:
            raise ValueError(ext+ ' is not in ' + str(self._exts.keys()))
    
        self._ext=valid_ext
        
    def __str__(self):
        return self._email

def console_main():
    n=Nexodyne()
    email='someone@gmail.com'
    if len(argv)>1:
        for e in argv[1:]:
            n.set_email(e)
            print n.get_email_icon()
    else:
        n.set_email(email)
        print n.get_email_icon()
        
if __name__=="__main__":
    console_main()
