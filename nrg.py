#!/usr/bin/env python
''' NagiosReportGenerator - Generate HTML status report

TODO: Write desc

Copyright (c) 2014 digIT 14/15
'''

import time
import sys
import datetime
from optparse import OptionParser
import requests

nagios_status = {2:'OK',
                 4:'Warning',
                 16:'Critical',
                 8:'Unknown',
                 1:'Pending'}
status_bgcolor = {2:"#2BE043",
                  4:"#F2ED4E",
                  16:"#E34040",
                  8:"#000",
                  1:"#000"}

mail_header = """From: Nagios Weekly Reporter <nagios@chalmers.it>\r
To: <RECIPIENT>
Reply-To: no-reply@chalmers.it
MIME-Version: 1.0
Subject: Weekly status report
Content-Type: text/html; charset=utf-8
"""

html_header = """<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Weekly Nagios status report</title>
</head>
<body>
"""

html_footer = """</body>
</html>"""

def main(argv):
    options = define_arguments(argv)

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
        print("Non-OK HTTP status code:", json_req.status_code, file=sys.stderr)
        sys.exit(1)

    if options.print_mail_header:
        print(mail_header.replace("<RECIPIENT>", options.recipient))
    output_html(json_req.json())

def output_html(json):
    if not 'servicelist' in json['data']:
        print("Unable to find any services in json. Unknown/invalid --service-status?", file=sys.stderr)
        sys.exit(1)

    print(html_header)
    print("<h2>Nagios status report ", time.strftime("week %W"), "</h2>", sep="")
    print("<h3>Generated on ", time.strftime("%d %b %Y %H:%M:%S"), "</h3>", sep="")
    print("<table border=1>")
    print("<tr>\n\t<th>Host</th><th style='width:100px'>Service</th><th>Status</th><th>Last check</th><th>Status information</th>\n</tr>")
    for host, service in json['data']['servicelist'].items():
        print_service_data(host, service)
    print("</table>")
    print(html_footer)

def print_service_data(host, services):
    i = 0
    for key, value in services.items():
        bgcolor = status_bgcolor[value['status']]
        if i <= 0:
            print("\t<tr><td>", host, "</td>", sep="")
        else:
            print("\t<tr><td></td>")
        print("\t\t<td>", key, "</td>", sep="")
        print("\t\t<td style='background-color:", bgcolor, "'>", nagios_status[value['status']], "</td>", sep="")
        last_check = datetime.datetime.fromtimestamp(float(value['last_check']/1000)).strftime('%Y-%m-%d %H:%M:%S')
        print("\t\t<td>", last_check, "</td>", sep="")
        print("\t\t<td><pre>", value['plugin_output'], "</pre></td>", sep="")
        print("\t</tr>")
        i = i + 1

def define_arguments(argv):
    parser = OptionParser(description=
                          'Generate a HTML report about current Nagios status')
    parser.add_option('-a', '--address', dest='address', metavar='URL',
                      default='https://localhost:/nagios',
                      help='The base address of the Nagios web gui [default: %default]')
    parser.add_option('-u', '--username', dest='username', metavar='USER',
                      default='digit', help='The username used to login to nagios')
    parser.add_option('-p', '--password', dest='password', metavar='PASS',
                      default='', help='The password used to login to nagios')
    parser.add_option('-s', '--service-status', dest='service_status', metavar='STATUS',
                      default='ok+warning+critical+unknown+pending', help='The service statuses we are interested in [default: %default]')
    parser.add_option('-r', '--recipient', dest='recipient', metavar='RECIPIENT',
                      default='digit@chalmers.it', help='The mail address of the recipient of the report [default: %default]')
    parser.add_option('-d', '--disable-mail-header', dest='print_mail_header', metavar='PRINT', action="store_false",
                      default=True, help='Disable printing of the mail headers')
    options, _ = parser.parse_args(args=argv[1:])
    return options

if __name__ == '__main__':
    main(sys.argv)
