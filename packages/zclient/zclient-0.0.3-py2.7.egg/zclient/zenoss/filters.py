import sys

def events_display(events, displayfilter):
	retlist = []
	for event in events['events']:
		retdict = {}
		for k, v in sorted(event.iteritems()):
	 		for df_k, df_v in sorted(displayfilter.iteritems()):
				if k.lower() == df_k:
					if df_v == 'True':
						retdict[k] = v
					elif v.find(df_v) >= 0:
						retdict[k] = v
		retlist.append(retdict)
	return retlist
