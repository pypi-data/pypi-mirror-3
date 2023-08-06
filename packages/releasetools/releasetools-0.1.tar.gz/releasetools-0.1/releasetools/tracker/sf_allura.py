"""
Following the documentation here: http://sourceforge.net/p/forge/documentation/API%20-%20Beta/
"""
import json
import urlparse
import webbrowser

import certifi
import oauth2

def init(config):
    if 'consumer_key' not in config and 'consumer_secret' not in config:
        raise Exception("""consumer_key and consumer secret must be set in %s
Read http://sourceforge.net/p/forge/documentation/API%%20-%%20Beta/ for
details on obtaining them.""" % (config['config']))

    if 'oauth_token' not in config or 'oauth_token_secret' not in config:
        getOauthToken(config)

def getOauthToken(config):
    CONSUMER_KEY = config['consumer_key']
    CONSUMER_SECRET = config['consumer_secret']
    REQUEST_TOKEN_URL = 'https://sourceforge.net/rest/oauth/request_token'
    AUTHORIZE_URL = 'https://sourceforge.net/rest/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://sourceforge.net/rest/oauth/access_token'

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    client = oauth2.Client(consumer)
    client.ca_certs = certifi.where()

    resp, content = client.request(REQUEST_TOKEN_URL, 'GET')
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urlparse.parse_qsl(content))
    
    webbrowser.open("%s?oauth_token=%s" % (
            AUTHORIZE_URL, request_token['oauth_token']))
    
    oauth_verifier = raw_input('What is the PIN? ')
    
    token = oauth2.Token(request_token['oauth_token'],
                         request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    client = oauth2.Client(consumer, token)
    client.ca_certs = certifi.where()
    
    resp, content = client.request(ACCESS_TOKEN_URL, "GET")
    access_token = dict(urlparse.parse_qsl(content))

    config['oauth_token'] = access_token['oauth_token']
    config['oauth_token_secret'] = access_token['oauth_token_secret']

def getOpenTickets(config):
    
    URL_BASE='http://sourceforge.net/rest/'

    consumer = oauth2.Consumer(config['consumer_key'], config['consumer_secret'])
    access_token = oauth2.Token(config['oauth_token'], config['oauth_token_secret'])
    client = oauth2.Client(consumer, access_token)
    client.ca_certs = certifi.where()

    url = URL_BASE + 'p/' + config['project'] + '/tickets'
    resp, content = client.request(url)
    tickets = json.loads(str(content))

    ret_tickets = []
    for ticket in tickets['tickets']:
        resp, content = client.request(url + '/' + str(ticket['ticket_num']))
        data = json.loads(content)
        tvals = data['ticket']
        if ('custom_fields' in tvals and '_milestone' in tvals['custom_fields']
            and tvals['custom_fields']['_milestone'] == config['release']
            and tvals['status'] not in ['closed', 'wont-fix', 'duplicate']):
            ret_tickets.append(ticket)

    return ret_tickets
