#!/usr/bin/python
###############################################################################

import signal
import smtpd
import smtplib
import email.utils
import subprocess
from smtplib import SMTPServerDisconnected
from email.mime.text import MIMEText
from pprint import pprint, pformat
from os import kill
from signal import alarm, signal, SIGALRM, SIGKILL
from subprocess import PIPE, Popen
import traceback
import json
import sys

class SMTPDropBoxTimeoutAlarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise SMTPDropBoxTimeoutAlarm

class SMTPDropBoxTest(object):
    """
    testing this:
    
    must create two processes - one that is the dropbox that sits and listens,
    second that creates an email message, sends it, then determines if the
    dropbox did as it was supposed to do.
    should I use nose tests?
    idea:  do the invoke-subprocess thing with a trap for exceptions;
    send a message,
    read the subprocess's output (files?  json object?)
    determine if output is correct.
    -- repeat process with various messages --
    """
    
    def __init__(self):
        self.dbProc = None
        self.outputFilename = 'smtpDropboxOutput.txt' 
        self.jsonFilename   = 'smtpDropboxOutput.json'
        
    def get_process_children(self, pid):
        #p = Popen('ps | tail -n +2 | --no-headers -o pid --ppid %d' % pid, shell = True, stdout = PIPE, stderr = PIPE)
        if (not pid):
            print "get_process_children() called with 0 or None for pid."
            return
        p1 = Popen("""ps""", shell = True, stdout = PIPE, stderr = subprocess.STDOUT)
        cmd = """ps %d | tail -n +2 | sed 's/^I//g' | sed 's/\s\+/ /g' | cut -d' ' -f 2,3""" % (pid)
        #print "doing cmd=>>%s<<" % (cmd)
        p2 = Popen(cmd, shell = True, stdout = PIPE, stderr = subprocess.STDOUT)
        stdout, stderr = p1.communicate()
        #print "p1 stdout = " + stdout
        stdout, stderr = p2.communicate()
        #print "p2 stdout = " + stdout
        subprocs = []
        for line in stdout.split('\n'):
            n = line.split(' ')
            if (len(n) >= 2):
                subprocs.append((int(n[0]), int(n[1])))
        needPids = [pid]
        for (f1, f2) in subprocs:
            if (f2 == pid):
                needPids.append(f1)
        print "subprocs: " + pformat(needPids)
        return needPids
       
    def killDropBoxProc(self):
        print "Killing drop box process."
        if not self.dbProc:
            return
        procpid = self.dbProc.pid or None
        print "process pid now: " + str(procpid)
        if not procpid:
            return
        pids = self.get_process_children(procpid)
        for pid in pids:
            # process might have died before getting to this line
            # so wrap to avoid OSError: no such process
            try: 
                print "Killing process/subprocess pid=%d." % (pid)
                kill(pid, SIGKILL)
            except OSError:
                pass
        print "Done killing drop box process."
        return
        
    def startSmtpDropBox(self):
        print "starting smtp dropbox..."
        self.outfileName = '/tmp/smtpdropboxTest.out'
        cmd = './smtpdropbox.py' # > %s 2>&1' % (self.outfileName)
        print "Executing command:  '%s'" % (cmd)
        # './smtpdropbox.py 2>&1 > ./dboxtest.out 2>&1',
        self.dbProc = subprocess.Popen(cmd, shell =False, stdin=None, stdout=None, stderr=subprocess.STDOUT )
        print "dbproc pid:  " + str(self.dbProc.pid)

        #signal(SIGALRM, alarm_handler)
        #alarm(10)  # 10 seconds
        return
        
    def stopSmtpDropBox(self):
        print "Stopping smtp dropbox..."
        self.killDropBoxProc()
        #self.outfh.close()
        return
        
    def sendEmail(self, fromaddr, toaddr, subj="", body="", attachList=[]):
        # Create the message
        
        to_addresses = ','.join(toaddr)
        
        msg = MIMEText(body)
        msg['To'        ] = to_addresses 
        msg['From'      ] = fromaddr
        msg['Subject'   ] = subj
        
        server = smtplib.SMTP('localhost', 55026)
        server.set_debuglevel(True) # show communication with the server
        
        try:
            try:
                server.sendmail(fromaddr, to_addresses, msg.as_string())
            finally:
                try:
                    server.quit()
                except:
                    print "Server has already disconnected, don't need to quit."
        except:
            pass    

        print "Sending an email from='%s' to='%s' subj='%s', body='%s', with %d attachments." % (
            pformat(fromaddr), pformat(to_addresses ), subj, body, len(attachList))
        return
        
    def runTest(self):
        self.startSmtpDropBox()
        self.fromAddrs  = 'from_a@b.com'
        self.toAddrs    = ['to_E@b.com']
        self.subject    = "test message one"
        self.body       = "this is the extreme body of a normal test message."
        try:
            self.sendEmail(self.fromAddrs, self.toAddrs, subj=self.subject, body=self.body)
        except SMTPDropBoxTimeoutAlarm:
            print "Oops, taking too long!"
        except Exception, err:          
            print traceback.format_exc()
            print sys.exc_info()[0]     
        fdata = []
        self.stopSmtpDropBox()
        print "data: " + pformat(fdata)
        self.compareInputOutput()        
        print "end of data."
        print "end of test."

    def assertequal(self, fname, val1, val2):
        if (val1 == val2):
            pass
        else:
            print "UNEQUAL, field=%20.20s:  json='%s', sent='%s'." % (fname, str(val1), str(val2))
            self.totalErrs += 1
        return    
    
    def compareInputOutput(self):
        #ofh = open(self.outputFilename, "r")
        jfh = open(self.jsonFilename,   "r")
        jsonStr = jfh.read()
        jfh.close()
        print "got json string back: %s" % (jsonStr)
        self.totalErrs = 0
        jsonObj = json.loads(jsonStr)
        self.assertequal('body',        jsonObj['body'      ], self.body        )
        self.assertequal('subject',     jsonObj['subject'   ], self.subject     )
        self.assertequal('mailfrom',    jsonObj['mailfrom'  ], self.fromAddrs   )
        self.assertequal('rcpttos',     jsonObj['rcpttos'   ], self.toAddrs     )
        print "\n" + "=" * 80 + '\n'
        if (self.totalErrs == 0):
            print "SUCCESS"
        else:
            print "ERRORS:  " + str(self.totalErrs)
        print "\n" + "=" * 80 + '\n'
        

dbt = SMTPDropBoxTest()
dbt.runTest()

###############################################################################
###############################################################################
#######################    E N D   O F   F I L E    ###########################
###############################################################################
###############################################################################

