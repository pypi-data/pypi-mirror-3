#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
import sys
try:
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter
except ImportError:
    print "\npygments is not installed yet. Install pygments or run 'pip install -r requirements.txt'.\n"
    sys.exit()

import argparse
#import Image
import SimpleHTTPServer
import BaseHTTPServer
import webbrowser
import SocketServer
import os
import distutils.sysconfig as dc

import urllib
import cgi
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class PykabooHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def __init__(self, request, host, server):
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, request, host, server)
   
    def do_GET(self):
        path = os.path.join(os.getcwdu(), self.path[1:])
        # This if body is only active when clicked on a .py link.
        if os.path.exists(path) and path.endswith('.py'):
            with open(path) as file:
                cod = file.read()
                hl = highlight(cod, PythonLexer(), HtmlFormatter(noclasses=True, linenos='inline', style='friendly'))
                hl = '<body style="background:#f0f0f0">'+hl+'</body>'
                self.send_response(200)
                self.end_headers()
                self.wfile.write(hl)
        # This else body is active when browsing through directories and python files.
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
 
    def list_directory(self, path):
        try:
            lis = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        lis.sort(key=lambda a: a.lower())
        f = StringIO()
        css_file = open(path_to_pykaboo_css).read()
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<head>\n<title>Directory and python file listing for %s</title>\n" % path)
        f.write('<style type="text/css"> %s</style>\n' %css_file)
        f.write('</head>\n')
        f.write("<body>\n<div class=page-container>")
        f.write("\n<div class='title-container'>")
        f.write("\n<h2>Pykaboo</h2>\n")
        # Dnw:
        #po = open(os.getenv("HOME")+'/Desktop/sc/other/Pykaboo/pykaboo/pyk1.png').read()
        #print po
        #f.write("\n<img width='65' src='pyk1.png' id='symbol'/>\n")
        #f.write("<img src='http://celebrity.womendiary.net/wp-content/uploads/MaryBonoMack-Scandalous-Pic.jpg'/>")
        f.write("\n</div>")
        f.write("<ul class=shortcut-list>\n")
        f.write("<li class=shortcut-list><a class='sh-c' href=%s>Python standard library modules</a></li>" % path_standard_library)
        f.write("\n<li class=shortcut-list><a class='sh-c' href=%s>User installed python modules</a></li>" % path_external_packages)
        try:
            with open(os.getenv("HOME")+'/.pykaboolinks', "r") as prc: 
                prc_string = prc.read()
            f.write(prc_string)
        except:
            pass

        f.write("\n</ul>")  
        f.write("\n<h5>Directory and python file listing for %s</h5>" % path)
        f.write("\n<hr>\n<ul>\n")
        os.chdir("/")
        for name in lis:
            fullname = os.path.join(path, name) 
            displayname = name
            condition1 = name.endswith(u'.py') or os.path.isdir(fullname) or os.path.islink(fullname) 
            condition2 = name.endswith(u'.egg-info') or name.endswith(u'.egg')
            if condition1 and not condition2:    
                if os.path.isdir(fullname):
                    displayname = name + "/"
                if os.path.islink(fullname):
                    displayname = name + "@"
                f.write('<li><a href="%s">%s</a>\n'% (fullname, displayname))
        f.write("</ul>\n<hr>\n</div>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        # Dnw:
        #self.send_header('Content-type', 'text/css; charset=%s' % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f  

def _add_argument_handler():
    if os.path.isdir(subcmd):
        print "\nYou added '%s' to the top directory links." % subcmd
        d_name = raw_input("\nSpecify the name of this link. Just pressing <enter> uses '%s' as the link name.\n> " % subcmd)
        print ""
        if len(d_name) == 0:
            d_name = subcmd
        else:
            pass
        with open(os.getenv("HOME")+'/.pykaboolinks', "a") as prc:
            prc.write("<li class=shortcut-list><a class='sh-c' href=%s>%s</a></li>\n" % (subcmd, d_name))
    else:
        print "\n'%s' is not an existing directory path.\n" % subcmd

def _remove_argument_handler():
    if not _link_name_checker(subcmd):
        print "\nthe top directory link name '%s' does not exist yet.\n" % subcmd
    else:
        _remove_line(subcmd)
        print "\nYou removed the top directory link name '%s'.\n" % subcmd

def _link_name_checker(subcmd):
    with open(os.getenv("HOME")+'/.pykaboolinks', "r") as prc:
        lines = prc.readlines()
        for line in lines:
            suff = "%s</a></li>\n" % subcmd
            if line.endswith(suff):
                return True
            else:
                pass
        return False

def _remove_line(del_d_name):
    with open(os.getenv("HOME")+'/.pykaboolinks', "r") as prc:
        lines = prc.readlines()

    with open(os.getenv("HOME")+'/.pykaboolinks', "w") as prc:
        for line in lines:
            suff = "%s</a></li>\n" % del_d_name
            if not line.endswith(suff):
                prc.write(line)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", help="Execute a command", action="store", nargs='*')
    args = parser.parse_args()

    if args.cmd:
        global cmd
        global subcmd
        try:
            cmd, subcmd = args.cmd
            if cmd == "add":
                _add_argument_handler()
            elif cmd == "remove":
                _remove_argument_handler()
            else:
                print "'%s' is not a valid first argument. Type 'pykaboo help' to get a list of valid arguments." % cmd
            
        except:
            cmd = args.cmd
            if cmd[0] == 'help':
                rn_st = ("\nUsage: pykaboo"
                         "                                    "
                         "Runs pykaboo.")
                print rn_st
                add_st = ("       pykaboo add /path/to/directory"
                         "             Adds a directory, you are then" 
                         "                        "
                         "                          prompted to name it.")
                print add_st
                remove_st = ("       pykaboo remove name_of_directory_link"
                             "      Removes an added directory"
                             "                                         "
                             "             link.\n")
                print remove_st

            elif cmd[0] == 'add':
                print "Add which path? type 'pykaboo add /absolute/path/to/dir' to add a path."

            elif cmd[0] == 'remove':
                print "remove which directory link name?"
                print "Created link names:"
                with open(os.getenv("HOME")+'/.pykaboorc', "r") as prc:
                    lines = prc.readlines()
                # Gets a specific part of a partially variable string
                for i in lines:
                    j = i.split('>')
                    k = j[2].split('<')
                    print k[0]
                print ""
                
            else:
                print "'%s' is not a valid first argument. Type 'pykaboo help' to get a list of valid arguments." % cmd[0] 
        sys.exit()
    else:
        pass

    webbrowser.open("http://localhost:8090")

    os.chdir("/usr/lib/python2.7")

    print "\nType 'pykaboo help' for the list of commands."
    print "\nPress <CTRL> + C to stop running pykaboo.\n"

    server = BaseHTTPServer.HTTPServer(('', 8090), PykabooHTTPRequestHandler)
    try:
        server.serve_forever()
    except:
        print "\nBye bye!\n"

path_to_pykaboo = os.path.abspath(__file__)
if path_to_pykaboo.endswith(".pyc"):
    path_to_pykaboo_css = path_to_pykaboo.replace("/__init__.pyc", "/pykaboo_style.css")
else:
    path_to_pykaboo_css = path_to_pykaboo.replace("/__init__.py", "/pykaboo_style.css")
path_external_packages = dc.get_python_lib()
path_standard_library = dc.get_python_lib(standard_lib=True)

if __name__ == '__main__':
    main()
