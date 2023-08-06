from urllib import urlopen
from xml.dom import minidom
from base import TargetPayBase, TargetPayException

API_URL = 'https://www.targetpay.com/ideal/'

class Ideal(TargetPayBase):
    """TargetPay Ideal API
    
    Ideal is a payment system used in The Netherlands.
    Documentation on the TargetPay Ideal API can be found here:
    
    https://www.targetpay.com/info/ideal-docu
    """

    def __init__(self, rtlo, test=False):
        """Constructor
        
        Arguments:
         * rtlo: Partner ID
         * test: Enable testing mode
        """
        super(Ideal, self).__init__(API_URL, rtlo)
        self.test = test
        self.start_url = self.api_url +  'start'
        self.check_url = self.api_url +  'check'
        self.issuer_url = self.api_url + 'getissuers.php?format=xml'
    
    def getBaseParameters(self):
        """Add test to the default set of parameters"""
        parameters = super(Ideal, self).getBaseParameters()
        parameters['test'] = self.test
        return parameters
    
    def startPayment(self, bank, description, amount, returnurl, currency='EUR', language='nl', reporturl=None):
        """Start a payment
        
        This function will return a URL to the users' ebanking environment.
        
        arguments:
         * bank: ID of the bank to use
         * description: Description of this payment
         * amount: Amount in cents
         * returnurl: URL to redirect the user to after a payment (either succesfull or failed)
         * currency: Currency, defaults to euro, not supported by Ideal at this moment
         * language: Language to use in the users' ebanking environment, not supported yet
         * reporrturl: URL to report the payment status to
        """
        if not amount > 0:
            raise ValueError('Amount should be positive')
        
        parameters = dict(
            bank=bank,
            description=description,
            amount=amount,
            returnurl=returnurl,
            currency=currency,
            language=language,
        )
        if reporturl:
            parameters['reporturl'] = reporturl
        result = self.doRequest(self.start_url, **parameters)
        result = result.split('|')
        if not len(result) > 1:
            result = result[0].split(' ')
            raise TargetPayException(result[0], ' '.join(result[1:]))
        return result[1]
    
    def checkPayment(self, trxid, once=True):
        """Check the status of a payment
        
        Arguments:
         * trxid: Transaction ID
         * once: Return an error if the same transaction is requested more than once
        """
        result = self.doRequest(self.check_url, trxid=trxid, once=once)
        result = result.split(' ')
        if not result[0] == '000000':
            raise TargetPayException(result[0], ' '.join(result[1:]))
        return True
    
    def getIssuers(self):
        """Returns a list of available banks"""
        response = urlopen(self.issuer_url).read()
        xml = minidom.parseString(response)
        issuers = xml.getElementsByTagName('issuer')
        result = {}
        for issuer in issuers:
            result[issuer.getAttribute('id')] = issuer.firstChild.nodeValue
        return result