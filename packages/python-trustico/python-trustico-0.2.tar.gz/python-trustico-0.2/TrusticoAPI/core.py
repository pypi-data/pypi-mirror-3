#
# Copyright 2012 Patrick Hetu <patrick.hetu@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import sys

import requests
import simplejson
from M2Crypto import X509

from pprint import pprint
from optparse import OptionParser

from schema import PRODUCTS, PROCESS
from schema import validate_order, validate_address, ValidationError

RE_PIPE = re.compile(r'(.*?)\|(.*?)\|', re.DOTALL)

APIURL = 'https://api.ssl-processing.com/geodirect/postapi/';


class TrusticoAPI:

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def call(self, command, **kwargs):
        payload = {
           'UserName': self.username,
           'Password': self.password,
        }

        payload['Command'] = command
        payload.update(kwargs)

        r = requests.post(APIURL, data=payload)

        result_dict = {}
        for row in RE_PIPE.findall(r.content):
            if not row: continue
            result_dict[row[0].strip('\n')] = row[1]
        return result_dict

    def hello(self, string="python-trustico test string"):
        return self.call('Hello', TextToEcho=string)

    def order(self, admin_address, tech_address, order, csr, renewal=0):
        payload = {}


        product = order['product']
        process = PRODUCTS[product]['process']

        for field, value in order.items():
            name = PROCESS[process][field]
            payload[name] = value

        for field, value in admin_address.items():
            name = PROCESS[process]['admin'][field]
            payload[name] = value

        for field, value in tech_address.items():
            name = PROCESS[process]['tech'][field]
            payload[name] = value

        if renewal == 1: payload['ProductName'] += ' RN'

        payload['ProductName'] = PRODUCTS[product]['name']
        payload['CSR'] = csr
        payload['AgreedToTerms'] = 1

        if process == '1':
            return self.call('ProcessType1', **payload)
        elif process == '2':
            return self.call('ProcessType2', **payload)

    def status_orderid(self, orderid):
        return self.call('GetStatus', OrderID = orderid)

    def status_issuerid(self, issuerid):
        return self.call('GetStatus', IssuerOrderID = issuerid)

    def get_approvers(self, domain, cli=False):
        result = self.call('GetApproverList', Domain = domain)
        emails = [str(email) for email in result.values() if '@' in email]

        # remove duplicates
        emails = list(set(emails))

        if cli:
            for email in sorted(emails): print email
        else:
            return emails


def main():
    parser = OptionParser()

    parser.add_option("-u", "--username", dest="username",
                    metavar="<username>", help="Your Trustico username")
    parser.add_option("-p", "--password", dest="password",
                    help="Your Trustico password")

    parser.add_option("-l", "--products", dest="show_products", action="store_true",
                    help="List products and related options")

    parser.add_option("-s", "--status", dest="status", action="store_true",
                    help="Query a status of an order or an issuer")
    parser.add_option("-o", "--orderid", dest="orderid",
                    help="The order id to check")
    parser.add_option("-i", "--issuerid", dest="issuersid",
                    help="The Issuers id to check")


    parser.add_option("-t", "--test", dest="test", action="store_true",
                    help="Test the username/password")
    parser.add_option("-r", "--renewal", dest="renewal", action="store_true",
                    help="Make the order processed as a renewal instead of a new order")

    parser.add_option("-a", "--approvers", dest="approvers", action="store_true",
                    help="<domain> Get the list of approvers email for a domain")

    parser.add_option("-C", "--csr_file", dest="csr_file",
                    help="Your certificate request", metavar="FILE")
    parser.add_option("-A", "--admin_address_file", dest="admin_address_file",
                    help="JSON file containing the admin address", metavar="FILE")
    parser.add_option("-T", "--tech_address_file", dest="tech_address_file",
                    help="JSON file containing the tech address", metavar="FILE")
    parser.add_option("-O", "--order_file", dest="order_file",
                    help="JSON file containing the order", metavar="FILE")

    (opt, args) = parser.parse_args()

    if opt.show_products:
        pprint(PRODUCTS)
        sys.exit(0)

    if opt.test and opt.username and opt.password:
        t = TrusticoAPI(opt.username, opt.password)
        pprint(t.hello())
        sys.exit(0)

    if opt.approvers and opt.username and opt.password and len(args) == 1:
        t = TrusticoAPI(opt.username, opt.password)
        t.get_approvers(args[0], cli=True)
        sys.exit(0)

    if opt.status and opt.orderid:
        t = TrusticoAPI(opt.username, opt.password)
        pprint(t.status_orderid(opt.orderid))
        sys.exit(0)

    if opt.status and opt.issuersid:
        t = TrusticoAPI(opt.username, opt.password)
        pprint(t.status_issuersid(opt.issuersid))
        sys.exit(0)

    if opt.username and opt.password and opt.admin_address_file and\
       opt.order_file and opt.tech_address_file:
        admin_address = simplejson.load(open(opt.admin_address_file, 'r'))
        tech_address = simplejson.load(open(opt.tech_address_file, 'r'))
        order = simplejson.load(open(opt.order_file, 'r'))

        t = TrusticoAPI(opt.username, opt.password)

        # get domain
        req = X509.load_request(opt.csr_file)
        name = str(req.get_subject())
        domain = name.split('/')[1].replace('CN=','').lstrip('.*')

        # validations
        try:
            validate_order(order, t.get_approvers(domain))
        except ValidationError, e:
            print "Error while validating order: %s" % e
            sys.exit(1)

        try:
            validate_address(admin_address)
        except ValidationError, e:
            print "Error while validating admin address: %s" % e
            sys.exit(1)

        try:
            validate_address(tech_address)
        except ValidationError, e:
            print "Error while validating tech address: %s" % e
            sys.exit(1)

        # send the order
        pprint(t.order(admin_address, tech_address, order, req.as_pem(), renewal=opt.renewal))
        sys.exit(0)

    parser.print_help()
    print "incorrect arguments"
    sys.exit(1)

