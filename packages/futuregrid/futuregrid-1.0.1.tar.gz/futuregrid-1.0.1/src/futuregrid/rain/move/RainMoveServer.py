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
Description: Server to interact with users. This contains the Fugang Functionality and calls RainMoveServerSites.py to do the real operations.
"""
__author__ = 'Javier Diaz'

from types import *
import re
import logging
import logging.handlers
import random
from random import randrange
import os
import sys
import socket, ssl
from multiprocessing import Process
from subprocess import *
import time

from futuregrid.image.repository.client.IRServiceProxy import IRServiceProxy
from futuregrid.utils.FGTypes import FGCredential
from futuregrid.utils import FGAuth
from futuregrid.rain.RainServerConf import RainServerConf

class RainMoveServerSites(object):

    def __init__(self):
        super(RainMoveServerSites, self).__init__()
        
               
        self.numparams = 4
        

        #load from config file
        self.rainMoveConf = RainServerConf()
        self.rainMoveConf.load_registerServerIaasConfig() 
        
        self.port = self.rainMoveConf.getPortRainMove()
        self.log_filename = self.rainMoveConf.getLogRainMove()
        self.logLevel = self.rainMoveConf.getLogLevelRainMove()
        
        self._ca_certs = self.rainMoveConf.getCaCertsRainMove()
        self._certfile = self.rainMoveConf.getCertFileRainMove()
        self._keyfile = self.rainMoveConf.getKeyFileRainMove()
        
        
        print "\nReading Configuration file from " + self.rainMoveConf.getConfigFile() + "\n"
        
        self.logger = self.setup_logger("")
        
        #Image repository Object
        verbose = False
        printLogStdout = False
        self._reposervice = IRServiceProxy(verbose, printLogStdout)
        
    def setup_logger(self, extra):
        #Setup logging        
        logger = logging.getLogger("RainMoveServer" + extra)
        logger.setLevel(self.logLevel)    
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler = logging.FileHandler(self.log_filename)
        handler.setLevel(self.logLevel)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False #Do not propagate to others
        
        return logger

    def auth(self, userCred):
        return FGAuth.auth(self.user, userCred) 

    def checkUserStatus(self, userId, passwd, userIdB):
        """
        return "Active", "NoActive", "NoUser"; also False in case the connection with the repo fails
        """
        if not self._reposervice.connection():
            msg = "ERROR: Connection with the Image Repository failed"
            self.logger.error(msg)
            return False
        else:
            self.logger.debug("Checking User Status")
            status= self._reposervice.getUserStatus(userId, passwd, userIdB)
            self._reposervice.disconnect()
            
            return status

    def start(self): 
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', self.port))
        sock.listen(1)
        self.logger.info('Starting Server on port ' + str(self.port))
        
        proc_list = []
        total_count = 0
        while True:        
            if len(proc_list) == self.proc_max:
                full = True
                while full:
                    for i in range(len(proc_list) - 1, -1, -1):
                        #self.logger.debug(str(proc_list[i]))
                        if not proc_list[i].is_alive():
                            #print "dead"                        
                            proc_list.pop(i)
                            full = False
                    if full:
                        time.sleep(self.refresh_status)
            
            total_count += 1
            #channel, details = sock.accept()
            newsocket, fromaddr = sock.accept()
            connstream = 0
            try:
                connstream = ssl.wrap_socket(newsocket,
                              server_side=True,
                              ca_certs=self._ca_certs,
                              cert_reqs=ssl.CERT_REQUIRED,
                              certfile=self._certfile,
                              keyfile=self._keyfile,
                              ssl_version=ssl.PROTOCOL_TLSv1)
                #print connstream                                
                proc_list.append(Process(target=self.process_client, args=(connstream, fromaddr[0])))            
                proc_list[len(proc_list) - 1].start()
            except ssl.SSLError:
                self.logger.error("Unsuccessful connection attempt from: " + repr(fromaddr))
                self.logger.info("Rain Server Move Request DONE")
            except socket.error:
                self.logger.error("Error with the socket connection")
                self.logger.info("Rain Server Move Request DONE")
            except:
                self.logger.error("Uncontrolled Error: " + str(sys.exc_info()))
                if type(connstream) is ssl.SSLSocket: 
                    connstream.shutdown(socket.SHUT_RDWR)
                    connstream.close() 
                self.logger.info("Rain Server Move Request DONE")
                
    def process_client(self, connstream, fromaddr):
        start_all = time.time()
        self.logger = self.setup_logger("." + str(os.getpid()))        
        self.logger.info('Accepted new connection')
        
        #receive the message
        data = connstream.read(2048)
        self.logger.debug("msg received: " + data)
        params = data.split(',')
        #print data
        #params[0] is infrastructure name.
        #params[1] is the user
        #params[2] is the user password
        #params[3] is the type of password
        
        infrastructure = params[0].strip()
        
        #MORE PARAMETERS ARE NEEDED
        #operation site, infrastructure origin, infrastructure destination, number machines,
                
        self.user = params[1].strip()
        passwd = params[2].strip()
        passwdtype = params[3].strip()
                       
        if len(params) != self.numparams:
            msg = "ERROR: incorrect message"
            self.errormsg(connstream, msg)
            return

        retry = 0
        maxretry = 3
        endloop = False
        while (not endloop):
            if not self.checknopasswd(fromaddr):
                userCred = FGCredential(passwdtype, passwd)
                if (self.auth(userCred)):# contact directly with LDAP
                    #check the status of the user in the image repository. 
                    #This contacts with image repository client to check its db. The user an password are OK because this was already checked.
                    userstatus = self.checkUserStatus(self.user, passwd, self.user)      
                    if userstatus == "Active":
                        connstream.write("OK")                    
                    elif userstatus == "NoActive":
                        connstream.write("NoActive")
                        msg = "ERROR: The user " + self.user + " is not active"
                        self.errormsg(connstream, msg)
                        return                    
                    elif userstatus == "NoUser":
                        connstream.write("NoUser")
                        msg = "ERROR: The user " + self.user + " does not exist"
                        self.logger.error(msg)
                        self.logger.info("IaaS register server Request DONE")
                        return
                    else:
                        connstream.write("Could not connect with image repository server")
                        msg = "ERROR: Could not connect with image repository server to verify the user status"
                        self.logger.error(msg)
                        self.logger.info("IaaS register server Request DONE")
                        return
                    endloop = True
                else:
                    retry += 1
                    if retry < maxretry:
                        connstream.write("TryAuthAgain")
                        passwd = connstream.read(2048)
                    else:
                        msg = "ERROR: authentication failed"
                        endloop = True
                        self.errormsg(connstream, msg)
                        return
            else:
                connstream.write("OK")
                endloop = True
        
        #DO STUFFS
        #Fugang Functionality  
