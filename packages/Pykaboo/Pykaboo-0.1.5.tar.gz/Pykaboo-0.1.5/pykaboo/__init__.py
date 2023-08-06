#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
import sys
try:
    from pygments import highlight
    import pygments.lexers as pl
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
try:
    import sysconfig
except ImportError:
    pass

if platform.system() == "Windows":
    print "Windows users install Pykaboo on Cygwin with pip and run it from the Cygwin shell."
    sys.exit()
else:
    pass

class PykabooHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    # PFF:
    #def __init__(self, request, host, server):
    #    SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, request, host, server)

    @staticmethod
    def _format_to_extension(stri):
        splitted_stri = stri.split("*")
        if len(splitted_stri) == 2 and len(splitted_stri[1]) != 0:
            return splitted_stri[1]
        else:
            return ".a_very_unlikely_extension_name"

    @staticmethod
    def _get_lexer(ext):
            for key in pl.LEXERS:
                if ext in pl.LEXERS[key][3]:
                    return key
                else:
                    pass
            raise ValueError      

    def do_GET(self):
        path = os.path.join(os.getcwdu(), self.path[1:])          
        if os.path.isdir(path):
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        elif os.path.exists(path):
            for kw, val in pl.LEXERS.iteritems():
                for el in val[3]:
                    formatted_extension = self._format_to_extension(el)
                    if path.endswith(formatted_extension):
                        with open(path) as file:
                            cod = file.read()
                            hl = highlight(cod, getattr(pl, self._get_lexer(el))(), HtmlFormatter(noclasses=True, linenos='inline', style='friendly'))
                            hl = '<body style="background:#f0f0f0">'+hl+'</body>'
                            self.send_response(200)
                            self.end_headers()
                            self.wfile.write(hl) 
                    else:
                        pass

            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
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
        # pass if file does not exist yet.
        try:
            with open(os.getenv("HOME")+'/.pykaboolinks', "r") as prc: 
                prc_string = prc.read()
            f.write(prc_string)
        except IOError:
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
        _show_added_shortcut_links(f, path, lis)
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

def _file_endswith(name): 
    # pass if file does not exist yet.
    try:
        with open(os.getenv("HOME")+'/.pykabooext', "r") as prc:
            lines = prc.readlines()
            for line in lines:
                # Stripping the \n.
                val = name.endswith(line.strip())
                if val == True:
                    return True
                else:
                    pass
            return False
    except IOError:
        pass      

def _show_added_shortcut_links(html_f, path, li):
    for name in li:
        fullname = os.path.join(path, name) 
        displayname = name
        eggs = name.endswith('.egg-info') or name.endswith('.egg')
        condition_dir = os.path.isdir(fullname) and not eggs
        condition_symlink = os.path.islink(fullname) and not eggs
        condition = name.endswith('.py') or condition_dir or condition_symlink or _file_endswith(name)
        if condition:    
            if os.path.isdir(fullname):
                displayname = name + "/"
            else:
                pass

            if os.path.islink(fullname):
                displayname = name + "@"
            else:
                pass

            html_f.write('<li><a href="%s">%s</a>\n'% (fullname, displayname))
        else:
            pass

def _handle_add_argument(scmd):
    if os.path.isdir(scmd):
        print "You added '%s' to the green directory links. Specify the name of this link." % scmd
        d_name = raw_input("Just pressing <enter> uses '%s' as the link name.\n>> " % scmd)
        if len(d_name) == 0:
            d_name = scmd
        else:
            pass
        with open(os.getenv("HOME")+'/.pykaboolinks', "a") as prc:
            prc.write("<li class=shortcut-list><a class='sh-c' href=%s>%s</a></li>\n" % (scmd, d_name))
        print "You added '%s' as a green directory link." % d_name
    else:
        print "'%s' is not an existing directory path." % scmd

def _handle_remove_argument(scmd):
    if not _is_link_name(scmd):
        print "The green directory link name '%s' does not exist yet." % scmd
    else:
        _remove_line(scmd)
        print "You removed the green directory link name '%s'." % scmd

def _is_link_name(scmd):
    with open(os.getenv("HOME")+'/.pykaboolinks', "r") as prc:
        lines = prc.readlines()
        for line in lines:
            suff = "%s</a></li>\n" % scmd
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
            else:
                pass

def _is_int(v):
    try:
        i = int(v)
        if i % 1 == 0:
            return True
        else:
            return False
    except (ValueError, TypeError):
        return False

def _handle_allow_argument(scmd):
    if scmd == "*":
        # PFF:
        # Allow all file types.
        pass
    else:
        with open(os.getenv("HOME")+'/.pykabooext', "a") as prc:
            prc.write("%s\n" % scmd)
    print "You allowed files with the '%s' extension to be viewed in Pykaboo." % scmd

def _handle_disallow_argument(scmd):
    if not _is_allowed(scmd):
        print "The extension '%s' is not even allowed yet." % scmd
    else:
        _disallow_line(scmd)
        print "You disallowed the '%s' extension." % scmd

def _is_allowed(scmd):
    with open(os.getenv("HOME")+'/.pykabooext', "r") as prc:
        lines = prc.readlines()
        for line in lines:
            if scmd in line:
                return True
            else:
                pass
        return False

def _disallow_line(scmd):
    with open(os.getenv("HOME")+'/.pykabooext', "r") as prc:
        lines = prc.readlines()

    with open(os.getenv("HOME")+'/.pykabooext', "w") as prc:
        for line in lines:
            fscmd = scmd + "\n"
            if not fscmd in line:
                prc.write(line)
            else:
                pass 

def _handle_arguments(ar):
    if len(ar) == 1:
        if ar[0] == 'help':
            col1 = ["\tpykaboo", "\tpykaboo port_number",
                   "\tpykaboo add /path/to/directory", 
                   "\tpykaboo remove name_of_directory_link",
                   "\tpykaboo allow extension_name",
                   "\tpykaboo disallow extension_name"]
            col2 = ["Runs pykaboo.",
                   "Hosts pykaboo from a specified port number.",
                   "Adds a green directory link, you are then prompted to name it.", 
                   "Removes an added green directory link.",
                   "Allows files with a specified extension to be viewed in pykaboo.",
                   "Disallows allowed files of a specified extension."]
            print "\nUsage:"
            for c1, c2 in zip(col1, col2):
                mc2 = "".join(textwrap.fill(c2, width=30, initial_indent="", subsequent_indent="\t\t\t\t\t\t", break_long_words = False))
                print "%-40s %s" % (c1, mc2)
            print "\nIf you want to remove all added links at once just delete the"
            print "'.pykaboolinks' file in your home folder." 
            print "If you want to disallow all allowed extensions at once just delete the"
            print "'.pykabooext' file in your home folder."
            print ""
            sys.exit()
        elif ar[0] == 'add':
            print "Add which path? type 'pykaboo add /absolute/path/to/dir' to add a path."
            sys.exit()                 
        elif ar[0] == 'remove':
            with open(os.getenv("HOME")+'/.pykaboolinks', "r") as prc:
                lines = prc.readlines()
                lines_string = "".join(lines) 
            if len(lines_string.strip()) == 0:
                print "You have not added any links yet."
            else:
                print "Remove which directory link name?"
                print "Created link names:"
                # Gets a specific part of a partially variable string
                for i in lines:
                    j = i.split('>')
                    k = j[2].split('<')
                    print k[0]

            sys.exit()          
        elif ar[0] == 'disallow':
            with open(os.getenv("HOME")+'/.pykabooext', "r") as prc:
                lines = prc.readlines()
                lines_string = "".join(lines) 
            if len(lines_string.strip()) == 0:
                print "You have not allowed any extensions yet."
            else:
                print "Disallow files with which extension?"
                print "Already allowed extensions of files:"
                print lines_string

            sys.exit()
        elif ar[0] == 'allow':
            print "allow showing files with which extension?"
            print "e.g.: 'pykaboo allow .html'."     
            # PFF:
            #print "To allow all filetypes type 'pykaboo allow *'."
            sys.exit()
        elif _is_int(ar[0]):
            if int(ar[0]) in range(65535):
                # Avoid this global?
                global port
                port = int(ar[0])
            else:
                print "Port number needs to be between 0 and 65534. Between 49152 and 65534 is advised."
                sys.exit()

        else:
            print "'%s' is not a valid first argument. Type 'pykaboo help' to get a list of valid arguments." % ar[0] 
            sys.exit()

    elif len(ar) == 2:
        if ar[0] == "add":
            _handle_add_argument(ar[1])
            sys.exit()
        elif ar[0] == "remove":
            _handle_remove_argument(ar[1])
            sys.exit()
        elif ar[0] == "allow":
            _handle_allow_argument(ar[1])
            sys.exit()
        elif ar[0] == "disallow": 
            _handle_disallow_argument(ar[1])
            sys.exit()
        else:
            print "'%s' is not a valid first argument. Type 'pykaboo help' to get a list of valid arguments." % ar[0]
            sys.exit()

    else:
        print "You can not give more than two arguments."
        sys.exit()    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", help="Execute a command", action="store", nargs='*')
    args = parser.parse_args()
    args_list = args.cmd
    if len(args_list) > 0:
        _handle_arguments(args_list)
    else:
        pass

    if "cygwin" in platform.system().lower():
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
    except KeyboardInterrupt:
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

try:
    if ".virtualenvs" in sysconfig.get_path('platlib'):
        path_external_packages = dc.get_python_lib()
    else:
        path_external_packages = sysconfig.get_path('platlib')
except:
    path_external_packages = dc.get_python_lib()

path_standard_library = dc.get_python_lib(standard_lib=True)

if __name__ == '__main__':
    main()
