import urllib2, re, base64, cookielib

from plone.app.layout.viewlets import ViewletBase

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.externalsnippet import _

class WindowViewlet(ViewletBase):
    
    index = ViewPageTemplateFile("window.pt")
    
    def update(self):
        super(WindowViewlet, self).update()
        self.snippet_url = self.context.getField('snippetURL').get(self.context)
        self.username    = self.context.getField('snippetUsername').get(self.context)
        self.password    = self.context.getField('snippetPassword').get(self.context)
        self.expression  = self.context.getField('snippetExpression').get(self.context)
        self.support_cookies = self.context.getField('snippetSupportCookies').get(self.context)

    def getSource(self):
        url = self.snippet_url
        if url:
            error = None
            req = urllib2.Request(url)
            try:
                username = self.username
                password = self.password
                if username and password:
                    if self.support_cookies:
                        req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')                          
                        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
                        req.add_header("Authorization", "Basic %s" % base64string)   
                        cj = cookielib.CookieJar()  
                        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))  
                        urllib2.install_opener(opener)  
                        response = urllib2.urlopen(req)
                    else:
                        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
                        passman.add_password(None, url, username, password)
                        authhandler = urllib2.HTTPBasicAuthHandler(passman)
                        opener = urllib2.build_opener(authhandler)
                        urllib2.install_opener(opener)
                        response = urllib2.urlopen(req)
                else:
                    response = urllib2.urlopen(req)
            except urllib2.HTTPError, e:
                error = (_(u'HTTP Error'), e.code)
            except urllib2.URLError, e:
                error = (_(u'URL Error'), '%s - %s' % (e.reason[0], e.reason[1]))
            else:
                data = response.read()
                expression = self.expression
                if expression:
                    PATTERN = re.compile(expression, re.IGNORECASE | re.DOTALL)
                    result = PATTERN.match(data)
                    return result and result.group(1) or None
                else:
                    return data

            return '<dl class="portalMessage error"><dt>%s</dt><dd>%s</dd></dl>' % (error[0], error[1])
