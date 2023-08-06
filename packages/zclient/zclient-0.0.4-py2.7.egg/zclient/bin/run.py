#!/usr/bin/env python

import os
import sys
from zclient import settings
from zclient import options
from zclient.zenoss import filters
from zclient.zenoss.api import ZenossAPI

def main():
	conf_file = os.path.expanduser('~/.zclient')
	all_settings = settings.getall(conf_file)
	all_options = options.parse()
	if all_options.getevents:
		events = get_events(all_settings, all_options.eventfilter)
		for e in filters.events_display(events, get_props(all_settings, all_options.displayfilter)): print e
		quit()
	if all_options.createevent:
		event_result = create_event(all_settings, get_props(all_settings, all_options.createeventfilter))
		if event_result['result']['success'] is True:
			print event_result['result']['msg']
		else:
			print 'Failed to create event: ' + event_result['result']['msg']
		quit()
	if all_options.closeevent:
		print close_event(all_settings, all_options.closeevent)
		quit()

def get_props(all_settings, prop):
	retval = None
	if prop:
		try:
			retval = all_settings[prop]
		except KeyError:
			fail('The property ' + prop + ' does not exist') 
	return retval

def close_event(all_settings, event_id):
	try:
		z = ZenossAPI(all_settings['zenosslogin'])
	except KeyError:
		fail('The property zenosslogin is required') 
	return z.close_event_on_event_id(event_id)
		
def create_event(all_settings, all_filters):
	try:
		z = ZenossAPI(all_settings['zenosslogin'])
	except KeyError:
		fail('The property zenosslogin is required') 
	try:
		return z.create_event_on_device(all_filters)
	except KeyError:
		fail('A create event filter is required when creating an event') 

def get_events(all_settings, eventfilter=None):
	all_filters = get_props(all_settings, eventfilter)
	try:
		z = ZenossAPI(all_settings['zenosslogin'])
	except KeyError:
		fail('The property zenosslogin is required') 
	return z.get_events(all_filters)

def fail(msg):
	print 'Error: ' + msg
	sys.exit(1)

if __name__ == "__main__":
    main()
