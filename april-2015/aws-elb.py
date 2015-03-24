#!/usr/bin/python

import boto.ec2.elb
import dns.resolver
import librato
import arrow

elb_connection = boto.ec2.elb.connect_to_region('us-east-1')
load_balancers = elb_connection.get_all_load_balancers()

librato_user = "auser@example.com"
librato_api_token = "XXXX"

api = librato.connect(librato_user,
                      librato_api_token,
                      sanitizer=librato.sanitize_metric_name
                      )
q = api.new_queue()
this_minute = arrow.utcnow().floor('minute').format('X')

for load_balancer in load_balancers:
    # print load_balancer.dns_name
    for address_type in ['A', 'AAAA']:
        try:
            answers = dns.resolver.query("all."+load_balancer.dns_name,
                                         address_type)
            for rdata in answers:
                # print "  " + str(rdata)
                q.add('hostname.ip.addresses_'+load_balancer.dns_name,
                      1, source=str(rdata), measure_time=this_minute)
        except dns.resolver.NoAnswer:
            pass
    q.submit()
