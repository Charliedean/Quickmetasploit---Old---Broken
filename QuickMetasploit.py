#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from collections import defaultdict
from ConfigParser import SafeConfigParser
import cmd 
import subprocess
import sys
import time
import socket
import fcntl
import struct
import math
import random
import blessings
import string

term = blessings.Terminal() # terminal size
width = term.width
config = SafeConfigParser()
config.read('config.ini')
DEFAULT_MODULE = config.get('main', 'Module')
DEFAULT_PAYLOAD = config.get('main' , 'Payload')
DEFAULT_LPORT = config.get('main' , 'Lport')

COLOURS = ['\033[94m', '\033[92m', '\033[93m', '\033[91m', '\033[0m']

class colours:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[0m'


def get_ip_address(ifname): # Gets ip from interface using sockets
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack(b'256s', ifname[:15])
    )[20:24])

default_variables = frozenset('iface module defaultmodule defaultpayload defaultlport'.split())

module_variables = defaultdict(lambda : default_variables)

module_variables.update({module: default_variables | other_variables for module, other_variables in
    {'exploit/multi/handler': {'payload', 'lhost', 'lport'},
    'auxiliary/scanner/smb/smb_login': {'rhosts', 'rport'},
    'auxiliary/scanner/rservices/rlogin_login': {'rhosts', 'rport', 'username', 'fromuser'},
    'auxiliary/scanner/snmp/snmp_enum': {'rhosts', 'rport', 'snmpversion', 'community'}
    }.items()})

short_module_names = {'smb_login': 'auxiliary/scanner/smb/smb_login',
                      'multi_handler': 'exploit/multi/handler',
                      'rlogin_login': 'auxiliary/scanner/rservices/rlogin_login',
                      'snmp_enum': 'auxiliary/scanner/snmp/snmp_enum'
                     }

class Handler(cmd.Cmd):
    lport = DEFAULT_LPORT
    payload = DEFAULT_PAYLOAD
    lhost = ''
    iface = b'eth0'
    module = short_module_names[DEFAULT_MODULE]
    rhosts = ''
    rhost = ''
    rport = ''
    username = ''
    fromuser = 'root'
    community = 'public'
    snmpversion = '1'
    defaultlport = config.get('main', 'Lport')
    defaultmodule = config.get('main', 'Module')
    defaultpayload = config.get('main', 'Payload')
    possible_modules = short_module_names.keys()
    possible_snmpversion = ('1' ,'2c')
    possible_community = ('public' , 'private' , 'admin' , 'CISCO' , 'system' , 'switch' , 'secret')
    possible_usernames = ('foobar' , 'root' , 'admin' , 'sysadmin')
    possible_payloads = ('windows/meterpreter/reverse_tcp' , 'linux/shell/revserse_tcp')
    possible_iface = ('eth0', 'lo' , 'wlan0')

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.lhost = get_ip_address(self.iface)
        self.variables = module_variables[self.module]

    def do_set(self, line):
        """Use Tab To Show Variables You Can Set"""
        try:
            firstvalue, secondvalue = line.split()
            if firstvalue == 'module':
                module = secondvalue = short_module_names[secondvalue]
                self.variables = module_variables[module]
            elif firstvalue == 'iface':
                iface = secondvalue
                self.lhost = get_ip_address(iface)
            setattr(self, firstvalue, secondvalue)
            config.set('main' , 'Module' , self.defaultmodule)
            config.set('main' , 'Payload' , self.defaultpayload)
            config.set('main' , 'Lport' , self.defaultlport)

        except ValueError:
            print colours.RED + "="*term.width                                       + colours.WHITE
            print colours.BLUE + "Please choose a option and a value to set!".center(width, ' ')        + colours.WHITE
            print colours.RED + "="*term.width                                       + colours.WHITE

    def do_easteregg(self, line):
        easter = raw_input("Enter The Code: ")
        counter = 0
        while True:
            if easter == "1337":
                print " "*(49 - int(46*math.sin(counter))) + random.choice(COLOURS) + "**--CharlieDean--**--Dario--**--Alex--**" + '\033[0m'
                print " "*(49 - int(-46*math.sin(counter))) + random.choice(COLOURS) + "**--CharlieDean--**--Dario--**--Alex--**" + '\033[0m'
                time.sleep(0.01)
                counter += 0.1
            else:
                print "Wrong Code!"

    def do_listallpayloads(self, line):
        """Shows All The Avalible Payloads"""
        subprocess.call(["msfcli", "multi/handler", "P"])

    def do_exit(self, line):
        """Exits Program"""
        sys.exit()

    def complete_set(self, text, line, begidx, endidx):
        cmdtokens = line.split(' ')[:-1]
        if cmdtokens == ['set']:
            return [v for v in self.variables if v.startswith(text)]
        elif cmdtokens == ['set', 'module'] or cmdtokens ==['set', 'defaultmodule']:
            return [m for m in self.possible_modules if m.startswith(text)]
        elif cmdtokens == ['set', 'snmpversion']:
            return [g for g in self.possible_snmpversion if g.startswith(text)]
        elif cmdtokens == ['set', 'community']:
            return [f for f in self.possible_community if f.startswith(text)]
        elif cmdtokens == ['set', 'username'] or cmdtokens == ['set', 'fromuser']:
            return [t for t in self.possible_usernames if t.startswith(text)]
        elif cmdtokens == ['set', 'payload'] or cmdtokens == ['set', 'defaultpayload']:
            return [e for e in self.possible_payloads if e.startswith(text)]
        elif cmdtokens == ['set', 'iface']:
            return [r for r in self.possible_iface if r.startswith(text)]
        else:
            return []

    def do_showoptions(self, line):
        """Shows Options For Module"""
        if self.module == "exploit/multi/handler":
            print colours.RED +"="*width                            + colours.WHITE
            print colours.BLUE + ("payload = %s"% (self.payload)).center(width, ' ')             + colours.WHITE
            print colours.BLUE + ("lhost = %s"% (self.lhost)).center(width, ' ')                 + colours.WHITE
            print colours.BLUE + ("lport = %s"% (self.lport)).center(width, ' ')                 + colours.WHITE
            print colours.BLUE + ("module = %s"% (self.module)).center(width, ' ')              + colours.WHITE
            print colours.RED + "="*width                           + colours.WHITE
        elif self.module == "auxiliary/scanner/smb/smb_login":
            print colours.RED + "="*width                           + colours.WHITE
            print colours.BLUE + ("rhosts = %s"% (self.rhosts)).center(width, ' ')              + colours.WHITE
            print colours.BLUE + ("rport = %s"% (self.rport)).center(width, ' ')                 + colours.WHITE
            print colours.BLUE + ("module = %s"% (self.module)).center(width, ' ')               + colours.WHITE
            print colours.RED + "="*width                           + colours.WHITE
        elif self.module == "auxiliary/scanner/rservices/rlogin_login":
            print colours.RED + "="*width                           + colours.WHITE
            print colours.BLUE + ("rhosts = %s"% (self.rhosts)).center(width, ' ')               + colours.WHITE
            print colours.BLUE + ("rport = %s"% (self.rport)).center(width, ' ')                 + colours.WHITE
            print colours.BLUE + ("module = %s"% (self.module)).center(width, ' ')              + colours.WHITE
            print colours.BLUE + ("username = %s"% (self.username)).center(width, ' ')           + colours.WHITE
            print colours.BLUE + ("fromuser = %s"% (self.fromuser)).center(width, ' ')           + colours.WHITE
            print colours.RED + "="*width                           + colours.WHITE
        elif self.module == "auxiliary/scanner/snmp/snmp_enum":
            print colours.RED + "="*width                           + colours.WHITE
            print colours.BLUE + ("rhosts = %s"% (self.rhosts)).center(width, ' ')               + colours.WHITE
            print colours.BLUE + ("rport = %s"% (self.rport)).center(width, ' ')                 + colours.WHITE
            print colours.BLUE + ("module = %s"% (self.module)).center(width, ' ')               + colours.WHITE
            print colours.BLUE + ("community = %s"% (self.community)).center(width, ' ')         + colours.WHITE
            print colours.BLUE + ("snmpversion = %s"% (self.snmpversion)).center(width, ' ')     + colours.WHITE
            print colours.RED + "="*width                           + colours.WHITE
        else:
            print "The module (%s) isn't supported yet!" % self.module

    def do_run(self, line):
        """Runs The Module With Settings"""
        if self.module == "exploit/multi/handler":
            subprocess.call(["msfcli", self.module, "payload=%s" %self.payload, "lhost=%s" %self.lhost, "lport=%s" %self.lport, "E"])

        elif self.module == "auxiliary/scanner/smb/smb_login":
            subprocess.call(["msfcli", self.module, "rhosts=%s" %self.rhosts, "rport=%s" %self.rport, "E"])

        elif self.module == "auxiliary/scanner/rservices/rlogin_login":
            subprocess.call(["msfcli", self.module, "rhosts=%s" %self.rhosts, "rport=%s" %self.rport, "username=%s" %self.username, "fromuser=%s" %self.fromuser, "E"])

        elif self.module == "auxiliary/scanner/snmp/snmp_enum":
            subprocess.call(["msfcli", self.module, "rhosts=%s" %self.rhosts, "rport=%s" %self.rport, "community=%s" %self.community, "version=%s" %self.snmpversion, "E"])
        else:
            print "The module (%s) isn't supported yet!" % self.module

if __name__ == '__main__':
    print colours.RED + "="*width
    print colours.BLUE  + ("––•–√\/––√\/––•––" + colours.GREEN + "QuickMetasploit" + colours.BLUE + "––•–√\/––√\/––•––").center(width + 9, ' ')
    print "Type Help To List All Commands".center(width, ' ')
    print "Type Help (Command) For Specific Help".center(width, ' ')
    print "Local Ip Will Be Automaticaly Set".center(width, ' ')
    print "CTRL + C To Exit".center(width, ' ')
    print "Written By CharlieDean".center(width, ' ')
    print colours.RED   + "="*width
    print colours.GREEN + ("Default Module is %s" %DEFAULT_MODULE).center(width, ' ')
    print ("Default Payload is %s" %DEFAULT_PAYLOAD).center(width, ' ')
    print ("Default Lport is %s" %DEFAULT_LPORT).center(width, ' ')
    print colours.RED + "="*width + colours.WHITE
    

    while(True):
        try:
            prompt = Handler()
            prompt.prompt = '(>>)'
            prompt.cmdloop('')
        except (KeyboardInterrupt, SystemExit):
            while(True):
                try:
                    time.sleep(0.05)
                    exit = raw_input (colours.GREEN + "\n\nAre You Sure You Want To Quit? y/[n] (>>)" + colours.WHITE)
                    if exit and exit.lower()[0] == "y":
                        print colours.RED + "Exiting...*e48e13207341b6bffb7fb1622282247b*"            + colours.WHITE
                        with open('config.ini', 'w') as f:
                            config.write(f)
                        sys.exit()
                    else:
                        prompt.cmdloop('')

                except KeyboardInterrupt:
                    pass
