from cmd2      import options, make_option
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
