#!/usr/bin/env python
#
# Copyright (c) 2010, Janrain, Inc.
#  
#  All rights reserved.
#  
#  Redistribution and use in source and binary forms, with or without modification,
#  are permitted provided that the following conditions are met:
#  
#  * Redistributions of source code must retain the above copyright notice, this
#      list of conditions and the following disclaimer. 
#  * Redistributions in binary
#      form must reproduce the above copyright notice, this list of conditions and the
#      following disclaimer in the documentation and/or other materials provided with
#      the distribution. 
#  * Neither the name of the Janrain, Inc. nor the names of its
#      contributors may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#  ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 


import urllib
import urllib2
import logging

import os
from google.appengine.ext.webapp import template

import cgi

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from django.utils import simplejson

import Cookie


class UserLogin(db.Model):
    identifier = db.StringProperty(multiline=False)
    date = db.DateTimeProperty(auto_now_add=True)


class MainHandler(webapp.RequestHandler):
    
    def get(self):
               path = os.path.join(os.path.dirname(__file__), 'index.html')
               self.response.out.write(template.render(path, 0))


class Login(webapp.RequestHandler):
    def get(self):
        logging.debug('get method')
        self.post()
        
    def post(self):
            logging.debug('popopsfost')
            # Step 1) Extract the token from your environment. If you are using app 
            # engine, you'd do something like:
            token = self.request.get('token')
        
            # Step 2) Now that we have the token, we need to make the api call to 
            # auth_info.  auth_info expects an HTTP Post with the following paramters:
            api_params = {
                'token': token,
                #'apiKey': 'c4daf6a6c91f0c3a795325d750f246e20f872cbd',
                'apiKey': '03069caa4f4bade32946e42809cd811d59abf52a',
                'format': 'json',
            }
            
            http_response = urllib2.urlopen('http://10.0.1.140:8080/api/v2/auth_info',
                                            urllib.urlencode(api_params))
            response = http_response.read()

            # print response
            # logging.error('post ' + response)

            auth_info = simplejson.loads(response)
            profile = auth_info['profile']
   
            # 'identifier' will always be in the payload. This is the
            # unique identifier that you use to sign the user in to your site
            identifier = profile['identifier']
   
            # Create a user object and store it in your datastore
            userLogin = UserLogin()
            userLogin.identifier = identifier
            userLogin.put()

            # Create a cookie with the identifier to send to the iPhone app
            cookie = Cookie.SimpleCookie()
            
            # Set the sid in the cookie
            cookie['sid'] = identifier
            
            # Will expire in two weeks
            cookie['sid']['expires'] = 14 * 24 * 60 * 60
            cookie['sid']['path'] = "/"
            # cookie['sid']['domain'] = "jrtokentest.appspot.com"
            cookie['sid']['domain'] = "nathan-mac.janrain.com"

            self.response.headers.add_header('Set-Cookie', cookie['sid'].OutputString())
            # self.response.out.write(response)
            self.response.out.write('<html><head>' +
#                                    '<script type="text/javascript" charset="utf-8" src="http://nathan-mac.janrain.com:8081/target/target-script-min.js"></script>' +
#                                    '<script type="text/javascript" src="' + self.request.get('pgsrc') + '"></script>' +
#                                    '''
#                                    <script type="text/javascript">
#                                    PhoneGap = {};
#                                    commandQueue = [];
#                                    command = {
#                                        className: "com.phonegap.debugconsole",
#                                        methodName: "log",
#                                        arguments: ["INVALID", "asdf"],
#                                        options: { logLevel:"INFO" }
#                                    };
#                                    commandQueue.push(JSON.stringify(command));
#                                    PhoneGap.getAndClearQueuedCommands = function () {
#                                        var json = JSON.stringify(commandQueue);
#                                        commandQueue = [];
#                                        return json;
#                                    };
#                                    gapBridge = document.createElement("iframe");
#                                    gapBridge.setAttribute("style", "display:none;");
#                                    gapBridge.setAttribute("height","0px");
#                                    gapBridge.setAttribute("width","0px");
#                                    gapBridge.setAttribute("frameborder","0");
#                                    document.documentElement.appendChild(gapBridge);
#                                    PhoneGap.gapBridge = gapBridge;
#                                    PhoneGap.gapBridge.src = "gap://ready";
#
#                                    </script>
#                                    ''' +
                                    '</head><body>' + response +
#                                    '<br/>' + self.request.get('pgsrc') +
                                    '</body></html>')
            # self.redirect("file://index.html")
            # self.redirect("/")
            self.response.set_status(302)
            self.response.headers.add_header('location', self.request.get('redirect'))

class TwoOhFour(webapp.RequestHandler):
    def get(self):
        self.response.set_status(204)

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/login', Login),
                                          ('/two-oh-four', TwoOhFour)],
                                            debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
