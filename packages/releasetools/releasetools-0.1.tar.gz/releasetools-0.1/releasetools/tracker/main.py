import sys

from ..common import getConfig, saveConfig, optionsbase

progname = 'tracker'

def main():
    optionsbase.add_option('-r', '--release', dest='release',
                           action='store', type='string',
                           help='Check this version of the project', metavar='PROJECT')
    
    config = getConfig(progname)
    if 'type' not in config:
        print "Error: missing tracker type in " + config['config'] + ". Aborting."
        sys.exit(1)

    if 'release' not in config or not config['release']:
        print "Error: missing --release. Aborting."
        sys.exit(3)
        
    modname = 'releasetools.tracker.'+config['type']
    trackertop = __import__(modname, globals(), locals(), [], -1)
    tracker = sys.modules[modname]
    try:
        tracker.init(config)
    except Exception as e:
        print str(e)
        print "Tracker initialization failed. Aborting."
        sys.exit(2)

    tickets = tracker.getOpenTickets(config)
    if len(tickets) > 0:
        print "Total open tickets for this release: %d" % (len(tickets))
        for ticket in tickets:
            print "%5d : %s" % (ticket['ticket_num'], ticket['summary'])

        print "Will not proceed with closing old release."
        sys.exit(4)

    saveConfig(config, progname)
