#!/usr/bin/env python
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
from snurtle.cmd2      import options, make_option
from clibundle import CLIBundle

ROUTE_LIST_TEMPLATE = '''<%
    singleton = 'NO'
    routegroup = report['name']
    preserve = 'NO'
    for prop in report['_PROPERTIES']:
         if prop['propertyname'] == '{http://www.opengroupware.us/oie}preserveAfterCompletion':
	     preserve = prop['value']
         elif prop['propertyname'] == '{http://www.opengroupware.us/oie}singleton':
             singleton = prop['value']
         elif prop['propertyname'] == '{http://www.opengroupware.us/oie}routeGroup':
             routegroup = prop['value']
%>${report['objectId']} ${report['name']} [singleton="${singleton}" routeGroup="${routegroup}" preservationEnabled="${preserve}"]'''

class RouteCLIBundle(CLIBundle):

#    @options([make_option('--delegated', action='store_true',  help=''),
#              make_option('--archived', action='store_true', help='')])          
    def do_list_routes(self, arg, opts=None):
        '''List available OIE routes'''
        if self.server_ok():  
            callid = self.server.search_for_objects(entity='Route',
                                                    criteria='list',
                                                    detail=16,
                                                    callback=self.callback)
            response = self.get_response(callid)
            if response:
                self.set_result(response, template=ROUTE_LIST_TEMPLATE)   
