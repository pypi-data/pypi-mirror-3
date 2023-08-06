#!/bin/env python
import multicast
from multicast.daemonize import daemonize
import socket
from optparse import OptionParser

def help(parser, e=None):
    if e:
        print e
        print
    parser.print_help()
    raise SystemExit

def parseTarget(t):

    if t.startswith ( "file://" ):
        return "FILE", t[7:], "storage"
    elif t == "stdin://":
        return "STDIN", None, "storage"
    elif t == "stdout://":
        return "STDOUT", None, "storage"


    s1 = t.split("@")

    ip = None
    port = None
    interface = None

    if len(s1) == 2:
        interface = s1[1]
        s1 = [ s1[0] ]

    if len(s1) == 1:
        s2 = s1[0].split (":")
        if len(s2) == 2:
            ip = s2[0]
            port = int(s2[1])
        elif len(s2) == 1:
            ip = ''
            port = int(s2[0])
        else:
            raise ValueError

    try: socket.inet_aton(ip)
    except: raise ValueError("Invalid IP: " + ip )

    return ip, port, interface

if __name__ == "__main__":
    parser = OptionParser(usage="%prog [options] [source_ip:]source_port[@source_interface] dest_ip:dest_port[@dest_interface]\nmulticast " + multicast.VERSION)
    parser.add_option ( "-t", "--ttl", action="store", type="int", dest="ttl", help="Time-To-Live for multicasts"  )
    parser.add_option ( "-q", action="store_true", dest="quiet", help="Dont say anything."  )
    parser.add_option ( "-d", "--daemon", action="store_true", dest="daemon", help="Run as daemon"  )
    parser.add_option ( "-v", action="store_true", dest="verbose", help="[OBSOLETED BY -q]"  )

    (options, args) = parser.parse_args()

    if len(args) < 2: 
        help(parser)
    
    try:
        s_ip, s_port, s_if = parseTarget(args[0])
        d_ip, d_port, d_if = parseTarget(args[1])        

        s_file = None
        d_file = None

        if d_if == "storage":
            if d_ip == "STDOUT":
                d_file = sys.stdout
            elif d_ip == "FILE":
                d_file = open( d_ip, 'w' )
            else:
                help(parser)

        if s_if == "storage":
            if s_ip == "STDIN":
                s_file = sys.stdin
            elif s_ip == "FILE":
                s_file = open( s_ip, 'r' )
            else:
                help(parser)
            

        s_ip_disp = s_ip
        d_ip_disp = d_ip

        s_if_disp = s_if
        d_if_disp = d_if

        if s_ip == '': s_ip_disp = "0.0.0.0"
        if d_ip == '': d_ip_disp = "0.0.0.0"

        if s_if is None: s_if_disp = "ANY"
        if d_if is None: d_if_disp = "ANY"        

    except ValueError, e:
        help(parser, e)

    if not options.quiet:
        print "Redirecting stream sent to {0}:{1} interface {2} TO {3}:{4} via interface {5}.".format ( s_ip_disp, s_port, s_if_disp, d_ip_disp, d_port, d_if_disp )
        
    try:        
        receiver = multicast.DatagramReceiver ( s_ip, s_port, s_if )
        sender = multicast.DatagramSender ( "0.0.0.0", d_port, d_ip, d_port )

        if not options.quiet:
            print "Source stream is",
            if receiver.multicast: print "multicast."
            else: print "unicast."

            print "Destination stream is",
            if sender.multicast: print "multicast."
            else: print "unicast."

            print "Streaming..."

        if options.daemon:
            if not options.quiet:
                print "Forking into background."
            daemonize()

        receiver.pipe (sender)
    except socket.error, e:
        if not options.daemon:
            print "Socket error: ", e
    except KeyboardInterrupt:
        pass
    finally:
        try: receiver.close()
        except: pass
    
        try: sender.close()
        except: pass
    

    if not options.quiet and not options.daemon:
        print "Done."




