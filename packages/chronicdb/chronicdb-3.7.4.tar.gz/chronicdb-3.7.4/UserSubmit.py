#!/usr/bin/python
#
# Copyright (C) LoomCM Inc. 2010 for ChronicDB
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import logging
import socket
import os
import sys
try:
    import ssl
except ImportError:
    print("You need python2.6 or higher.")
    sys.exit(1)
try:
    import simplejson as json
except ImportError:
    import json


class UserSubmit:

    user_ssl_socket = None
    user_socket = None
    user_server=""
    user_port=""
    logger = logging.getLogger("ChronicDB.UserSubmit")
    
    def __init__(self,server,port):
        self.user_server = server
        self.user_port = port

    def connect(self):
        self.logger.debug("Connecting to " + self.user_server + " port " + self.user_port)
        self.user_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Be safe. Require a certificate from the server, and only
        # trust THIS list of certificate signing authorities. Just
        # like browsers trust only a specific list of certificate
        # signing authorities.
        cert = os.path.dirname(__file__) + "/chronicdb_trusted_certificate_authorities.crt"
        self.user_ssl_socket = ssl.wrap_socket(self.user_socket,
                                               ca_certs=cert,
                                               cert_reqs=ssl.CERT_REQUIRED)
        
        self.user_ssl_socket.connect((self.user_server, int(self.user_port)))

    def communicate(self,arguments):
        # Run in a REPL. This is as secure as using your browser. And
        # it runs over SSL, which is often more secure than using your
        # e-mail client and mobile phone.
        submission = dict()
        submission['from_user'] = []
        # Using the full path to the utility would be a violation of
        # user privacy, so don't do that.
        submission['from_user'] += arguments[1:]
        send_string = json.dumps(submission)
        self.user_ssl_socket.send(send_string)
        more = 1
        counter = 1
        ret = None
        while more != 0:
            self.logger.debug("Running command " + str(counter))
            response = json.loads(self.user_ssl_socket.recv(1024*128))
            self.logger.debug("communicate response: " + str(response))
            exec(response)
            counter += 1
        return ret
    
    def close(self):
        self.user_ssl_socket.close()
        self.user_socket.close()
