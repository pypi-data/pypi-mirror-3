import types
from datetime import datetime
import time
import pprint

from NagCommands import NagCommands
from NagList import NagList

from nicetime import getnicetimefromdatetime, getdatetimefromnicetime
from inspect import isclass

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

cache_opts = {
    'cache.type': 'memory',
    'cache.regions': 'short_term',
    'cache.enabled': True,
    'cache.short_term.expire': '15'
}
cache = CacheManager(**parse_cache_config_options(cache_opts))
class NagDefinition(object):
    '''This is the base class that all other 'Nag' objects inherit.  This class defines common functions and should not be directly instantiated. '''    
    def getnowtimestamp(self):
        return time.time()
        
    def __init__(self, nag = None):
        if nag == None:
            self.nag = self
            self._nagcreated=datetime.now()
        else:
            self.nag = nag
            
    @property
    def commands(self):
        return NagCommands(self)
    
    @property
    def attributes(self):
        '''Returns a list of tuples with each tuple representing an attribute'''
        
        output = []
        for attr in self.__dict__:
            attrtype = type(self.__dict__[attr])
            if attrtype is not types.ListType and attrtype is not NagList and not issubclass(attrtype, NagDefinition):
                t = self.__dict__[attr]
                try:
                    t = int(str(t))
                except ValueError:
                    try:
                        t = float(str(t))
                    except ValueError:
                        pass
            
                output.append((attr, t))

        return output
    
    def getbad(self, objtype, items = None):
        if items == None:
            return NagList([x for x in getattr(self, self.classname(objtype)+'s') if int(x.__dict__['current_state']) > 0])
        else:
            return NagList([x for x in items if int(x.__dict__['current_state']) > 0])
        
    def getbadservices(self):
        return NagList([x for x in self.services if x.status[0] != 'ok'])

    def classname(self, classname = None):
        if classname:
            classbase = classname
        else:
            classbase = self.__class__
        
        parts = str(classbase).split("'")[1].lower().split('.')
        return parts[len(parts)-1]

    def genoutput(self, outputformat = 'json', items = [], finaloutput = True, prittyprint = False):
        outputformat = outputformat.lower()
        
        #Setup
        output = {}
        if outputformat == 'json':
            output['objtype'] = self.classname()
            output['attributes'] = {}
        else:
            return 'Invalid Output'

        #Attributes
        for attr in self.attributes:
            if outputformat == 'json':
                if attr[1] is None:
                    output['attributes'][attr[0]] = 'none'
                else:
                    output['attributes'][attr[0]] = attr[1]
        
        order = ['host', 'service', 'servicegroup']
        if items == []:
            if order[0] == self.classname(): 
                items = getattr(self, order[1]+'s')
            else:
                try:
                    items = getattr(self, order[0]+'s')
                except Exception:
                    pass
                    
        for obj in items:
            temp = obj.genoutput(outputformat = outputformat, finaloutput = False)
            if outputformat == 'json':
                if obj.classname() + 's' not in output.keys():
                    output[obj.classname() + 's'] = []
                output[obj.classname() + 's'].append(temp)
            
        if finaloutput:
            if outputformat == 'json':
                if prittyprint:
                    output = pprint.PrettyPrinter().pformat(output)
            
        return output
    
    def getobj(self, objtype, value, attribute = 'host_name'):
        return NagList([x for x in getattr(self, self.classname(objtype)+'s') if x.__dict__[attribute.lower()] == value])
        
    def getservice(self, service_description):
        #return self.getobj(objtype = Nag.Service, value = service_description, attribute = 'service_description').first
        try:
            return getattr(self.services, service_description)
        except AttributeError:
            return None
    
    def gethost(self, host_name):
        #return self.getobj(objtype = Nag.Host, value = host_name, attribute = 'host_name').first
        #return NagList([x for x in self.hosts if x.name == host_name]).first
        try:
            return getattr(self.hosts, host_name)
        except AttributeError:
            return None
    
    def getservicegroup(self, servicegroup_name):
        #Note: Using NagList to get the object an attribute is not possible because servicegroups set their name attribute 
        # to their alias which is not an identifier of a unique service group (unlike Host and Service which are)
        return self.getobj(objtype = Nag.ServiceGroup, value = servicegroup_name, attribute = 'servicegroup_name').first

class Nag(NagDefinition):
    '''Top level object that 'holds' all the other objects like Services and Hosts.  The child Nag Objects are defined here so a Host is of type Nag.Host.'''
    
    name = ''
    
    @property
    def lastupdated(self):
        return datetime.fromtimestamp(float(self.last_command_check))
    
    def getbadhosts(self):
        return self.getbad(Nag.Host)
    
    def laststatuschange(self, returntimesincenow = True):
        lastchange = max(self.services, key=lambda x: x.laststatuschange(returntimesincenow = False)).laststatuschange(returntimesincenow = False)
        
        if returntimesincenow:
            return getnicetimefromdatetime(lastchange)
        else:
            return lastchange
    
    def getservicegroups(self, onlyimportant = False):
        @cache.region('short_term', '_getservicegroups{0}'.format(self.nag._nagcreated))
        def _getservicegroups(onlyimportant = onlyimportant):
            
            if onlyimportant:
                servicegroups = NagList([x for x in self._servicegroups if x.servicegroup_name in self.importantservicegroups])
            else:
                servicegroups = self._servicegroups
                
                '''Build up a servicegroup instance that will have all services NOT in a servicegroup'''
                noservicegroup = Nag.ServiceGroup()
                noservicegroup.alias = 'No Service Group'
                noservicegroup.nag = self.nag
                noservicegroup.servicegroup_name = 'noservicegroup'
                noservicegroup.members = ''
                
                servicesinservicegroup = []
                for servicegroup in self._servicegroups:
                    servicesinservicegroup.extend(servicegroup.services)
                
                for services in list(set(self.services) - set(servicesinservicegroup)):
                    noservicegroup.members = noservicegroup.members + services.host.host_name + ',' + services.name + ','
                    
                noservicegroup.members = noservicegroup.members.strip(',')
                servicegroups.append(noservicegroup)
                
                '''Build "allservices" sudo servicegroup'''
                allservicesservicegroup = Nag.ServiceGroup()
                allservicesservicegroup.alias = 'All Services'
                allservicesservicegroup.nag = self.nag
                allservicesservicegroup.servicegroup_name = 'allservices'
                allservicesservicegroup.members = ''
                
                for services in self.services:
                    allservicesservicegroup.members = allservicesservicegroup.members + services.host.host_name + ',' + services.name + ','
                    
                allservicesservicegroup.members = allservicesservicegroup.members.strip(',')
                servicegroups.append(allservicesservicegroup)
                
                servicegroups = NagList(servicegroups)
                    
            return servicegroups
    
        return _getservicegroups(onlyimportant)
    
    @property
    def servicegroups(self):
        return self.getservicegroups()
    
    class Host(NagDefinition):
        '''Host represents a host definition found in status.dat.'''

        @property
        def services(self):
            return NagList([x for x in self.nag.services if x.host_name == self.host_name])
        
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
        '''Service represents a service definition found in status.dat'''

        @property
        def host(self):
            #@cache.region('short_term', '_getservicehost{0}{1}'.format(self.name, self.nag._nagcreated))
            def _getservicehost():
                return NagList([x for x in self.nag.hosts if x.host_name == self.host_name]).first
        
            return _getservicehost()
        @property
        def name(self):
            return self.service_description
        
        @property
        def status(self):
            isdowntime = False
            if int(self.scheduled_downtime_depth) > 0: isdowntime = True
            if ((time.time() - self.nag.config.STALE_THRESHOLD) > int(self.next_check) and 
                self.active_checks_enabled == '1' and 
                self.nag.config.IGNORE_STALE_DATA == False):
                return 'stale', isdowntime
            
            #@cache.region('short_term', '_getservicestatus{0}{1}'.format(self.name,self.nag._nagcreated))
            def _getservicestatus():
                if self.nag.config.REQUIRE_HARD_SERVICE_STATUS and int(self.state_type) != 1:
                    return 'ok', isdowntime
                if int(self.current_state) == 2:
                    return 'critical', isdowntime
                elif int(self.current_state) == 1:
                    return 'warning', isdowntime
                elif int(self.current_state) > 2 or int(self.current_state) < 0:
                    return 'unknown', isdowntime
                else:
                    return 'ok', isdowntime

            return _getservicestatus()

        def laststatuschange(self, returntimesincenow = True, timestamp = None):
            if timestamp:
                lastchange = datetime.fromtimestamp(float(timestamp))
            else:
                lastchange = datetime.fromtimestamp(float(self.last_state_change))
            
            if returntimesincenow:
                return getnicetimefromdatetime(lastchange)
            else:
                return lastchange
            
        @property
        def servicegroups(self):
            servicegroups = []
            for servicegroup in self.nag.getservicegroups():
                if self in servicegroup.services:
                    servicegroups.append(servicegroup)
            return NagList(servicegroups)
        
    class ServiceGroup(NagDefinition):
        '''ServiceGroup represents a service group definition found in objects.cache.'''
        
        def gethostsandservices(self):
            @cache.region('short_term', '_gethostsandservices{0}{1}'.format(self.servicegroup_name, self.nag._nagcreated))
            def _gethostsandservices():
                tempservices = []
                temphosts = []
                if 'members' in self.__dict__.keys() and self.members != '':
                    members = self.members.split(',')
                    for i in range(len(members)):
                        if i % 2 == 0:
                            host = self.nag.gethost(members[i])
                            if host not in temphosts:
                                temphosts.append(host)
                            tempservices.append(host.getservice(members[i+1]))
                            
                return (tempservices,temphosts)
            
            return _gethostsandservices()
        
        @property
        def services(self):
            return NagList(self.gethostsandservices()[0])
        
        @property
        def hosts(self):
            return  NagList(self.gethostsandservices()[1])

        @property
        def name(self):
            return self.alias
        
        @property
        def status(self):
            if len([x for x in self.services if x.status[0] == 'stale']):
                 return 'unknown'
            
            #@cache.region('short_term', '_getservicegroupstatus{0}{1}'.format(self.servicegroup_name, self.nag._nagcreated))
            def _getservicegroupstatus():
                if len([x for x in self.services if x.status[0] == 'critical' and x.status[1] == False]):
                     return 'critical'

                elif len([x for x in self.services if x.status[0] == 'warning' and x.status[1] == False]):
                     return 'warning'

                elif len([x for x in self.services if x.status[0] == 'ok' and x.status[1] == True]):
                     return 'downtime'

                elif len([x for x in self.services if x.status[0] == 'unknown' or x.status[0] == 'stale']):
                     return 'unknown'
                else:
                     return 'ok'
            
            return _getservicegroupstatus()
        
        def laststatuschange(self, returntimesincenow = True):
            lastchange = max(self.services, key=lambda x: x.laststatuschange(returntimesincenow = False)).laststatuschange(returntimesincenow = False)
            
            if returntimesincenow:
                return getnicetimefromdatetime(lastchange)
            else:
                return lastchange

if __name__ == "__main__":
    pass