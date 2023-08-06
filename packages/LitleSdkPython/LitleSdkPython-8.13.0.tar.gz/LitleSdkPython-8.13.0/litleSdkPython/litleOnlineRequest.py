#Copyright (c) 2011-2012 Litle & Co.
#
#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation
#files (the "Software"), to deal in the Software without
#restriction, including without limitation the rights to use,
#copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the
#Software is furnished to do so, subject to the following
#conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#OTHER DEALINGS IN THE SOFTWARE.

#import litleSdkPython
import litleXmlFields
import pyxb
import os
from Communications import *
from Configuration import *

class litleOnlineRequest:
        
    def __init__(self, Configuration):
        self.Configuration = Configuration
        self.MerchantId = Configuration.getMerchantId()
        self.User = Configuration.getUser()
        self.Password = Configuration.getPassword()
        self.Version = Configuration.getVersion()
        self.ReportGroup = Configuration.getReportGroup()
        self.communications = Communications(self.Configuration)
        self.printXml = Configuration.getPrintXml()
        
    def _litleToXml(self,litleOnline):
        try :
            temp =litleOnline.toxml()
            temp= temp.replace('ns1:','')
            return temp.replace(':ns1','')
        except pyxb.BindingValidationError,e:
            raise Exception("Invalid Number of Choices, Fill Out One and Only One Choice",e)
        
    def sendRequest(self,transaction, user=None, password=None, version=None, merchantId=None, reportGroup=None, 
                    timeout=None, url=None, proxy=None):
        if (user != None):
            self.User = user
        if (password != None):
            self.Password = password
        if (version != None):
            self.Version = version
        if (merchantId != None):
            self.MerchantId = merchantId
        if (reportGroup != None):
            self.ReportGroup = reportGroup
            
        litleOnline = self._createTxn(transaction)
        requestXml = self._litleToXml(litleOnline)
        if(self.printXml):
            print'\nRequest:\n', requestXml
        responseXml = self.communications.http_post(requestXml, url=url,
                                                    proxy=proxy, timeout=timeout)
        if(self.printXml):
            print '\nResponse:\n', responseXml
        return self._processResponse(responseXml)
    
    def setCommunications(self, communications):
        self.communications = communications
     
    def _createTxn(self, transaction):
        litleOnline = litleXmlFields.litleOnlineRequest()
        litleOnline.merchantId = self.MerchantId
        litleOnline.version = self.Version
        authentication = litleXmlFields.authentication()
        authentication.user = self.User
        authentication.password =  self.Password 
        litleOnline.authentication = authentication
        transaction.reportGroup = self.ReportGroup
        litleOnline.transaction = transaction
        return litleOnline
    
    def _addNamespace(self, responseXml):
        if ((responseXml.count("xmlns='http://www.litle.com/schema'") == 0) and
            (responseXml.count('xmlns="http://www.litle.com/schema"') == 0)):
            return responseXml.replace(' response=',' xmlns="http://www.litle.com/schema" response=')    
        return responseXml
    
    def _processResponse(self, responseXml):
        temp = self._addNamespace(responseXml)
        try:
            response =litleXmlFields.CreateFromDocument(temp)
        except Exception, e:
            raise Exception("Error Processing Response", e)    
        if (response.response == '0'):
            return response.transactionResponse
        else:
            raise Exception(response.message)
      
