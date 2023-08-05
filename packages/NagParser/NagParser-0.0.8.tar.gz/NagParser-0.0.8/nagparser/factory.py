#!/usr/bin/env python

import re
from Nag import Nag
from NagList import NagList

def parse(config):
    tempobjs = []
    
    files = config.files
    importantservicegroups = config.IMPORTANTSERVICEGROUPS
    
    nag = None

    for filename in files:
        tempfile = open(filename)
        content = tempfile.read()
        tempfile.close()
        
        if nag == None:
            nag = Nag()
        
        sectionsnames = ['hoststatus', 'servicestatus', 'programstatus', 'define servicegroup']
        for section in sectionsnames:
            pat = re.compile(section +' \{([\S\s]*?)\}', re.DOTALL)
    
            for sectioncontent in pat.findall(content):
                if section == 'hoststatus': 
                    temp = Nag.Host(nag)
                elif section == 'servicestatus': 
                    temp = Nag.Service(nag)
                elif section == 'programstatus':
                    temp = nag
                elif section == 'define servicegroup':
                    temp = Nag.ServiceGroup(nag)
                
                for attr in sectioncontent.splitlines():
                    attr = attr.strip()
                    if len(attr) == 0 or attr.startswith('#'):
                        pass
                    else:
                        if section == 'define servicegroup':
                            delim = '\t'
                        else:
                            delim = '='

                        shortattr = attr.split(delim)[0].lower()
                        value = attr.replace(shortattr+delim, '')
                        temp.__dict__[shortattr] = value
                tempobjs.append(temp)
    
    hosts = filter(lambda x: isinstance(x, Nag.Host), tempobjs)
    services = filter(lambda x: isinstance(x, Nag.Service), tempobjs)
    servicegroups = filter(lambda x: isinstance(x, Nag.ServiceGroup), tempobjs)

    nag.importantservicegroups = importantservicegroups
    nag.config = config
    
    if len(hosts):
        nag.hosts = NagList(hosts)
    if len(services):
        nag.services = NagList(services)
    if len(servicegroups):
        nag._servicegroups = NagList(servicegroups)

    return nag


if __name__ == "__main__":
    pass