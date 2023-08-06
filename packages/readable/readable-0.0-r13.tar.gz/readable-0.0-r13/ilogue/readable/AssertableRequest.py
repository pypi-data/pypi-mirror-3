from mock import Mock, sentinel
from urllib2 import urlopen, HTTPError, URLError
#from urllib import urlencode
from time import sleep
from BeautifulSoup import BeautifulSoup
from ilogue.dialogue.testutils.AssertablePage import AssertablePage
#from shortuuid import uuid as shortuuid
#from ilogue.readable.AssertableFileDownload import AssertableFileDownload


class AssertableRequest(object):
    server = None
    ROOT = 'http://0.0.0.0:6543'
    MAXATTEMPTS = 10
    ATTEMPTPAUSE = 0.2


    def get(self, url):
        page = self.tryUrlOpen(url)
        return AssertablePage(page[:8192])

#    def post(self, url, data):
#        data = urlencode(data)
#        return self.tryUrlOpen(url, data)

#    def viewFor(self, *resource):
#        page = self.get(_url(*resource))
#        return assertResponse(None,content=page)

#    def viewAt(self, url):
#        page = self.get(url)
#        return assertResponse(None,content=page)

#    def fileAt(self, url):
#        return self.tryDownloadFileAt(url)

#    def expectedErrorForRequest(self, url, data=None):
#        page = self.tryUrlErrorOpen(url, data)
#        return assertResponse(None,content=page)

#    def tryDownloadFileAt(self, url):
#        url = self.absolute(url)
#        for connectAttempts in range(1,self.MAXATTEMPTS):
#            try:
#                response = urlopen(url)
#                #if successful, return response string
#                return self.responseToAssertableFileDownload(response)
#            # an http error is a meaningful failure:
#            except HTTPError as httpErr:
#                traceback = self.tryGetTraceback(httpErr)
#                raise AssertionError(str(httpErr)+traceback)
#            #if we got our connection refused, do nothing and try again:
#            except URLError as urlErr:
#                if not 'Connection refused' in urlErr.reason:
#                    raise urlErr
#            sleep(self.ATTEMPTPAUSE)

#    def responseToAssertableFileDownload(self, response):
#        filename = '/tmp/test_ploy_filedwnl_'+shortuuid()+'.tmp'
#        self.readResponseToFile(response, filename)
#        return AssertableFileDownload(response,filename)

#    def readResponseToFile(self, response, localFile):
#        CHUNK = 16 * 1024
#        with open(localFile, 'wb') as fp:
#          while True:
#            chunk = response.read(CHUNK)
#            if not chunk: break
#            fp.write(chunk)


    # attempt add debug view to HTTPError
    def tryUrlOpen(self, url, data=None):
        url = self.absolute(url)
        for connectAttempts in range(1,self.MAXATTEMPTS):
            try:
                response = urlopen(url, data)
                #if successful, return response string
                return response.read()
            # an http error is a meaningful failure:
            except HTTPError as httpErr:
                traceback = self.tryGetTraceback(httpErr)
                raise AssertionError(str(httpErr)+traceback)
            #if we got our connection refused, do nothing and try again:
            except URLError as urlErr:
                if not 'Connection refused' in urlErr.reason:
                    raise urlErr
            sleep(self.ATTEMPTPAUSE)
        else:
            raise urlErr

#    def tryUrlErrorOpen(self, url, data=None):
#        url = self.absolute(url)
#        for connectAttempts in range(1,self.MAXATTEMPTS):
#            try:
#                urlopen(url, data)
#                #if successful, throw assertionError
#                raise AssertionError('Expected error, got normal http response.')
#            # an http error is expected:
#            except HTTPError as httpErr:
#                return (httpErr.read() or '')
#            #if we got our connection refused, do nothing and try again:
#            except URLError as urlErr:
#                if not 'Connection refused' in urlErr.reason:
#                    raise urlErr
#            sleep(self.ATTEMPTPAUSE)

    # try to get the server internal traceback from the HTTP response content
    def tryGetTraceback(self, httpError):
        trace = '  '
        try:
            content = httpError.read()
            soup = BeautifulSoup(content)
            textVersionDivs = soup.findAll("div",id="short_text_version")
            if textVersionDivs:
                area = textVersionDivs[0].textarea
                trace += area.string
            else:
                trace += '[No Pyramid traceback found]'
        except Exception as err:
            trace += str(err)
        return trace

    # make an url absolute if it is relative
    def absolute(self, url):
        if url[0] == '/':
            url = self.ROOT + url
        return url

if __name__ == '__main__':
    print(__doc__)

