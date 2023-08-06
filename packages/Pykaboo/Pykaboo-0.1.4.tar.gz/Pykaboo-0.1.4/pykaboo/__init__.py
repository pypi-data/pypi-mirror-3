#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
import sys
try:
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter
except ImportError:
    print "Pygments is not installed yet. Install pygments or run 'pip install -r requirements.txt'."
    sys.exit()

# NOTE: 
# PFF stands for scaffolding code for a Possible Future Feature.
#
# Comments not intended as code are indented by one space. Example: # This is a comment.
# Comments intended as code are not indented.              Example: #print "This is a code comment."

from subprocess import call
import textwrap
import sysconfig
import platform
import argparse
# PFF:
#import Image
import SimpleHTTPServer
import BaseHTTPServer
import webbrowser
import os
import distutils.sysconfig as dc
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

if platform.system() == "Windows":
    print "Windows users install Pykaboo on Cygwin with pip and run it from the Cygwin shell."
    sys.exit()
else:
    pass

class PykabooHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    # PFF:
    #def __init__(self, request, host, server):
    #    SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, request, host, server)
   
    def do_GET(self):
        # Needed to define global in order to encapsulate the body of _show_added_shortcut_links()
        # How to best avoid global when encapsulating a piece of code? 
        global path
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
            # Needed to define global in order to encapsulate the body of _show_added_shortcut_links()
            # How to best avoid global when encapsulating a piece of code? 
            global lis
            lis = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None

        lis.sort(key=lambda a: a.lower())
        # Needed to define global in order to encapsulate the body of _show_added_shortcut_links()
        # How to best avoid global when encapsulating a piece of code? 
        global f
        f = StringIO()
        css_file = open(path_to_pykaboo_css).read()
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<head>\n<title>Directory and python file listing for %s</title>\n" % path)
        f.write('<style type="text/css"> %s</style>\n' % css_file)
        f.write('</head>\n')
        f.write("<body>\n<div class=page-container>")
        f.write("\n<div class='title-container'>")
        f.write("\n<h2>Pykaboo</h2>\n")
        # PFF:
        #po = open(os.getenv("HOME")+'/Desktop/sc/other/Pykaboo/pykaboo/pyk1.png').read()
        #print po
        #f.write("\n<img width='65' src='pyk1.png' id='symbol'/>\n")
        f.write("\n</div>")
        f.write("<ul class=shortcut-list>\n")
        f.write("<li class=shortcut-list><a class='sh-c' href=%s>Python standard library modules</a></li>" % path_standard_library)
        f.write("\n<li class=shortcut-list><a class='sh-c' href=%s>User installed python packages</a></li>" % path_external_packages)
        try:
            with open(os.getenv("HOME")+'/.pykaboolinks', "r") as prc: 
                prc_string = prc.read()
            f.write(prc_string)
        except:
            pass

        f.write("\n</ul>")  
        f.write("\n<h5>Directory and python file listing for %s</h5>" % path)
        f.write("\n<hr>\n<ul>\n")
        # PFF:
        #if platform.system() != "windows":
        #    os.chdir(root)
        #else:
        #    pass
        os.chdir(root)
        _show_added_shortcut_links()
        f.write("</ul>\n<hr>\n</div>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        # PFF:
        #self.send_header('Content-type', 'text/css; charset=%s' % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f  

def _show_added_shortcut_links():
    for name in lis:
        fullname = os.path.join(path, name) 
        displayname = name
        condition1 = name.endswith(u'.py') or os.path.isdir(fullname) or os.path.islink(fullname) 
        condition2 = name.endswith(u'.egg-info') or name.endswith(u'.egg')
        if condition1 and not condition2:    
            if os.path.isdir(fullname):
                displayname = name + "/"
            else:
                pass

            if os.path.islink(fullname):
                displayname = name + "@"
            else:
                pass

            f.write('<li><a href="%s">%s</a>\n'% (fullname, displayname))
        else:
            pass

def _handle_add_argument():
    if os.path.isdir(subcmd):
        print "You added '%s' to the green directory links. Specify the name of this link." % subcmd
        d_name = raw_input("Just pressing <enter> uses '%s' as the link name.\n>> " % subcmd)
        if len(d_name) == 0:
            d_name = subcmd
        else:
            pass
        with open(os.getenv("HOME")+'/.pykaboolinks', "a") as prc:
            prc.write("<li class=shortcut-list><a class='sh-c' href=%s>%s</a></li>\n" % (subcmd, d_name))
        print "You added '%s' as a green directory link." % d_name
    else:
        print "'%s' is not an existing directory path." % subcmd

def _handle_remove_argument():
    if not _is_link_name(subcmd):
        print "The green directory link name '%s' does not exist yet." % subcmd
    else:
        _remove_line(subcmd)
        print "You removed the green directory link name '%s'." % subcmd

def _is_link_name(subcmd):
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

def _is_int(v):
    try:
        i = int(v)
        if i % 1 == 0:
            return True
        else:
            return False
    except:
        return False

def _handle_arguments():
    global cmd
    global subcmd
    try:
        cmd, subcmd = args.cmd
        if cmd == "add":
            _handle_add_argument()
            os._exit(1)
        elif cmd == "remove":
            _handle_remove_argument()
            os._exit(1)
        else:
            print "'%s' is not a valid first argument. Type 'pykaboo help' to get a list of valid arguments." % cmd
        
    except:
        cmd = args.cmd
        if cmd[0] == 'help':
            col1 = ["\tpykaboo", "\tpykaboo port_number",
                   "\tpykaboo add /path/to/directory", 
                   "\tpykaboo remove name_of_directory_link"]
            col2 = ["Runs pykaboo.",
                   "Hosts pykaboo from a specified port number.",
                   "Adds a green directory link, you are then prompted to name it.", 
                   "Removes an added green directory link."]
            print "\nUsage:"
            for c1, c2 in zip(col1, col2):
                mc2 = "".join(textwrap.fill(c2, width=30, initial_indent="", subsequent_indent="\t\t\t\t\t\t", break_long_words = False))
                print "%-40s %s" % (c1, mc2)
            print "\nIf you want to remove all added links at once just delete the '.pykaboolinks'"
            print "file in your home folder." 
            print ""
            sys.exit()
        elif cmd[0] == 'add':
            print "Add which path? type 'pykaboo add /absolute/path/to/dir' to add a path."
            sys.exit()                 
        elif cmd[0] == 'remove':
            with open(os.getenv("HOME")+'/.pykaboolinks', "r") as prc:
                lines = prc.readlines()
                lines_string = "".join(lines) 
            if len(lines_string.strip()) == 0:
                print "You have not added any links yet."
            else:
                print "remove which directory link name?"
                print "Created link names:"
                # Gets a specific part of a partially variable string
                for i in lines:
                    j = i.split('>')
                    k = j[2].split('<')
                    print k[0]
            sys.exit()

        elif _is_int(cmd[0]):
            if int(cmd[0]) in range(65535):
                global port
                port = int(cmd[0])
            else:
                print "Port number needs to be between 0 and 65534. Between 49152 and 65534 is advised."
                sys.exit()

        else:
            print "'%s' is not a valid first argument. Type 'pykaboo help' to get a list of valid arguments." % cmd[0] 
            sys.exit()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", help="Execute a command", action="store", nargs='*')

    global args
    args = parser.parse_args()
    if args.cmd:
        _handle_arguments()
    else:
        pass

    if "cygwin" in platform.system().lower():
        try: 
            call(["cygstart", "http://localhost:%d" % port])
        except:
            # Calling it once somehow causes an exception.
            call(["cygstart", "http://localhost:%d" % port])

    else:
        webbrowser.open("http://localhost:%d" % port)

    # Let pykaboo initially show the folder containing the standard library modules.
    os.chdir(path_standard_library)
    server = BaseHTTPServer.HTTPServer(('', port), PykabooHTTPRequestHandler)
    try:
        print "\nType 'pykaboo help' for the list of commands."
        print "\nPress <CTRL> + C to stop running pykaboo.\n"
        print "Serving on 'http://localhost:%d'." % port
        server.serve_forever()
    except:
        print "\nBye bye!\n"

# PFF:
#if platform.system() == "Windows":
#    root = os.path.splitdrive(sys.executable)[0]+"/"
#else:
#    root = "/"

root = "/"
port = 8090
path_to_pykaboo = os.path.abspath(__file__)
if path_to_pykaboo.endswith(".pyc"):
    path_to_pykaboo_css = path_to_pykaboo.replace("/__init__.pyc", "/pykaboo_style.css")
else:
    path_to_pykaboo_css = path_to_pykaboo.replace("/__init__.py", "/pykaboo_style.css")

if ".virtualenvs" in sysconfig.get_path('platlib'):
    path_external_packages = dc.get_python_lib()
else:
    path_external_packages = sysconfig.get_path('platlib')
path_standard_library = dc.get_python_lib(standard_lib=True)

if __name__ == '__main__':
    main()
