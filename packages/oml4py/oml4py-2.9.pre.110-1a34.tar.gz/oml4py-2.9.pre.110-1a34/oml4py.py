# 
# Description: Python Class for OML Connection and Data Uploading
#
# From http://oml.mytestbed.net/projects/oml/wiki/Description_of_Text_protocol
#
# The client opens a TCP connection to an OML server and then sends a header 
# followed by a sequence of measurement tuples. The header consists of a 
# sequence of key, value pairs terminated by a new line. The end of the header 
# section is identified by an empty line. Each measurement tuple consists of 
# a new-line-terminated string which contains TAB-separated text-based 
# serialisations of each tuple element. Finally, the client ends the session 
# by simply closing the TCP connection.
#
# Author: Fraida Fund
#
# Date: 08/06/2012
#

import sys
import os
import socket
from time import time
from time import sleep

# Compatibility with Python 2 and 3's string type
if float(sys.version[:3])<3:
    def to_bytes(s):
        return s
else:
    def to_bytes(s):
        return bytes(s, "UTF-8")


class OMLBase:
    """
    This is a Python OML class
    """

    VERSION = "2.9.pre.110-1a34"
    VERSION_STRING = ("OML4Py Client V2.9.pre.110-1a34")
    COPYRIGHT = "Copyright 2012, NYU-Poly, Fraida Fund"
    PROTOCOL = 1

    def _banner(self):
        sys.stderr.write("INFO\t%s [Protocol V%d] %s\n" % (self.VERSION_STRING, self.PROTOCOL, self.COPYRIGHT))

    def __init__(self,appname,expid=None,sender=None,uri="tcp:localhost:3003"):
        self._banner()

        self.oml = True

        # Set all the instance variables
        self.appname = appname
        if self.appname[:1].isdigit() or '-' in self.appname or '.' in self.appname:
          sys.stderr.write("ERROR\tInvalid app name: %s\n" %  self.appname)
          self.oml = False

        if expid is None:
          try:
            self.expid = os.environ['OML_EXP_ID']
          except KeyError:
            self.oml = False
        else:
          self.expid = expid

        if uri is None:
          try:
            uri_l = os.environ['OML_SERVER'].split(":")
          except KeyError:
            self.oml = False
        else:
          uri_l = uri.split(":")

        try:
          self.omlserver = uri_l[1]
          self.omlport = int(uri_l[2])
        except NameError:
          self.oml = False
        except IndexError:
          self.oml = False

        if sender is None:
          try:
            self.sender =  os.environ['OML_NAME']
          except KeyError:
            self.oml = False
        else:
          self.sender = sender

        self.starttime = 0

        if self.oml:        
          # Set socket
          self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          self.sock.settimeout(5) 
          self.streams = 0
          self.schema = ""
          self.nextseq = {}
          self.streamid = {}


    def addmp(self,mpname,schema):
 
      if self.oml:
        if "-" in mpname or "." in mpname:
          sys.stderr.write("ERROR\tInvalid measurement point name: %s\n" %  mpname)
          self.oml = False

        else:
          # Count number of streams
          self.streams += 1

          if self.streams > 1:
             self.schema += '\n'

          str_schema = "schema: " + str(self.streams) + " " + self.appname + "_" + mpname + " " + schema

          self.schema += str_schema
          self.nextseq[mpname] = 0
          self.streamid[mpname] = self.streams
   

    def start(self):

      if self.oml:        
        # Use socket to connect to OML server
        try:
          self.sock.connect((self.omlserver,self.omlport))
          self.sock.settimeout(None)
  
          self.starttime = int(time())

          header = "protocol: 1" + '\n' + "experiment-id: " + str(self.expid) + '\n' + \
                 "start-time: " + str(self.starttime) + '\n' + "sender-id: " + str(self.sender) + '\n' + \
                 "app-name: " + str(self.appname) + '\n' + \
                 str(self.schema) + '\n' + "content: text" + '\n' + '\n'    
    
          self.sock.send(to_bytes(header))
          sys.stderr.write("INFO\tCollection URI is tcp:%s:%d\n" % (self.omlserver,self.omlport))
        except socket.error as e:
          sys.stderr.write("ERROR\tCould not connect to OML server: %s\n" %  e)
          self.oml = False
          sys.stderr.write("ERROR\tOML disabled\n")
      else:
        sys.stderr.write("ERROR\tOML disabled\n")


    def close(self):
      streamid = None

      if self.oml:
        self.sock.close()


    def inject(self,mpname,values):

      if self.oml:        
        # Inject data into OML 

        if self.starttime == 0:
            sys.stderr.write("ERROR\tDid not call start()\n")
            self.oml = False
        else:
          timestamp = time() - self.starttime
          try:
            streamid = self.streamid[mpname]
            seqno = self.nextseq[mpname]
            str_inject = str(timestamp) + '\t' + str(streamid) + '\t' + str(seqno)

            try:
              for item in values:
                str_inject += '\t'
                str_inject += str(item)
              str_inject += '\n'
              self.sock.send(to_bytes(str_inject))
              self.nextseq[mpname]+=1
            except TypeError:
              sys.stderr.write("ERROR\tInvalid measurement list\n")
          except KeyError:
            sys.stderr.write("ERROR\tTried to inject into unknown MP '%s'\n" % mpname)
    
      else:
        timestamp = time() - self.starttime
        str_inject = str(timestamp) + '\t'
        try:
          for item in values:
              str_inject += '\t'
              str_inject += str(item)
          str_inject += '\n'
          sys.stdout.write(str_inject)
        except TypeError:
          sys.stderr.write("ERROR\tInvalid measurement list\n")

