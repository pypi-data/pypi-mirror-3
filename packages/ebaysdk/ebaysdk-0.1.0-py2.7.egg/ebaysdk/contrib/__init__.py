from ebaysdk import ebaybase, tag, nodeText
import urllib
import urllib2
import re
from types import DictType 
import pprint

from xml.dom.minidom import parseString, Node
from BeautifulSoup import BeautifulStoneSoup
from ebaysdk.utils import object_dict, xml2dict, dict2xml, dict_to_xml

class gazelle(ebaybase):
    '''
    >>> from ebaysdk.contrib import gazelle
    >>> g = gazelle()
    >>> g.execute("https://www.gazelle.com/sr1_api/products/search.xml", { 'keywords' : 'nikon', 'items_per_pages' : 10 })
    >>> tot = nodeText(g.response_dom().getElementsByTagName('total_results')[0])
    >>> print tot > 10
    True
    '''

    def __init__(self, 
        username='c462fe43f27f864bf6f1ad3b178d4c0b', 
        password='3547d16b259b27a2bf99027ad9ca021978cae1aa',
        realm='Application'):
        
        ebaybase.__init__(self)

        self.username = username
        self.password = password
        self.realm    = realm

    def response_dom(self):
        if not self._response_dom:
            self._response_dom = parseString(self._response_content)

        return self._response_dom

    def response_dict(self):
        if not self._response_dict:
            self._response_dict = xml2dict().fromstring(self._response_content)

        return self._response_dict
        
    def execute(self, url, call_data=dict()):
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

            auth_handler = urllib2.HTTPBasicAuthHandler()
            auth_handler.add_password(
                realm=self.realm,
                uri=self.url,
                user=self.username,
                passwd=self.password
            )
            opener = urllib2.build_opener(auth_handler)
            urllib2.install_opener(opener)

            response = urllib2.urlopen(
                "%s?%s" % (self.url, urllib.urlencode(self.call_data))
            )

            xml = response.read()

        except Exception, e:
            self._response_error = "failed to connect: %s" % e
            return ""

        return xml                           

    def error(self):
         "builds and returns the api error message"
         
         return self._response_error

    
class cexchange(ebaybase):
    """
    Shopping backend for ebaysdk.
    http://developer.ebay.com/products/shopping/
    
    >>> c = cexchange()
    >>> c.execute('SearchProducts', tag('keywords', tag('string', 'iPhone 3G 8GB')) )
    >>> print c._response_content
    Success
    >>> c.execute('GetProductByEbayProductId', tag('eBayProductId', 'EPID71354345'))
    >>> print c._response_content
    Test
    """
    
    def __init__(self, 
        domain='services.cexops.com', 
        uri='/SOAP/RMS.asmx',
        https=False,
        response_encoding='XML',
        request_encoding='XML',
        config_file='ebay.yaml',
        debug=5 ):

        ebaybase.__init__(self)

        self.api_config = {
            'domain' : domain,
            'uri' : uri,
            'https' : https,
            'response_encoding' : response_encoding,
            'request_encoding' : request_encoding,
        }    

        self.load_yaml(config_file)

    def _build_request_headers(self):
        return {
            "SOAPAction" : "\"http://cexchange.com/services/%s\"" % self.verb,
            "Content-Type": "text/xml"
        }

    def _build_request_xml(self):

        xml = "<?xml version='1.0' encoding='utf-8'?>"
        xml += "<soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\""
        xml += " xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\""
        xml += " xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">"
        xml += "<soap:Body><%s xmlns=\"http://cexchange.com/services\">" % self.verb
        xml += self.call_xml
        xml += "</%s>" %self.verb
        xml += "</soap:Body></soap:Envelope>"

        return xml
