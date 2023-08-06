#
# Copyright 2010-2012 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
#
#
# Corporation of Balclutha DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL Corporation of Balclutha BE LIABLE FOR
# ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
import urlparse
import Products.ZenModel.RRDDataSource as RRDDataSource
from Products.ZenModel.ZenPackPersistence import ZenPackPersistence
from AccessControl import Permissions
from Products.ZenUtils.Utils import binPath

class DataSourceBase(ZenPackPersistence, RRDDataSource.RRDDataSource):
    """
    A command-plugin that calls munin-based Zope-agents on remote
    instance via wget

    This base class needs instantiations with munin_plugins, and uri 
    attributes
    """
    ZOPE_MONITOR = 'ZopeMonitor'
    ZENPACKID = 'ZenPacks.lbn.ZopeMonitor'

    sourcetypes = ('COMMAND', ZOPE_MONITOR,)
    sourcetype = 'COMMAND'

    eventClass = '/Status/Zope'
        
    zopeURI = '${here/zZopeURI}'
    timeout = 60
    parser = 'ZenPacks.lbn.ZopeMonitor.parsers.Munin'

    _properties = RRDDataSource.RRDDataSource._properties + (
        {'id':'zopeURI',    'type':'string', 'mode':'w'},
        {'id':'timeout',    'type':'int',    'mode':'w'},
        )
        
    _relations = RRDDataSource.RRDDataSource._relations + (
        )


    factory_type_information = ( 
    { 
        'immediate_view' : 'editZopeMonitorDataSource',
        'actions'        :
        ( 
            { 'id'            : 'edit',
              'name'          : 'Data Source',
              'action'        : 'editZopeMonitorDataSource',
              'permissions'   : ( Permissions.view, ),
            },
        )
    },
    )


    def __init__(self, id, title=None, buildRelations=True):
        RRDDataSource.RRDDataSource.__init__(self, id, title, buildRelations)
        #self.addDataPoints()


    def getDescription(self):
        """ DEBUGSTR """
        return '@@munin.zope.plugins/%s' % self.uri


    def useZenCommand(self):
        return True


    def getCommand(self, context):
        """ use curl to read munin.zope plugins on stdout """

        return RRDDataSource.RRDDataSource.getCommand(self, context, 
                                                      'curl %s/@@munin.zope.plugins/%s' % (self.zopeURI, self.uri))


    def checkCommandPrefix(self, context, cmd):
        return cmd


    def addDataPoints(self):
        for tag in self.munin_tags:
            if not hasattr(self.datapoints, tag):
                self.manage_addRRDDataPoint(tag)

    def zmanage_editProperties(self, REQUEST=None):
        '''validation, etc'''
        if REQUEST:
            # ensure default datapoint didn't go away
            self.addDataPoints()
            # and eventClass
            if not REQUEST.form.get('eventClass', None):
                REQUEST.form['eventClass'] = self.__class__.eventClass
        return RRDDataSource.RRDDataSource.zmanage_editProperties(self, REQUEST)





