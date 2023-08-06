import json
import urllib
import urllib2

ROUTERS = { 'MessagingRouter': 'messaging',
			'EventsRouter': 'evconsole',
			'ProcessRouter': 'process',
			'ServiceRouter': 'service',
			'DeviceRouter': 'device',
			'NetworkRouter': 'network',
			'TemplateRouter': 'template',
			'DetailNavRouter': 'detailnav',
			'ReportRouter': 'report',
			'MibRouter': 'mib',
			'ZenPackRouter': 'zenpack' }

class ZenossAPI():
	def __init__(self, login, debug=False):
		"""
		Initialize the API connection, log in, and store authentication cookie
		"""
		# Use the HTTPCookieProcessor as urllib2 does not save cookies by default
		self.urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
		if debug: self.urlOpener.add_handler(urllib2.HTTPHandler(debuglevel=1))
		self.reqCount = 1
		self.login = login

		# Contruct POST params and submit login.
		loginParams = urllib.urlencode(dict(
						__ac_name = self.login['username'],
						__ac_password = self.login['password'],
						submitted = 'true',
						came_from = self.login['url'] + '/zport/dmd'))
		self.urlOpener.open(self.login['url'] + '/zport/acl_users/cookieAuthHelper/login',
							loginParams)

	def _router_request(self, router, method, data=[]):
		if router not in ROUTERS:
			raise Exception('Router "' + router + '" not available.')

		# Contruct a standard URL request for API calls
		req = urllib2.Request(self.login['url'] + '/zport/dmd/' +
							  ROUTERS[router] + '_router')

		# NOTE: Content-type MUST be set to 'application/json' for these requests
		req.add_header('Content-type', 'application/json; charset=utf-8')

		# Convert the request parameters into JSON
		reqData = json.dumps([dict(
					action=router,
					method=method,
					data=data,
					type='rpc',
					tid=self.reqCount)])

		# Increment the request count ('tid'). More important if sending multiple
		# calls in a single request
		self.reqCount += 1

		# Submit the request and convert the returned JSON to objects
		return json.loads(self.urlOpener.open(req, reqData).read())

	def get_devices(self, deviceClass='/zport/dmd/Devices', limit=50):
		return self._router_request('DeviceRouter', 'getDevices',
									data=[{'uid': deviceClass,
										   'params': {} }])['result']

	def get_devices_by_name_filter(self, name, deviceClass='/zport/dmd/Devices', limit=50):
		return self._router_request('DeviceRouter', 'getDevices',
									data=[{'uid': deviceClass,
										   'params': {'name': name} }])['result']

	def get_graph_defs(self, uid, drange=129600):
		return self._router_request('DeviceRouter', 'getGraphDefs', data=[{'uid': uid, 'drange': drange}])['result']

	def get_rrd_value(self, uid, dsname, drange=129600):
		return self._router_request('DeviceRouter', 'getRRDValue', data=[{'uid': uid, 'dsname': dsname, 'drange': drange}])['result']

	def get_events(self, event_filter=None):
		data = dict(start=0, limit=100, dir='DESC', sort='severity')
		data['params'] = dict(device=None, component=None, eventClass=None, severity=[5,4,3,2], eventState=[0,1])
		if event_filter:
			for k, v in event_filter.iteritems():
				try:
					data['params'][k] = v
				except KeyError:
					pass

		return self._router_request('EventsRouter', 'query', [data])['result']

	def add_device(self, deviceName, deviceClass):
		data = dict(deviceName=deviceName, deviceClass=deviceClass)
		return self._router_request('DeviceRouter', 'addDevice', [data])

	def get_templates(self, id):
		data = dict(id=id)
		return self._router_request('DeviceRouter', 'getTemplates', [data])

	def get_unbound_templates(self, uid):
		data = dict(uid=uid)
		return self._router_request('DeviceRouter', 'getUnboundTemplates', [data])

	def set_bound_templates(self, uid, templateIds):
		data = dict(uid=uid, templateIds=templateIds)
		return self._router_request('DeviceRouter', 'setBoundTemplates', [data])

	def get_graphs(self, uid):
		data = dict(uid=uid)
		return self._router_request('TemplateRouter', 'getGraphs', [data])

	def get_graph_points(self, uid):
		data = dict(uid=uid)
		return self._router_request('TemplateRouter', 'getGraphPoints', [data])

	def create_event_on_device(self, event_filter):
		data = dict(device=None, summary='Event created by zclient', severity='Critical',
					component='', evclasskey='', evclass='')
		for k, v in event_filter.iteritems():
			try:
				data[k] = v
			except KeyError:
				pass
		if data['severity'] not in ('Critical', 'Error', 'Warning', 'Info', 'Debug', 'Clear'):
			raise Exception('Severity "' + data['severity'] +'" is not valid.')
		if data['device'] is None:
			raise Exception('A device must be specified when creating an event.')

		return self._router_request('EventsRouter', 'add_event', [data])

	def close_event_on_event_id(self, event_id):
		data = dict(evids=[event_id], limit=1)
		data['params'] = dict(severity=[5,4,3,2,1,0], eventState=[0,1,2,3,4,6])
		return self._router_request('EventsRouter', 'close', [data])
