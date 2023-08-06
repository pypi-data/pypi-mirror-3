import os
import sys
import httplib, urllib, ConfigParser
import md5
import string
import base64
import re
import yaml
from types import DictType 
import pprint

from xml.dom.minidom import parseString, Node
from BeautifulSoup import BeautifulStoneSoup
from ebaysdk.utils import object_dict, xml2dict, dict2xml, dict_to_xml, escape

       
def nodeText(node):

    rc = []

    if hasattr(node, 'childNodes'):
        for cn in node.childNodes:
            if cn.nodeType == cn.TEXT_NODE:
                rc.append(cn.data)
            elif cn.nodeType == cn.CDATA_SECTION_NODE:
                rc.append(cn.data)    
        
    return ''.join(rc)

def tag(name, value):
    return "<%s>%s</%s>" % ( name, value, name )

class ebaybase(object):
    
    def __init__(self,debug=0):                
        self.verb   = None
        self.debug  = debug
        
        self.spooled_calls = [];
        self._reset()
        
    def v(self, *args, **kwargs):        
        args_a = [w for w in args]
        first  = args_a[0]
        args_a.remove(first)

        h = kwargs.get('mydict', {})
        if h:
            h = h.get(first, {})
        else:
            h = self.response_dict().get(first, {})
        
        if len(args) == 1:
            try:
                return h.get('value', None)
            except:
                return h
                
        last = args_a.pop()
        
        for a in args_a:
            h = h.get(a, {})

        h = h.get(last, {})
        
        try:
            return h.get('value', None)
        except:
            return h    
        
    def load_yaml(self, config_file):
            
        dirs = [ '.', os.environ.get('HOME'), '/etc' ]

        for mydir in dirs:
            myfile = "%s/%s" % (mydir, config_file)
            
            if os.path.exists( myfile ):
                try:
                    f = open( myfile, "r" ) 
                except IOError, e:
                    print "unable to open file %s" % e

                #print "using file %s" % myfile
                
                yData  = yaml.load( f.read() )
                domain = self.api_config.get('domain', '')
                
                self.api_config_append( yData.get(domain, {}) )
                return
    
    def api_config_append(self, config):
        for c in config:
            self.api_config[c] = config[c] 
        
    def getNodeText(self,nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    def _reset(self):
        self._response_content = None
        self._response_dom     = None
        self._response_soup    = None
        self._response_dict    = None
        self._response_error   = None
        
    def do(self,verb,call_data=dict()):
        return self.execute(verb,call_data)
                    
    def execute(self,verb,xml):
        self.verb        = verb
        self.call_xml    = xml

        self._reset()    
        self._response_content = self._execute_http_request()

        # remove xml namespace
        regex = re.compile( 'xmlns="[^"]+"' )
        self._response_content = regex.sub( '', self._response_content )

    def response_soup(self):
        if not self._response_soup:
            self._response_soup = BeautifulStoneSoup(unicode(self._response_content))
        
        return self._response_soup
        
    def response_dom(self):
        if not self._response_dom:
            dom = parseString((self._response_content or ("<%sResponse></%sResponse>" % (self.verb, self.verb))) )
            self._response_dom = dom.getElementsByTagName(self.verb+'Response')[0]
        
        return self._response_dom

    def response_dict(self):
        if not self._response_dict:
            mydict = xml2dict().fromstring(self._response_content)
            self._response_dict = mydict.get(self.verb+'Response', mydict)
            
        return self._response_dict
        
    def api_init(self,config_items):
        for config in config_items:
            self.api_config[config[0]] = config[1]
        
 
    
    def _execute_http_request(self):
        "performs the http post and returns the XML response body"
        
        try:
            
            if self.api_config.get('https'):
                connection = httplib.HTTPSConnection(
                    self.api_config.get('domain', None),
                    #timeout=10
                )
            else:
                connection = httplib.HTTPConnection(
                    self.api_config.get('domain', None),
                    #timeout=10
                )
             
            connection.set_debuglevel(0)
            connection.request(
                "POST", 
                self.api_config.get('uri', None), 
                self._build_request_xml(), 
                self._build_request_headers()
            )

            self._response_object = connection.getresponse()
            xml = self._response_object.read()
            connection.close()

        except Exception, e:
            self._response_error = "%s" % e
            return ""
                       
        if self._response_object.status != 200:
            self._response_error = "Error sending request:" + self._response_object.reason
            return ""
        else:    
            return xml
    
    def has_error(self):
        str = self._collect_errors()
        
        if (len(str) > 0):
            return True
        else:
            return False
            
    def error(self):
        "builds and returns the api error message"
                
        str = self._collect_errors()

        if ( len(str) > 0 ):
            return "%s error:\n%s\n" % (self.verb, "\n".join(str))
        else:
            return ""

    def _collect_errors(self):

        str_array = []

        if self._response_error:
            str_array.append( self._response_error )

        for e in self.response_dom().getElementsByTagName("Errors"):

            if e.getElementsByTagName('ErrorClassification'):
                str_array.append( '- Class: %s' % nodeText(e.getElementsByTagName('ErrorClassification')[0])  )

            if e.getElementsByTagName('SeverityCode'):
                str_array.append( '- Severity: %s' % nodeText(e.getElementsByTagName('SeverityCode')[0])  )

            if e.getElementsByTagName('ErrorCode'):
                str_array.append( '- Code: %s' % nodeText(e.getElementsByTagName('ErrorCode')[0])  )

            if e.getElementsByTagName('ShortMessage'):
                str_array.append( '- %s ' % nodeText(e.getElementsByTagName('ShortMessage')[0])  )

            if e.getElementsByTagName('LongMessage'):
                str_array.append( '- %s ' % nodeText(e.getElementsByTagName('LongMessage')[0])  )        

        return str_array
        
class shopping(ebaybase):
    """
    Shopping backend for ebaysdk.
    http://developer.ebay.com/products/shopping/
    
    >>> s = shopping()
    >>> s.debug = 5
    >>> s.execute('FindProducts', tag('QueryKeywords', 'apple'))
    >>> if not s.has_error():
    ...     print s.v('Ack')
    ... else:
    ...     print s.error()
    Success
    >>> s.execute('FindItemsAdvanced', "%s%s" % (tag('CharityID', '3897'), tag('ModTimeFrom','2010-08-30T19:09:02.768Z' )))
    >>> d = s.response_dict()    
    """
    
    def __init__(self, 
        domain='open.api.ebay.com', 
        uri='/shopping',
        https=False,
        siteid=0,
        response_encoding='XML',
        request_encoding='XML',
        config_file='ebay.yaml',
        debug=0 ):

        ebaybase.__init__(self)

        self.debug = debug
        
        self.api_config = {
            'domain' : domain,
            'uri' : uri,
            'https' : https,
            'siteid' : siteid,
            'response_encoding' : response_encoding,
            'request_encoding' : request_encoding,
        }    

        self.load_yaml(config_file)

    def v(self, *args, **kwargs):        
        args_a = [w for w in args]
        first  = args_a[0]
        #args_a.remove(first)

        h = kwargs.get('mydict', {})
        if h:
            h = h.get(first, {})
        else:
            h = self.response_dict().get(first, {})

        if len(args) == 1:
            try:
                return h.get('value', None)
            except:
                return h

        last = args_a.pop()

        for a in args_a:
            h = h.get(a, {})

        h = h.get(last, {})

        try:
            return h.get('value', None)
        except:
            return h
    def _build_request_headers(self):
        return {
            "X-EBAY-API-VERSION": self.api_config.get('version', ''),	
            "X-EBAY-API-APP-ID": self.api_config.get('appid', ''),
            "X-EBAY-API-SITEID": self.api_config.get('siteid', ''),
            "X-EBAY-API-CALL-NAME": self.verb,
            "X-EBAY-API-REQUEST-ENCODING": "XML",
            "Content-Type": "text/xml"
        }

    def _build_request_xml(self):
        xml = "<?xml version='1.0' encoding='utf-8'?>"
        xml += "<" + self.verb + "Request xmlns=\"urn:ebay:apis:eBLBaseComponents\">"
        xml += self.call_xml
        xml += "</" + self.verb + "Request>"

        return xml

class html(ebaybase):
    """
    HTML backend for ebaysdk.

    >>> h = html()
    >>> h.execute('http://shop.ebay.com/i.html?rt=nc&_nkw=mytouch+slide&_dmpt=PDA_Accessories&_rss=1')
    >>> if not h.has_error():
    ...     print h.v('rss', 'channel', 'ttl')
    ...     title = h.response_dom().getElementsByTagName('title')[0]
    ...     print nodeText( title )
    ...     print title.toxml()
    ... else:
    ...     print h.error()
    60
    mytouch slide
    <title><![CDATA[mytouch slide]]></title>
    """

    def __init__(self):
        ebaybase.__init__(self)

    def response_dom(self):
        if not self._response_dom:
            self._response_dom = parseString(self._response_content)

        return self._response_dom

    def response_dict(self):
        if not self._response_dict:
            self._response_dict = xml2dict().fromstring(self._response_content)
            
        return self._response_dict

    def execute(self,url, call_data=dict()):
        self.url = url
        self.call_data = call_data
        
        self._reset()    
        self._response_content = self._execute_http_request()

        # remove xml namespace
        regex = re.compile( 'xmlns="[^"]+"' )
        self._response_content = regex.sub( '', self._response_content )

    def _execute_http_request(self):
        "performs the http post and returns the XML response body"

        try:
            regex = re.compile( 'http(s?)://([^/]+)(.*)' )
            p = re.findall( regex, self.url ).pop()

            if p[0] == 's':
                connection = httplib.HTTPSConnection(p[1])
            else:
                connection = httplib.HTTPConnection(p[1])


            connection.set_debuglevel(0)
            connection.request(
                "GET", 
                p[2], 
                urllib.urlencode(self.call_data)
            )
        
            response = connection.getresponse()        
            xml = response.read()
            connection.close()
        except Exception, e:
            self._response_error = "failed to connect: %s" % e
            return ""
            
        if response.status > 400:
            self._response_error = "Error sending request:" + response.reason            
            return ""
        else:
             return xml                           

    def has_error(self):
        if self._response_error is None:
            return False
        else:
            return True
            
    def error(self):
         "builds and returns the api error message"
        
         if self._response_error != "":
             return self._response_error
         else:
             return None
         
class trading(ebaybase):
    """
    Trading backend for the ebaysdk
    http://developer.ebay.com/products/trading/
    
    >>> t = trading()
    >>> t.execute('GetCharities', tag('CharityID', '3897'))        
    >>> if not t.has_error():
    ...    print nodeText(t.response_dom().getElementsByTagName('Name')[0])
    ... else:
    ...    print t.error()
    Sunshine Kids Foundation
    """

    def __init__(self, 
        domain='api.ebay.com', 
        uri='/ws/api.dll',
        https=False,
        siteid='0',
        response_encoding='XML',
        request_encoding='XML',
        config_file='ebay.yaml' ):
        
        ebaybase.__init__(self)

        self.api_config = {
            'domain' : domain,
            'uri'    : uri,
            'https'  : https,
            'siteid' : siteid,
            'response_encoding' : response_encoding,
            'request_encoding' : request_encoding,
        }    

        self.load_yaml(config_file)        

    def _build_request_headers(self):
        return {
            "X-EBAY-API-COMPATIBILITY-LEVEL": self.api_config.get('compatability','648'),	
            "X-EBAY-API-DEV-NAME": self.api_config.get('devid', ''),
            "X-EBAY-API-APP-NAME": self.api_config.get('appid',''),
            "X-EBAY-API-CERT-NAME": self.api_config.get('certid',''),
            "X-EBAY-API-SITEID": self.api_config.get('siteid',''),
            "X-EBAY-API-CALL-NAME": self.verb,
            "Content-Type": "text/xml"
        }

    def _build_request_xml(self):
        xml = "<?xml version='1.0' encoding='utf-8'?>"
        xml += "<" + self.verb + "Request xmlns=\"urn:ebay:apis:eBLBaseComponents\">"
        xml += "<RequesterCredentials>"
        if self.api_config.get('token', None):
            xml += "<eBayAuthToken>%s</eBayAuthToken>" % self.api_config.get('token')
        else:
            xml += "<Username>%s</Username>" % escape(self.api_config.get('username', ''))
            xml += "<Password>%s</Password>" % escape(self.api_config.get('password', ''))
                
        xml += "</RequesterCredentials>" 
        xml += self.call_xml
        xml += "</" + self.verb + "Request>"

        return xml
                        
class finding(ebaybase):
    """
    Finding backend for ebaysdk.
    http://developer.ebay.com/products/finding/
    
    >>> f = finding()
    >>> f.execute('findItemsAdvanced', tag('keywords', 'shoes'))        
    >>> if not f.has_error():
    ...     print f.v('itemSearchURL') != ''
    ...     items = f.v('searchResult', 'item') 
    ...     print len(items)
    ...     print f.v('ack')
    ...     print nodeText(f.response_dom().getElementsByTagName('ack')[0])
    ... else:
    ...     print f.error()
    True
    100
    Success
    Success
    """

    """
    print "itemId"
    print f.v('country', mydict=items[0])
    print f.v('itemId', mydict=items[0])
    print f.v('title', mydict=items[0])
    print f.v('primaryCategory', 'categoryId', mydict=items[0])

    # examples using the response dom
    titles = f.response_dom().getElementsByTagName('title')
    print titles[0].toxml()
    print nodeText(titles[0])

    items = f.response_dom().getElementsByTagName('item')

    # <shippingServiceCost currencyId="USD">4.75</shippingServiceCost>
    shipCost = items[0].getElementsByTagName('shippingServiceCost')[0]
    print shipCost.attributes['currencyId'].value
    print nodeText(shipCost)
    """
    
    def __init__(self, 
        domain='svcs.ebay.com', 
        service='FindingService', 
        uri='/services/search/FindingService/v1',
        https=False,
        siteid='EBAY-US',
        response_encoding='XML',
        request_encoding='XML',
        config_file='ebay.yaml' ):

        ebaybase.__init__(self)

        self.api_config = {
            'domain'  : domain,
            'service' : service,
            'uri'     : uri,
            'https'   : https,
            'siteid'  : siteid,
            'response_encoding' : response_encoding,
            'request_encoding' : request_encoding,
        }    

        self.load_yaml(config_file)

    def _build_request_headers(self):
        return {
            "X-EBAY-SOA-SERVICE-NAME" : self.api_config.get('service',''),
            "X-EBAY-SOA-SERVICE-VERSION" : self.api_config.get('version',''),
            "X-EBAY-SOA-SECURITY-APPNAME"  : self.api_config.get('appid',''),
            "X-EBAY-SOA-GLOBAL-ID"  : self.api_config.get('siteid',''),
            "X-EBAY-SOA-OPERATION-NAME" : self.verb,
            "X-EBAY-SOA-REQUEST-DATA-FORMAT"  : self.api_config.get('request_encoding',''),
            "X-EBAY-SOA-RESPONSE-DATA-FORMAT" : self.api_config.get('response_encoding',''),
            "Content-Type" : "text/xml"
        }

    def _build_request_xml(self):
        xml = "<?xml version='1.0' encoding='utf-8'?>"
        xml += "<" + self.verb + "Request xmlns=\"http://www.ebay.com/marketplace/search/v1/services\">"
        xml += self.call_xml
        xml += "</" + self.verb + "Request>"

        return xml
