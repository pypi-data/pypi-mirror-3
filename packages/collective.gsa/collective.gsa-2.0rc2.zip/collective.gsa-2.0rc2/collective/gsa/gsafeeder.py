import mechanize
import codecs
import os
import sys
from daemon.runner import DaemonRunner
import time
from collective.gsa.utils import encode_multipart_formdata, \
        safe_unicode

class Feeder(object):

    def __init__(self, host, source, path):
        self.stdin_path = "/dev/null"
        self.stdout_path = "var/log/gsa.log"
        self.stderr_path = "var/log.gsa.err"
        self.pidfile_path = os.path.abspath('var/gsa.pid')
        self.pidfile_timeout = 1

        self.host = host
        self.source = source
        self.path = path

        self.encoder = codecs.getencoder('utf-8')

    def sendFile(self, filename):
        with open(filename, "r") as xmlfile:
            xml = safe_unicode(xmlfile.read())

        body, headers = self.prepareRequest(xml)

        url = "http://%s" % self.host

        try:
            request = mechanize.Request('%s/xmlfeed' % self.encoder(url)[0], self.encoder(body)[0], headers)
            res = mechanize.urlopen(request, timeout=1)
            data = res.read()
            res.close()

            if data != "Success":
                raise RuntimeError(data)

            print "Successfully sent: %s" % filename
        except Exception, e:
            print e
            pass
        else:
            try:
                os.remove(filename)
            except IOError, e:
                print e

    def prepareRequest(self, xml):
        feedtype = u'incremental'
        datasource = safe_unicode(self.source)
        params = []

        params.append(("feedtype", feedtype))
        params.append(("datasource", datasource))
        data=('data','xmlfilename',xml)

        content_type, body = encode_multipart_formdata(params, (data,))

        headers = {}
        headers['Content-type']=content_type.encode('utf-8')

        return body, headers

    def run(self):
        print "Start processing..."

        while True:
            for fname in os.listdir(self.path):
                if not fname.endswith('.gsa'):
                    continue

                self.sendFile(os.path.join(self.path, fname))

            sys.stdout.flush()
            time.sleep(1)


def main(host, source, path, argv=sys.argv, write=sys.stdout.write):
    feeder = Feeder(host, source, path)

    import pdb; pdb.set_trace()
    
    #debug
    feeder.run()

    #runner = DaemonRunner(feeder)
    #runner.parse_args()
    #runner.do_action()

if __name__ == '__main__':
    main()
