import xml.dom.minidom as xml
import types
from datetime import datetime
import time

import os 

from nicetime import getnicetimefromdatetime, getdatetimefromnicetime
from inspect import isclass

class NagDefinition(object):
    '''TODO: insert doc string here'''
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    STALE_THRESHOLD = 240       #Should be set to Nagios check timeout or the longest time in seconds a check might take
    IGNORE_STALE_DATA = False
    NAGIOS_CMD_FILE = '/var/lib/nagios3/rw/nagios.cmd'
    APIKEY = None
    
    def getnowtimestamp(self):
        return time.time()
        
    def __init__(self, nag = None):
        if nag == None:
            self.nag = self
        else:
            self.nag = nag
    
    @property
    def attributes(self):
        '''Returns a list of tuples with each tuple representing an attribute'''

        output = []
        for attr in self.__dict__:
            attrtype = type(self.__dict__[attr])
            if attrtype != types.ListType and not issubclass(attrtype, NagDefinition):
                t = attr, self.__dict__[attr]
                output.append(t)
        return output
    
    
    def getbad(self, objtype, items = None):
        if items == None:
            return filter(lambda x: int(x.__dict__['current_state']) > 0, getattr(self, self.classname(objtype)+'s'))
        else:
            return filter(lambda x: int(x.__dict__['current_state']) > 0, items)
        
    def getbadservices(self):
        return filter(lambda x: x.status[0] != 'ok', self.services)
        #return self.getbad(Nag.Service, self.services)

    def classname(self, classname = None):
        if classname:
            classbase = classname
        else:
            classbase = self.__class__
        
        parts = str(classbase).split("'")[1].lower().split('.')
        return parts[len(parts)-1]

    def genoutput(self, outputformat = 'xml', returnxmlstring = True, 
                  recursive = True, items = [], isservicegroup = False):
        
        selfclassname = self.classname()
        outputformat = outputformat.lower()
        
        #Setup
        output = {}
        if outputformat == 'xml':
            doc = xml.Document()
            output = doc.createElement(selfclassname)
        elif outputformat == 'json':
            output['objtype'] = selfclassname
            output['attributes'] = {}
            
        if isservicegroup == False and selfclassname == 'servicegroup':
            isservicegroup = True

        #Attributes
        for attr in self.attributes:
            if outputformat == 'xml':
                output.setAttribute(attr[0], attr[1])
            if outputformat == 'json':
                output['attributes'][attr[0]] = attr[1]
        
        order = ['host', 'service', 'servicegroup']
        if recursive:
            if items == []:
                if order[0] == selfclassname: 
                    items = getattr(self, order[1]+'s')
                else:
                    if isservicegroup:
                        items = getattr(self, order[1]+'s')
                    else:
                        try:
                            items = getattr(self, order[0]+'s')
                            #items.extend(getattr(self, order[2]+'s')) # Disabled until I get the servicegroup logic working correctly
                        except Exception:
                            pass
                        
        if isservicegroup and selfclassname == 'service':
            items = [getattr(self, order[0])]

        for obj in items:
            temp = obj.genoutput(recursive = True, outputformat = outputformat, 
                                 returnxmlstring = False, isservicegroup = isservicegroup)
            if outputformat == 'xml':
                output.appendChild(temp)
            if outputformat == 'json':
                if obj.classname() + 's' not in output.keys():
                    output[obj.classname() + 's'] = []
                output[obj.classname() + 's'].append(temp)
                
        if returnxmlstring and outputformat == 'xml':
            output = 'XML output is broken, sorry, try JSON its good for you'
            #output.toprettyxml(indent = '  ')
            
        return output
    
    def getobj(self, objtype, value, attribute = 'host_name', first = False):
        objs = filter(lambda x: x.__dict__[attribute.lower()] == value, getattr(self, self.classname(objtype)+'s'))
        
        if first:
            if objs:
                return objs[0]
            else:
                return None
        else:
            return objs
        
    def getservice(self, service_description):
        return self.getobj(objtype = Nag.Service, value = service_description, 
                           attribute = 'service_description', first = True)

    def scheduledowntime(self, author, starttime, endtime, comment, apikey = None, doappend = False):
          
        TIMEFORMAT = '%Y%m%d%H%M'
        try:
            start = int(time.mktime(time.strptime(starttime, TIMEFORMAT)))
        except Exception:
            try:
                start = int(time.mktime(getdatetimefromnicetime(starttime).timetuple()))
            except Exception:
                return 'Error: "StartTime" not in correct format.'
            
        try:
            end = int(time.mktime(time.strptime(endtime, TIMEFORMAT)))
        except Exception:
            try:
                end = int(time.mktime(getdatetimefromnicetime(endtime, datetime.fromtimestamp(start)).timetuple()))
            except Exception:
                return 'Error: "EndTime" not in correct format.'
            
        values = {'fixed': 1, 'trigger_id': 0, 'duration': 0, 'author': author, 
                  'start_time': start, 'end_time': end, 'comment': comment}
        
        if self.classname() == 'servicegroup':
            values['servicegroup_name'] = self.servicegroup_name
            command = 'SCHEDULE_SERVICEGROUP_SVC_DOWNTIME;<servicegroup_name>;<start_time>;<end_time>;<fixed>;<trigger_id>;<duration>;<author>;<comment>'
        elif self.classname() == 'host':
            values['host_name'] = self.host_name
            command = 'SCHEDULE_HOST_SVC_DOWNTIME;<host_name>;<start_time>;<end_time>;<fixed>;<trigger_id>;<duration>;<author>;<comment>'
        elif self.classname() == 'service':
            values['host_name'] = self.host_name
            values['service_description'] = self.service_description
            command = 'SCHEDULE_SVC_DOWNTIME;<host_name>;<service_description>;<start_time>;<end_time>;<fixed>;<trigger_id>;<duration>;<author>;<comment>'
        else:
            return 'Error: Invalid Nag object'

        for value in values:
            command = command.replace('<' + value + '>', str(values[value]))
        
        if command.find('<') > 0:
            return 'Error: Incomplete Nagios command file format substitution '
        
        command = '[' + str(int(time.time())) + '] ' + command
        
        if doappend:
            try:
                if self.nag.APIKEY == None or apikey not in self.nag.APIKEY:
                    return 'Error: Invalid or Missing API Key.  A valid API Key is required to do a POST.'
                else:
                    commandfile = os.open(self.NAGIOS_CMD_FILE, os.O_RDWR | os.O_NONBLOCK)
                    os.write(commandfile, command + '\n')
                    os.close(commandfile)
            except Exception, e:
                print e
                return 'Error: Appending to the Nagios command file'
        
        return command
    
class Nag(NagDefinition):
    '''TODO: insert doc string here'''
    
    name = ''
    
    @property
    def lastupdated(self):
        return datetime.fromtimestamp(float(self.last_command_check))
    
    def gethost(self, host_name):
        return self.getobj(objtype = Nag.Host, value = host_name, attribute = 'host_name', first = True)
    
    def getservicegroup(self, servicegroup_name):
        return self.getobj(objtype = Nag.ServiceGroup, value = servicegroup_name, attribute = 'servicegroup_name', first = True)
    
    def getbadhosts(self):
        return self.getbad(Nag.Host)
    
    def laststatuschange(self, returntimesincenow = True):
        lastchange = max(self.services, key=lambda x: x.laststatuschange(returntimesincenow = False)).laststatuschange(returntimesincenow = False)
        
        if returntimesincenow:
            return getnicetimefromdatetime(lastchange)
        else:
            return lastchange
    
    def getservicegroups(self, onlyimportant = False):
        if onlyimportant:
            return filter(lambda x: x.servicegroup_name in self.importantservicegroups, self._servicegroups)
        else:
            return self._servicegroups
    
    @property
    def servicegroups(self):
        return self.getservicegroups()
    
    class Host(NagDefinition):
        '''TODO: insert doc string here'''
        
        @property
        def services(self):
            return filter(lambda x: x.host_name == self.host_name, self.nag.services)
        
        @property
        def name(self):
            return self.host_name

        
        def laststatuschange(self, returntimesincenow = True):
            lastchange = max(self.services, key=lambda x: x.laststatuschange(returntimesincenow = False)).laststatuschange(returntimesincenow = False)
            
            if returntimesincenow:
                return getnicetimefromdatetime(lastchange)
            else:
                return lastchange
        
    class Service(NagDefinition):        
        '''TODO: insert doc string here'''
        @property
        def host(self):
            host = filter(lambda x: x.host_name == self.host_name, self.nag.hosts)
            if len(host):
                host = host[0]
            return host
        
        
        @property
        def name(self):
            return self.service_description
        
        @property
        def status(self):
            isdowntime = False
            if int(self.scheduled_downtime_depth) > 0: isdowntime = True
            
            if ((time.time() - self.STALE_THRESHOLD) > int(self.next_check) and 
                self.active_checks_enabled == '1' and 
                self.IGNORE_STALE_DATA == False):
                return 'stale', isdowntime
            if int(self.current_state) == 2:
                return 'critical', isdowntime
            if int(self.current_state) == 1:
                return 'warning', isdowntime
            if int(self.current_state) > 2 or int(self.current_state) < 0:
                return 'unknown', isdowntime
            return 'ok', isdowntime

        def laststatuschange(self, returntimesincenow = True, timestamp = None):
            if timestamp:
                lastchange = datetime.fromtimestamp(float(timestamp))
            else:
                lastchange = datetime.fromtimestamp(float(self.last_state_change))
            
            if returntimesincenow:
                return getnicetimefromdatetime(lastchange)
            else:
                return lastchange
        
    class ServiceGroup(NagDefinition):
        @property
        def services(self):
            tempservices = []
            
            members = self.members.split(',')
            for i in range(len(members)):
                if i % 2 == 0:
                    tempservices.append(self.nag.gethost(members[i]).getservice(members[i+1]))

            return tempservices

        @property
        def name(self):
            return self.alias

        @property
        def status(self):
            if len(filter(lambda x: x.status[0] == 'stale', self.services)):
                return 'unknown'
            
            if len(filter(lambda x: int(x.current_state) == 2 and
                                    int(x.scheduled_downtime_depth) == 0, 
                                        self.services)):
                return 'critical'
            
            if len(filter(lambda x: int(x.current_state) == 1 and
                                    int(x.scheduled_downtime_depth) == 0, 
                                        self.services)):
                return 'warning'
            
            if len(filter(lambda x: int(x.scheduled_downtime_depth) > 0 and
                                    int(x.current_state) != 0, 
                                        self.services)):
                return 'downtime'
            
            if len(filter(lambda x: x.status[0] == 'unknown' or 
                          x.status[0] == 'stale', self.services)):
                return 'unknown'
            return 'ok'
        
        def laststatuschange(self, returntimesincenow = True):
            lastchange = max(self.services, key=lambda x: x.laststatuschange(returntimesincenow = False)).laststatuschange(returntimesincenow = False)
            
            if returntimesincenow:
                return getnicetimefromdatetime(lastchange)
            else:
                return lastchange

if __name__ == "__main__":
    pass
