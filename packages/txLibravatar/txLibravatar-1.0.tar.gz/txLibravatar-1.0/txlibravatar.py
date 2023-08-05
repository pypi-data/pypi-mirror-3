"""
TxLibravatar Twisted module for Libravatar

Copyright (C) 2011 Francois Marier <francois@libravatar.org>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""

# pylint: disable=F0401
from libravatar import compose_avatar_url, service_name, normalized_target
from libravatar import parse_user_identity, parse_options
from twisted.internet import defer
from twisted.names import client, dns
from twisted.names.error import DNSNameError, DNSServerError, DNSFormatError
from twisted.names.error import DNSNotImplementedError, DNSQueryRefusedError
from twisted.names.error import DNSUnknownError, ResolverError


def libravatar_url(email=None, openid=None, https=False,
                   default=None, size=None):
    """
    Return a URL to the appropriate avatar
    """

    avatar_hash, domain = parse_user_identity(email, openid)
    query_string = parse_options(default, size)

    d = lookup_avatar_server(domain, https)
    d.addCallback(compose_avatar_url, avatar_hash, query_string, https)
    return d


def parse_srv_response(result, https):
    """
    Extract the avatar servers from SRV records in the DNS zone

    The SRV records should look like this:

       _avatars._tcp.example.com.     IN SRV 0 0 80  avatars.example.com
       _avatars-sec._tcp.example.com. IN SRV 0 0 443 avatars.example.com
    """

    (answer, unused, unused) = result

    records = []
    for record in answer:
        if record.type != dns.SRV:
            continue

        srv_record = {'priority': int(record.payload.priority),
                      'weight': int(record.payload.weight),
                      'port': int(record.payload.port),
                      'target': record.payload.target}

        records.append(srv_record)

    return normalized_target(records, https)


def error_handler(failure):
    """
    Swallow all DNS-related errors and simply default to
    libravatar.org in these cases.
    """

    failure.trap(DNSNameError, DNSServerError, DNSFormatError,
                 DNSNotImplementedError, DNSQueryRefusedError,
                 DNSUnknownError, ResolverError)


def lookup_avatar_server(domain, https):
    """
    Return the avatar server to federate to (if any).
    """

    if not domain:
        return defer.succeed(None)

    d = client.lookupService(service_name(domain, https))
    d.addCallback(parse_srv_response, https)
    d.addErrback(error_handler)
    return d
