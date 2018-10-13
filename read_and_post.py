#!/usr/bin/env python
import sys
import requests
import RPi.GPIO as gpio
import Adafruit_DHT
import re
import json
import time, datetime
from pprint import pprint
 
if __name__ == "__main__":
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(26, gpio.OUT)
    gpio.output(26, True)
	 
    # Parse command line parameters.
    sensor_args = { '11': Adafruit_DHT.DHT11,
                    '22': Adafruit_DHT.DHT22,
                    '2302': Adafruit_DHT.AM2302 }
    if len(sys.argv) == 5 and sys.argv[1] in sensor_args:
        sensor = sensor_args[sys.argv[1]]
        pin = sys.argv[2]
        host = sys.argv[3]
        api_key = sys.argv[4]
               
    else:
        print 'usage: sudo ./read_and_post.py [11|22|2302] GPIOpin#'
        print 'example: sudo ./read_and_post.py 2302 4 - Read from an AM2302 connected to GPIO #4'
        sys.exit(1)
 
    http_lead = re.compile("\Ahttps?://")
    if not http_lead.match(host):
        raise ValueError("Must specify application protocol")
 
    route = host + "/api/v1/readings"
 

    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    #convert to farenheit
    temperature = temperature * 9/5 + 32
 
    # Note that sometimes you won't get a reading and
    # the results will be null (because Linux can't
    # guarantee the timing of calls to read the sensor).  
    # If this happens try again!
    payload = {'reading':{'humidity':float(humidity), 'temperature':float(temperature)}}
    data = json.dumps(payload)
    headers = {'X-Api-Key':api_key, 'Content-Type':'application/json'}
 
    if humidity is not None and temperature is not None:
    
        try:
            r = requests.post(route, data=data, headers=headers, verify=False)
            print "{0}\tT:{1:.2f}F\tH:{2:.2f}\t@ {3}".format(r.status_code, temperature, humidity, datetime.datetime.now())
        except:         
            print "POST to {0} failed, trying again soon".format(host)
            raise
 
