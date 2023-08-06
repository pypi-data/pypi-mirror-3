from os.path import exists, realpath
from os import system

def bbedit(self):
    frame, lineno = self.stack[self.curindex]
    filename = self.canonic(frame.f_code.co_filename)
    if exists(filename):
        filename = realpath(filename)
        system('bbedit +%s -b "%s"' % (lineno, filename))

def preloop(self):
    bbedit(self)

def precmd(self, line):
    bbedit(self)
    return line
