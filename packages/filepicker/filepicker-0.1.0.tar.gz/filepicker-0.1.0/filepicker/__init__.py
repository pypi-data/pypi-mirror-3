import requests
import urllib

OPENURL = 'http://www.filepicker.io/open/'
SAVEASURL = 'http://www.filepicker.io/saveas/'

class Filepicker():
    def setKey(self, key):
        self.key = key

    def __init__(self, key):
        self.key = key

    def getFileContents(self, fpurl):
        r = requests.get(fpurl)
        return r.content

    def saveDataToFile(self, fpurl, data):
        try:
            r = requests.post(fpurl, data=data)
        except Exception:
            return False
        if r.status_code == requests.codes.ok:
            return True
        else:
            return False

    def getFile(self, callbackurl, mimetypes='*/*', options=None, id=0):
        if not self.key:
            raise Exception("API Key not found. Use with filepicker.setKey()")

        return OPENURL + '?redirect_url=%s&id=%s&m=%s&key=%s' % (urllib.quote(callbackurl), 
                urllib.quote(id),
                urllib.quote(mimetypes),
                urllib.quote(self.key))
