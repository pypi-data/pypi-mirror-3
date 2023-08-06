#!/usr/bin/env python
# -------------------------------------------------------------------------- #
# Copyright 2010-2011, Indiana University                                    #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License"); you may    #
# not use this file except in compliance with the License. You may obtain    #
# a copy of the License at                                                   #
#                                                                            #
# http://www.apache.org/licenses/LICENSE-2.0                                 #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
# -------------------------------------------------------------------------- #
"""
Description: Client that users will use. This is fg-move
"""
__author__ = 'Javier Diaz'

import argparse
from types import *
import re
import logging
import logging.handlers
import glob
import random
import os
import sys
import socket, ssl
from subprocess import *
import textwrap
#from xml.dom.ext import *
#from xml.dom.minidom import Document, parse
import time
from getpass import getpass
import hashlib

from futuregrid.rain.RainClientConf import RainClientConf
from futuregrid.utils import fgLog

class RainMoveClient(object):
    def __init__(self):
        super(RainMoveClient, self).__init__()
        
        
        
        #Load Configuration from file
        self._genConf = IMClientConf()
        self._genConf.load_generationConfig()        
        self.serveraddr = self._genConf.getServeraddr()
        self.rainmove_port = self._genConf.getGenPort()
        
        self._ca_certs = self._genConf.getCaCertsGen()
        self._certfile = self._genConf.getCertFileGen()
        self._keyfile = self._genConf.getKeyFileGen()
        
        self._log = fgLog.fgLog(self._genConf.getLogFileGen(), self._genConf.getLogLevelGen(), "GenerateClient", printLogStdout)


    def check_auth(self, socket_conn, checkauthstat):
        endloop = False
        passed = False
        while not endloop:
            ret = socket_conn.read(1024)
            if (ret == "OK"):
                if self._verbose:
                    print "Authentication OK. Your image request is being processed"
                self._log.debug("Authentication OK")
                endloop = True
                passed = True
            elif (ret == "TryAuthAgain"):
                msg = "ERROR: Permission denied, please try again. User is " + self.user                    
                self._log.error(msg)
                if self._verbose:
                    print msg                            
                m = hashlib.md5()
                m.update(getpass())
                passwd = m.hexdigest()
                socket_conn.write(passwd)
                self.passwd = passwd
            elif ret == "NoActive":
                msg="ERROR: The status of the user "+ self.user + " is not active"
                checkauthstat.append(str(msg))
                self._log.error(msg)
                #if self._verbose:
                #    print msg            
                endloop = True
                passed = False          
            elif ret == "NoUser":
                msg="ERROR: User "+ self.user + " does not exist"
                checkauthstat.append(str(msg))
                self._log.error(msg)
                #if self._verbose:
                #    print msg + " WE"  
                endloop = True
                passed = False
            else:                
                self._log.error(str(ret))
                #if self._verbose:
                #    print ret
                checkauthstat.append(str(ret))
                endloop = True
                passed = False
        return passed

    def move(self):
        start_all = time.time()
        #generate string with options separated by | character
        output = None
        checkauthstat = []
        #params[0] is user
        #params[8] is the user password
        #params[9] is the type of password
       
        #TODO: DEFINE options       
        
        options = str(self.user) + "|" + str(self.OS) + "|" + str(self.version) + "|" + str(self.arch) + "|" + \
                str(self.software) + "|" + str(self.givenname) + "|" + str(self.desc) + "|" + str(self.getimg) + \
                "|" + str(self.passwd) + "|ldappassmd5|" + str(self.baseimage) + "|"+ str(self.scratch) + "|" + str(self.size)

        
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            rainMoveServer = ssl.wrap_socket(s,
                                        ca_certs=self._ca_certs,
                                        certfile=self._certfile,
                                        keyfile=self._keyfile,
                                        cert_reqs=ssl.CERT_REQUIRED,
                                        ssl_version=ssl.PROTOCOL_TLSv1)
            self._log.debug("Connecting server: " + self.serveraddr + ":" + str(self.rainmove_port))
            if self._verbose:
                print "Connecting server: " + self.serveraddr + ":" + str(self.rainmove_port)
            rainMoveServer.connect((self.serveraddr, self.rainmove_port))            
        except ssl.SSLError:
            self._log.error("CANNOT establish SSL connection. EXIT")
            if self._verbose:
                print "ERROR: CANNOT establish SSL connection. EXIT"

        rainMoveServer.write(options)
        #check if the server received all parameters
        if self._verbose:
            print "Your request is in the queue to be processed after authentication"
                
        if self.check_auth(rainMoveServer, checkauthstat):
            if self._verbose:
                print "Moving resources"
            ret = rainMoveServer.read(2048)
            
            if (re.search('^ERROR', ret)):
                self._log.error('The image has not been generated properly. Exit error:' + ret)
                if self._verbose:
                    print "ERROR: The image has not been generated properly. Exit error:" + ret    
            else:
                self._log.debug("Returned string: " + str(ret))
                
                if self.getimg:            
                    output = self._retrieveImg(ret, "./")                    
                    rainMoveServer.write('end')
                else:
                    
                    if (re.search('^ERROR', ret)):
                        self._log.error('The image has not been generated properly. Exit error:' + ret)
                        if self._verbose:
                            print "ERROR: The image has not been generated properly. Exit error:" + ret
                    else:
                        self._log.debug("The image ID is: " + str(ret))
                        output = str(ret)
        else:       
            self._log.error(str(checkauthstat[0]))
            if self._verbose:
                print checkauthstat[0]
            return
        
        end_all = time.time()
        self._log.info('TIME walltime image generate client:' + str(end_all - start_all))
        
        #server return addr of the img and metafile compressed in a tgz, imgId or None if error
        return output


def extra_help():
   msg = "Useful information about the software. Currently, we do not parse the packages names provided within the -s/--software option" +\
         "Therefore, if some package name is wrong, it won't be installed. Here we provide a list of useful packages names from the official repositories: \n" +\
         "CentOS: mpich2, python26, java-1.6.0-openjdk. More packages names can be found in http://mirror.centos.org/ \n" +\
         "Ubuntu: mpich2, openjdk-6-jre, openjdk-6-jdk. More packages names can be found in http://packages.ubuntu.com/ \n\n" +\
         "FutureGrid Performance packages (currently only for CentOS 5): fg-intel-compilers, intel-compilerpro-common, " +\
         "intel-compilerpro-devel, intel-compilerproc, intel-compilerproc-common, intel-compilerproc-devel " +\
         "intel-compilerprof, intel-compilerprof-common, intel-compilerprof-devel, intel-openmp, intel-openmp-devel, openmpi-intel"
   return msg
   
def main():

    parser = argparse.ArgumentParser(prog="fg-move", formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="FutureGrid Rain Move Help",
                                     epilog=textwrap.dedent(extra_help()))    
    parser.add_argument('-u', '--user', dest='user', required=True, help='FutureGrid User name')
    parser.add_argument('-d', '--debug', dest='debug', action="store_true", help='Print logs in the screen for debug')
    parser.add_argument('--nopasswd', dest='nopasswd', action="store_true", default=False, help='If this option is used, the password is not requested. This is intended for systems daemons like Inca')
    
    args = parser.parse_args()

    print 'FG-move client...'
    
    verbose = True

    if args.nopasswd == False:    
        print "Please insert the password for the user " + args.user + ""
        m = hashlib.md5()
        m.update(getpass())
        passwd = m.hexdigest()
    else:        
        passwd = "None"
    
        
    fgmove = RainMoveClient()
    status = fgmove.move()
    
    print status


if __name__ == "__main__":
    main()




