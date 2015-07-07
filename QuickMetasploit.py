#!/usr/bin/python2.7
from collections import defaultdict
import cmd 
import subprocess
import sys
import time
import socket
import fcntl
import struct





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

################################################################Main class for commands
class Handler(cmd.Cmd):

    lport = ''
    payload = 'windows/meterpreter/reverse_tcp'
    lhost = ''
    iface = 'eth0'
    module = short_module_names['multi_handler']
    rhosts = ''
    rhost = ''
    rport = ''
    username = ''
    fromuser = 'root'
    community = 'public'
    snmpversion = '1'
    #multi_handler = 'exploit/multi/handler'
    #smb_login = 'auxiliary/scanner/smb/smb_login'
    #rlogin_login = 'auxiliary/scanner/rservices/rlogin_login'
    #snmp_enum = 'auxiliary/scanner/snmp/snmp_enum'
    possible_modules = short_module_names.keys()
    possible_snmpversion = ('1' ,'2c')
        
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.lhost = get_ip_address(self.iface)
        self.variables = module_variables[self.module]


        
    def do_set(self, line):
        """Use Tab To Show Variables You Can Set"""
        try:
            firstvalue, secondvalue = line.split()
            if firstvalue == 'module':
                module = short_module_names[secondvalue]
                self.variables = module_variables[module]
            setattr(self, firstvalue, secondvalue)
        
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
        elif cmdtokens == ['set', 'snmpversion']:
            return [g for g in self.possible_snmpversion if g.startswith(text)]
        else:
            return []

            
    def do_showpayloads(self, line):
        """Shows All The Avalible Payloads"""
        subprocess.call(["msfcli", "multi/handler", "P"])
        
    def do_exit(self, line):
        """Exits Program"""
        sys.exit()
    
    
    def do_showoptions(self, line):
        """Shows Options For Module"""
        self.lhost = get_ip_address(self.iface)
            
        if self.module == "multi_handler" or "exploit/multi/handler":
            print "========================================"
            print "--payload =", self.payload
            print "--lhost =", self.lhost
            print "--lport =", self.lport
            print "--module =", self.module
            print "========================================"
        elif self.module == "smb_login":
            print "========================================"
            print "--rhosts =", self.rhosts
            print "--rport =", self.rport
            print "--module =", self.module
            print "========================================"
        elif self.module == "rlogin_login":
            print "========================================"
            print "--rhosts =", self.rhosts
            print "--rport =", self.rport
            print "--module =", self.module
            print "--username =", self.username
            print "--fromuser =", self.fromuser
            print "========================================"
        elif self.module == "snmp_enum":
            print "========================================"
            print "--rhosts =", self.rhosts
            print "--rport =", self.rport
            print "--module =", self.module
            print "--community =", self.community
            print "--snmpversion =", self.snmpversion
            print "========================================"
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
                    exit = raw_input ("\n\nAre You Sure You Want To Quit? y/[n] (>>)")
                    if exit and exit.lower()[0] == "y":
                        print "Exiting..."
                        sys.exit()
                    else:
                        prompt.cmdloop('')
                
                except KeyboardInterrupt:
                    pass
#################################################################
