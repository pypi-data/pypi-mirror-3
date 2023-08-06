from optparse import OptionParser

def parse():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("--get-events", action="store_true", dest="getevents",
                      help="show events")
    parser.add_option("--create-event", action="store_true", dest="createevent",
                      help="create an event")
    parser.add_option("--close-event", dest="closeevent",
                      help="close an event by event id")
    parser.add_option("--event-filter", dest="eventfilter",
                      help="set an event filter")
    parser.add_option("--display-filter", dest="displayfilter",
                      help="set a display filter")
    parser.add_option("--create-event-filter", dest="createeventfilter",
                      help="set a create event filter")
    (options, args) = parser.parse_args()
    return options 
