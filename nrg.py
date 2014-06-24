#!/usr/bin/env python
''' NagiosReportGenerator - Generate HTML status report

TODO: Write desc

Copyright (c) 2014 digIT 14/15
'''

import os
import sys
from optparse import OptionParser
import requests
from requests.auth import HTTPBasicAuth

nagios_status = {2:'OK',
                 4:'Warning',
                 16:'Critical',
                 8:'Unknown',
                 1:'Pending'}

def main(argv):
    parser = OptionParser(description='Generate a HTML report about current Nagios status.')
    parser.add_option('-a', '--address', dest='address', metavar='URL',
                      default='https://tatooine.chalmers.it:7777/nagios',
                      help='The base address of the Nagios web gui [default: %default]')
    parser.add_option('-u', '--username', dest='username', metavar='USER',
                      default='digit', help='The username used to login to nagios')
    parser.add_option('-p', '--password', dest='password', metavar='PASS',
                      default='', help='The password used to login to nagios')
    parser.add_option('-s', '--service-status', dest='service_status', metavar='STATUS',
                      default='ok+warning+critical+unknown+pending', help='The service statuses we are interested in [default: %default]')
    options, args = parser.parse_args(args=argv[1:])

    if not options.username or not options.password:
        parser.error('Username or password not set')

    json_req = None
    cgi_url = "/cgi-bin/statusjson.cgi?query=servicelist&details=true&servicestatus="
    url = options.address + cgi_url + options.service_status
    try:
        json_req = requests.get(url,
                                auth=(options.username,
                                      options.password),
                                      verify=False)
    except Exception as msg:
        print("Unable to fetch json from:", url, "\nMsg:", msg, file=sys.stderr)
        sys.exit(1)

    if json_req.status_code != requests.codes.ok:
        print("Non-OK HTTP status code:", json_req.status_code)
        sys.exit(1)

    output_html(json_req.json())

def output_html(json):
    for host, service in json['data']['servicelist'].items():
        print(host, " - ")
        print_services(service)

def print_services(services):
    for key, value in services.items():
        print("\t", key, "- Status:", nagios_status[value['status']])
        print("\t\t", value['plugin_output'])

if __name__ == '__main__':
    main(sys.argv)
