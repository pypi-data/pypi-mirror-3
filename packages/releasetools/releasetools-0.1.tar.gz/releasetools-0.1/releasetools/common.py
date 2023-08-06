import ConfigParser
import os

from optparse import OptionParser

defaultconfig = os.path.expanduser('~/.releasetools')
optionsbase=OptionParser()
optionsbase.add_option('-f', '--config', dest='config',
                       action='store', type='string', default=defaultconfig,
                       help='Use this configuration file', metavar='FILE')
optionsbase.add_option('-p', '--project', dest='project',
                       action='store', type='string',
                       help='Work on this project', metavar='PROJECT')

def getConfig(progname, options=optionsbase):
    (opts, args) = options.parse_args()
    
    config = ConfigParser.ConfigParser()
    config.read(opts.config)
    
    if opts.project:
        progname = '%s:%s' % (progname, opts.project)
        
    retvals = {}
    if config.has_section(progname):
        for opt in config.options(progname):
            retvals[opt] = config.get(progname, opt)
    optnames = filter(lambda x: not x.startswith('_') and not x in ['ensure_value', 'read_file', 'read_module'], dir(opts))
    for opt in optnames:
        retvals[opt] = getattr(opts, opt)

    return retvals

def saveConfig(config, progname):
    if config['project']:
        progname = '%s:%s' % (progname, config['project'])
        
    configfile = ConfigParser.ConfigParser()
    configfile.read(config['config'])
    if not configfile.has_section(progname):
        configfile.add_section(progname)

    optnames = filter(lambda x: x not in ['project', 'config'], config.keys())
    for opt in optnames:
        configfile.set(progname, opt, config[opt])

    with open(config['config'], 'wb') as configfp:
        configfile.write(configfp)
    
