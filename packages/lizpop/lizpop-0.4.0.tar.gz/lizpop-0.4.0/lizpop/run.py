#-*- coding: utf-8 -*-

#print "Load run as %s" % __name__ #debug

import sys, os, re

def usage(progname):
  sys.stdout.write(
    r'''Usage:
  %s [OPTION ...] [FILE] [-- ARG ...]
    [FILE]:
      Load scheme source code from FILE , and exit.
      If omitted, run interactively.

    [OPTION ...]:
      -q   Do not load your initialization file (~/.lizpop.scm) .
      -h   Display this help and exit.
      -v   Print version number and exit.
      -t   Output stack traces when error occurred.
      -eml Embedded scheme mode 

    [-- ARG ...]:
      The toplevel variable `*args*` is set to the (ARG ...)

''' % progname)

if __name__ == '__main__':

#scriptdir = os.path.dirname(os.path.abspath(sys.argv[0]))
#if scriptdir in sys.path:
#  sys.path.remove(scriptdir)

  import lizpop.config

  progname = "python [python's-args] -m lizpop.run"
  params = {"read-inifile":True, "embedded":False, "show-version":False,
            "prompt":"> ", "file":None, "lispargs":[]}

  arglist = sys.argv[1:]
  try:
    while True:
      arg = arglist.pop(0)
      if re.match("-", arg):
        if arg == "-N":
          if len(arglist) <= 0:
            usage(progname); exit(1)
          progname = arglist.pop(0)
        elif arg == "-h":
          usage(progname); exit(1)
        elif arg == "-v":
          params["show-version"] = True
        elif arg == "-q":
          params["read-inifile"] = False
        elif arg == "-t":
          lizpop.config.istraceback = True
        elif arg == "-d":
          lizpop.config.isdebug = True
        elif arg == "-eml":
          params["embedded"] = True
        elif arg == "-p":
          if len(arglist) > 0:
            params["prompt"] = arglist.pop(0)
            if params["prompt"] == "":
              params["prompt"] = False
        elif arg == "--":
          if len(arglist) > 0:
            params["lispargs"] = list(arglist)
          break
        else:
          usage(progname); exit(1)
      else:
        params["file"] = arg
  except IndexError: pass

  # if not lizpop.config.istraceback: sys.tracebacklimit=0

  from lizpop import scheme
  from lizpop.inport import InPort

  if params["show-version"]:
    print "version %s" % scheme.LIZPOP_VERSION
    exit(1)

  # Booting  -- call this the first time only
  scheme.Boot.boot()

  lisp = scheme.Interpreter()

  # bind *args*
  lisp.bind_toplevel("*args*",
                     scheme.ScmList.from_iter(
      x.decode("utf-8", "replace") for x in params["lispargs"]))

  # bind *program-name*
  progname = u"lizpop"
  if params["file"] is not None:
    progname = params["file"].decode("utf-8", "replace")
  lisp.bind_toplevel("*program-name*", progname)

  # load inifile
  inifile = "~/.lizpop.scm"
  if params["read-inifile"] and (
    os.path.isfile(os.path.expanduser(inifile))):
    lisp.srepl('(load "%s")' % inifile, errquit=False)

  # start REPL
  if params["file"] is None:
    if params["embedded"]:
      lisp.repl(prompt=params["prompt"],
                readport=InPort(sys.stdin, embedded=True), writemode="raw")
    else:
      lisp.repl(prompt=params["prompt"])
  else:
    inport = None
    try:
      if params["embedded"]:
        inport = InPort(open(params["file"], "r"), embedded=True)
        lisp.repl(readport=inport, writemode="raw", errquit=True)
        # lisp.repl(readport=inport, writemode="raw")
      else:
        inport = open(params["file"], "r")
        lisp.repl(readport=inport, errquit=True)
        # lisp.repl(readport=inport)
    finally:
      if inport: inport.close()

