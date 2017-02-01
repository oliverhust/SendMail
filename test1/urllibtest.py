#!/usr/bin/python
# -*- coding: utf-8 -*-


import urllib
import urllib2


def test1():
    url = 'http://www.pythontab.com'
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'

    values = {'name' : 'Michael Foord',
              'location' : 'pythontab',
              'language' : 'Python' }
    headers = { 'User-Agent' : user_agent }
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(req)
    the_page = response.read()
    print(the_page[0:1024])
    print("-"*128)
    print(the_page[-1024:])


def test2():
    to_trans = \
'''6.3.1.  Portal IP Address
   This attribute is the IP address of the Portal through which a Storage Node can transmit and receive storage data.  The Portal IP Address is a 16-byte field that may contain an IPv4 or IPv6 address. When this field contains an IPv4 address, it is stored as an IPv4- mapped IPv6 address.  That is, the most significant 10 bytes are set to 0x00, with the next 2 bytes set to 0xFFFF [RFC2373].  When this field contains an IPv6 address, the entire 16-byte field is used. The Portal IP Address and the Portal TCP/UDP Port number (see 6.3.2 below) are used as a key to identify a Portal uniquely.  It is a required attribute for registration of a Portal.
6.3.2.  Portal TCP/UDP Port
   The TCP/UDP port of the Portal through which a Storage Node can transmit and receive storage data.  Bits 16 to 31 represents the TCP/UDP port number.  Bit 15 represents the port type.  If bit 15 is set, then the port type is UDP.  Otherwise it is TCP.  Bits 0 to 14 are reserved.
   If the field value is 0, then the port number is the implied canonical port number and type of the protocol indicated by the associated Entity Type.
   The Portal IP Address and the Portal TCP/UDP Port number are used as a key to identify a Portal uniquely.  It is a required attribute for registration of a Portal.
6.3.3.  Portal Symbolic Name
   A variable-length UTF-8 encoded NULL-terminated text-based description of up to 256 bytes.  The Portal Symbolic Name is a user- readable description of the Portal entry in the iSNS server.
Tseng, et al.              Standards Track                     [Page 80]
RFC 4171          Internet Storage Name Service (iSNS)    September 2005
6.3.4.  Entity Status Inquiry Interval
   This field indicates the requested time, in seconds, between Entity Status Inquiry (ESI) messages sent from the iSNS server to this Network Entity.  ESI messages can be used to verify that a Portal registration continues to be valid.  To request monitoring by the iSNS server, an iSNS client registers a non-zero value for this Portal attribute using a DevAttrReg message.  The client MUST register an ESI Port on at least one of its Portals to receive the ESI monitoring.
   If the iSNS server does not receive an expected response to an ESI message, it SHALL attempt an administratively configured number of re-transmissions of the ESI message.  The ESI Interval period begins with the iSNS server's receipt of the last ESI Response.  All re- transmissions MUST be sent before twice the ESI Interval period has passed.  If no response is received from any of the ESI messages, then the Portal SHALL be deregistered.  Note that only Portals that have registered a value in their ESI Port field can be deregistered in this way.
   If all Portals associated with a Network Entity that have registered for ESI messages are deregistered due to non-response, and if no registrations have been received from the client for at least two ESI Interval periods, then the Network Entity and all associated objects (including Storage Nodes) SHALL be deregistered.
   If the iSNS server is unable to support ESI messages or the ESI Interval requested, it SHALL either reject the ESI request by returning an "ESI Not Available" Status Code or modify the ESI Interval attribute by selecting its own suitable value and returning that value in the Operating Attributes of the registration response message.
   If at any time an iSNS client that is registered for ESI messages has not received an ESI message to any of its Portals as expected, then the client MAY attempt to query the iSNS server using a DevAttrQry message using its Entity_ID as the key.  If the query result is the error "no such entry", then the client SHALL close all remaining TCP connections to the iSNS server and assume that it is no longer registered in the iSNS database.  Such a client MAY attempt re- registration.
'''
    to_trans = urllib.quote(to_trans)

    url = "http://translate.google.cn/translate_a/single?client=t&sl=auto&tl=zh-CN&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&ssel=3&tsel=0&kc=1&tk=20013.396941 HTTP/1.1"
    headers = {
        'Accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        'Referer': 'http://translate.google.cn/',
        'Accept-Language': 'zh-CN',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
        'Host': 'translate.google.cn',
        'Connection': 'Keep-Alive',
        'Cache-Control': 'no-cache',
        'Cookie': 'NID=87=VZ1GKQxfxIKkuSU694vEqySgWfnNx11M7dcUVVFmyRMbwBuG8XbxW2wpZUlfbU7YBYxREo7vN3zj4YvSB-ITqMu9vMhFVusIhVNCmAGvkdwvTRPE9Zp0lSqgTgllQ6dr; _ga=GA1.3.708381979.1475137972',
    }
    values = {'q': to_trans}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(req)
    the_page = response.read()
    print(the_page[0:1024])
    print("-"*128)
    print(the_page[-1024:])


if __name__ == '__main__':
    test2()

