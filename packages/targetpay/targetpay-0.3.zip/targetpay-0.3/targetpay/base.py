from urllib import urlencode, urlopen

class TargetPayException(Exception):
    pass

class TargetPayBase(object):
    """Base class for the various TargetPay APIs
    
    This class should not be used directly by third-party code.
    """
    
    def __init__(self, api_url, rtlo, ip='', domain=''):
        """Constructor
        
        Parameters:
         * api_url: The URL for this specific API
         * rtlo: Partner ID
        """
        self.api_url = api_url
        self.rtlo = rtlo
    
    def getBaseParameters(self):
        """Returns a dictionary containing default parameters for a request
        """
        parameters = {
            'rtlo': self.rtlo,
        }
        return parameters
    
    def doRequest(self, url, **parameters):
        """Send a request to TargetPay
        
        Arguments:
         * url: The URL to call
         * Named arguments will be passed as URL parameters to the API call
        """
        url_parameters = self.getBaseParameters()
        url_parameters.update(parameters)
        url += '?' + urlencode(url_parameters)
        return urlopen(url).read()