#-*- coding: utf-8; mode: python; -*-
#
# This is a sample implementation for running Lizpop on apache2 + mod_wsgi3.3. 
#
# Installation Example:
# (1)Edit httpd.conf
#     Must configure apache2+mod_wsgi to run in `Daemon Mode`.
#     For example:
#       LoadModule wsgi_module modules/mod_wsgi.so
#       WSGIScriptAlias /wsgi_sample /home/someplace/wsgi_sample/application.wsgi
#       WSGIDaemonProcess wsgi_sample processes=1 threads=15
#       # WSGISocketPrefix /var/run/wsgi
#       <Directory /home/someplace/wsgi_sample>
#         WSGIProcessGroup wsgi_sample
#         Options ExecCGI FollowSymlinks
#         AddHandler wsgi-script .py
#       # Order deny,allow
#       # Deny from all
#       # allow from 127.0.0.1 192.168.10.
#         Order allow,deny
#         Allow from all
#       </Directory>
# (2)Reboot apache, e.g. $ sudo /etc/init.d/apache restart
# (3)Browse to http://your-server-name/wsgi_sample/
#    e.g.
#     http://192.168.10.1/wsgi_sample/
#     http://192.168.10.1/wsgi_sample/hello
#     http://192.168.10.1/wsgi_sample/helloworld.eml
#     http://192.168.10.1/wsgi_sample/dumpinfo.eml
#       (Please check `wsgi.multiprocess: #t` and `wsgi.multithread: #t` )
#     http://192.168.10.1/wsgi_sample/calendar.eml
#
# FILES:
#   booteml.scm ---- scheme script on boot-up
#   *.eml  --- samples
#
#
mydebug = True
if mydebug: print "Loading application.wsgi"
import sys, re, os, threading, cgi
import StringIO
import datetime
import wsgiref, wsgiref.util

### getting this place
#   __file__ or  environ["SCRIPT_FILENAME"]
#   e.g.   os.path.dirname( os.path.abspath(__file__) ) 
#          os.path.dirname(environ["SCRIPT_FILENAME"])
thisplace = os.path.dirname( os.path.abspath(__file__) ) 

### Add this-place to sys.path
# another way:
#  WSGIDaemonProcess wsgi_sample .... python-path=/thisplace:/someplace
pathlist =  [thisplace]
for path in reversed(pathlist):
  if not path in sys.path:
    if mydebug: print "Add %s to sys.path" % path
    sys.path.insert(0, path)
if mydebug: print sys.path

#### Load lizpop ###################
# Enable traceback scheme's error 
import lizpop.config
lizpop.config.istraceback = True 
lizpop.config.isdebug = True 
# load scheme
import lizpop.scheme
from lizpop import scheme
from lizpop.inport import InPort
# Add booteml.scm to boot-sources , and boot up lizpop
startup = os.path.join(thisplace, "booteml.scm")
scheme.Boot.boot(extsources=[startup])
if mydebug: print "Lizpop did boot-up"

# Context for application-level
# (The instance is created at the last of this file)
class AppContext:
  def __init__(self):
    # Thease attributes must be readonly
    self._basedir = os.path.dirname( os.path.abspath(__file__) ) 
    # table (PATH_INFO <=> function)
    self.dispatch_table = {"/":"/index.eml", "/hello":hello,
                           "/dump":dump,
                           # "/redirect301":redirect301,
                           "/redirect":redirect302,
                           }
  def basedir(self): return self._basedir

# Context Class for request-level
class RequestContext:
  def __init__(self, environ):
    self._environ = environ

    self._basedir = None
    if "SCRIPT_FILENAME" in environ:
      self._basedir = os.path.dirname(environ["SCRIPT_FILENAME"])

    # path_info, e.g. http://somewhere.com/wsgi/eml/hello.eml => /eml/hello.eml
    self._path = self._environ["PATH_INFO"]

    # cgi.FieldStorage object
    self._query = cgi.FieldStorage(fp=self._environ['wsgi.input'],
                                  environ=self._environ)
    # user data
    self._data = {}
    # forward function
    self.forward = None
    # quit function
    self.quit = None

    self._lisp = None

  def environ(self): return self._environ
  def basedir(self): return self._basedir
  def path(self): return self._path
  def query(self): return self._query

  # getter for request data
  def getdata(self, name=None, fallback=None):
    if name is None: return self._data
    return self._data.get(unicode(name), fallback)

  # setter for request data
  def setdata(self, *args):
    for i in xrange(0, len(args), 2):
      self._data[ unicode(args[i]) ] = args[i+1]

# Context Class for response
class ResponseContext:
  def __init__(self, start_response, status="200 OK", headers=[]):
    self.start_response = start_response
    self._status = status
    self._headerlist = headers
    self._body = "" # must be byte-string

  def start(self):
    "Do start_response, and return response body"
    self.setheader("Content-Length", str(len(self._body)))
    if mydebug: print "ResponseContext> start_response response=", self
    self.start_response(self._status, self._headerlist)
    return self._body

  def status(self): return self._status
  def setstatus(self, status): self._status = str(status)
  def headerlist(self): return self._headerlist
  def clear_headerlist(self): self._headerlist = []
  def delheader(self, name, value=None):
    name = str(name).lower()
    if value: value = str(value)
    for id in reversed( xrange( len(self._headerlist) ) ):
      (n,v) = (self._headerlist[id][0].lower(), self._headerlist[id][1])
      if n == name and (value is None or v == value):
        del self._headerlist[id]
    return self._headerlist
  def addheader(self, name, value):
    (name, value) = (str(name), str(value))
    self._headerlist.append((name, value))
    return self._headerlist
  def setheader(self, name, value):
    (name, value) = (str(name), str(value))
    self.delheader(name)
    self.addheader(name, str(value)) # not unicode
  def body(self): return self._body
  def setbody(self,body):
    self._body = body
  def __str__(self):
    return "\n".join([self._status] + ["  " + str(tp) for tp in self._headerlist] )

class QuitRequestException(BaseException):
  def __init__(self):
    self.retry_handler = None

def application(environ, start_response):
  request = RequestContext(environ)
  response = ResponseContext(start_response,
                           "200 OK",
                           [('Content-Type', 'text/html; charset=UTF-8')])

  quitexc = QuitRequestException()

  def forward(path_or_handler):
    quitexc.retry_handler = path_or_handler
    response.setbody("")
    raise quitexc

  def quit_request():
    raise quitexc

  # register forward, quit_request to RequestContext
  request.forward = forward
  request.quit = quit_request
  
  handler = request.path()
  try:
    while True:
      try:
        # dispatch request
        if isinstance(handler, basestring):
          if handler in appctx.dispatch_table:
            handler = (appctx.dispatch_table)[handler]
        if isinstance(handler, basestring):
          (base, ext) = os.path.splitext(handler)
          if ext == ".eml":
            handler_path = handler
            handler = lambda rq,rs : eml_dispatch(rq, rs, handler_path)
        if callable(handler): handler(request, response)
        else: errorpage(request, response)

      except QuitRequestException, ex:
        if ex is not quitexc: raise ex
        if ex.retry_handler is not None:
          handler = ex.retry_handler
          continue
      # end of try (dispatch)
      break
    # end of while
    if mydebug: print "path=", request.path() # debug
    return response.start()
  finally:
    if mydebug: print "End of request" # debug
    request._lisp = None
    (request, response) = (None, None)
  
def eml_dispatch(request, response, path):
  r'''Dispatch *.eml request, and run EML script.
  The following procedures and variables can be used in a EML script.
    (request . MESSAGE ARGS)  ---- Accessor for RequestContext
    (response . MESSAGE ARGS) ---- Accessor for ResponseContext
    &ENVNAME   ---- WSGI environment (ENVNAME is key name of environments)
                    e.g. &REMOTE_ADDR, &QUERY_STRING 
  '''
  # Get source filepath (appctx.basedir() + "/" + request.path)
  appdir = appctx.basedir()
  # srcname = request.path()
  srcname = path
  srcpath = os.path.normpath(appdir + srcname)
  if mydebug: print "eml source path=", srcpath #debug
  # Go to the error page if no source-file
  if not os.path.isfile(srcpath):
    if mydebug: print "EML file(%s) was not found." % srcpath
    return errorpage(request, response)
    
  # define (request) function
  def call_request(message=None, *args):
    '''Procedure: (request . MESSAGE ARGS)
       e.g. (request)  --- get RequestContext object
            (request 'environ) --- get wsgi environ object
            (request 'setdata "mode" "exec") -- set request-data '''
    if message is None: return request
    return (getattr(request, str(message)))(*args)

  # define (response) function
  def call_response(message=None, *args):
    '''Procedure: (response . MESSAGE ARGS)
       e.g. (response)  --- get ResponseContext object
            (response 'setstatus "404 Not Found") --- set status
            (response 'setheader "Content-Type" "text/plain; charset=UTF-8")'''
    if message is None: return response
    return (getattr(response, str(message)))(*args)

  inport = None;
  outport = StringIO.StringIO()
  errport = StringIO.StringIO()
  try:
    if request._lisp:
      lisp = request._lisp
      lisp.outport = outport
      lisp.errport = errport
      if mydebug: print "Re-use scheme.Interpreter" # debug
    else:
      # create lisp interpreter
      lisp = scheme.Interpreter(outport=outport, errport=errport)
      request._lisp = lisp
      if mydebug: print "Create scheme.Interpreter" # debug

    # bind call_request procedure to `request`
    bind = lisp.bind_toplevel
    bind(u"request", call_request)
    bind(u"response", call_response)
    # bind environ items to `&keyname` variable
    #  e.g. &REMOTE_ADDR, &QUERY_STRING ...
    for k,v in request.environ().iteritems():
      bind("&%s" % k, v)

    # Set *load-path* to this place  
    # (Not implemented yet - adding ~/.lizpop.scm and LIZPOP_LOAD_PATH )
    bind("*load-path*", scheme.ScmList.from_iter([appdir]))
    # Set input-port to EML source file
    inport = InPort(open(srcpath, "r"), embedded=True)
    # Run REPL 
    try:
      result = lisp.repl(readport=inport,
                         writemode="raw", # Write a result using `(display ..)'
                         errquit=True     # Quit immediately if an error occurred
                         )
    except Exception:
      msg = ("<b>Error message</b>\n" + cgi.escape(lisp.errport.getvalue()) + "\n" +
             "<b>Contents</b>\n" + cgi.escape(lisp.outport.getvalue()) + "\n")
      msg = re.sub(r" ", "&nbsp;", msg)
      msg = re.sub(r"\n", "<br />", msg)
      response.clear_headerlist()
      request.setdata("status", "500 Internal Server Error")
      request.setdata("message", msg)
      return errorpage(request, response)
    response.setbody(lisp.outport.getvalue())
    return 
  finally:
    lisp = None
    outport.close()
    errport.close()
    if inport: 
      if mydebug: print "close %s" % srcpath
      inport.close()

def hello(request, response):
  response.setstatus("200 OK")  # no need
  response.setheader('Content-Type', 'text/plain; charset=UTF-8')
  response.setbody("Hello")

def errorpage(request, response):
  response.setstatus( request.getdata("status", "404 Not Found") )
  msg = request.getdata("message")
  if msg is None:
    msg = "The requested URL %s was not found." % request.environ()["REQUEST_URI"]
  response.setheader('Content-type', 'text/html; charset=iso-8859-1')
  response.setbody(r'''
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head><title>%s</title></head>
<body>
<h1>%s</h1>
<p>%s</p>
<hr>
</body></html>
''' % (response.status(), response.status(), msg) )

def redirect301(request, response, url=None):
  url = request.getdata("redirect-url", url)
  if url is None: return errorpage(request, response)
  response.setstatus("301 Moved Permanently")
  response.clear_headerlist()
  response.setheader("Location", url)
  response.setbody("")

def redirect302(request, response, url=None):
  url = request.getdata("redirect-url", url)
  if url is None: return errorpage(request, response)
  response.setstatus("302 Found")
  response.clear_headerlist()
  response.setheader("Location", url)
  response.setbody("")

# For debug 
def dump(request, response):
  response.setstatus('200 OK')
  outlist = []
  outlist.append(datetime.datetime.now().strftime("%H:%M:%S"))
  outlist.append("__name__=%s" % __name__)
  outlist.append("__file__=%s" % __file__)

  import thread
  outlist.append("thread.stack_size=%s" % thread.stack_size())
  th = threading.currentThread()
  outlist.append("Current thread type is %s" % type(th))
  outlist.append("Current thread name is %s" % th.getName())

  outlist.append("Process id = %s" % os.getpid())

  environ = request.environ()
  outlist.append("environ type=%s" % type(environ))
  outlist.append("start_response type=%s" % type(response.start_response))

  outlist.append("request_uri(with query)=" +
                 wsgiref.util.request_uri(environ, include_query=1))
  outlist.append("request_uri(without query)=" +
                 wsgiref.util.request_uri(environ, include_query=False))
  outlist.append("application_uri=" + 
                 wsgiref.util.application_uri(environ))

  query = request.query()
  outlist.append("queries")
  for key in query.keys():
    outlist.append("  %s:%s" % (key, query.getlist(key)))

  outlist.append("environ")
  for k,v in environ.iteritems():
    outlist.append("  %s:%s" % (k,v))

  output = "\n".join(outlist)
  response.setbody(output)
  response.setheader('Content-Type', 'text/plain')

# Create an AppContext instance
appctx = AppContext()

