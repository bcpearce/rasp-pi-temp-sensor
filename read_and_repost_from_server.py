#!/usr/bin/env python
import sys
import requests
import re
import json
import time, datetime
from pprint import pprint

def check_protocol(function):
    def wrapper(host, *args, **kwargs):
        http_lead = re.compile("\Ahttps?://")
        if not http_lead.match(host):
            raise ValueError("Must specify application protocol in host: {0}".format(host))
        return(function(host, *args, **kwargs))
    return wrapper

@check_protocol
def read_from_host(host, route=""):
    r = requests.get(host + route)
    if r.status_code == 200:
        return json.loads(r.text)
    return False

@check_protocol
def post_to_host(host, reading, api_key, route="/api/v1/readings"):
 
    if reading['humidity'] is not None and reading['temperature'] is not None:

        payload = {'reading':{'humidity':float(reading['humidity']), 'temperature':float(reading['temperature'])}}
        data = json.dumps(payload)
        headers = {'X-Api-Key':api_key, 'Content-Type':'application/json'}
    
        try:
            r = requests.post(host + route, data=data, headers=headers, verify=False)
            print "{0}\tT:{1:.2f}F\tH:{2:.2f}\t@ {3}".format(r.status_code, reading['temperature'], reading['humidity'], datetime.datetime.now())
        except:         
            print "POST to {0} failed".format(host)
            raise

 
if __name__ == "__main__":
     
    # Parse command line parameters.
    if len(sys.argv) == 4:
        host1 = sys.argv[1]
        host2 = sys.argv[2]
        api_key = sys.argv[3]
               
    else:
        print "ERROR: invalid input options"
        print 'usage: ./read_and_repost_from_server.py [source host] [dest host] [api_key]'
        print 'example: sudo ./read_and_post.py http://192.168.1.10 https://192.168.1.11 my_secret_key - Read from 192.168.1.10 and post to 192.168.1.11 with my_secret_key as the api_key'
        sys.exit(1)

    # make the reading from first host
    reading = read_from_host(host1)

    # post to second host
    if reading:
        post_to_host(host2, reading, api_key)
        print 
