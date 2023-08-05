#!/usr/bin/python
###############################################################################



import asyncore
import email.utils
import os
import json
import smtpd
import smtplib
import uu
from StringIO import StringIO
from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Parser import Parser as EmailParser
from email.Utils import COMMASPACE, formatdate
from email.Header import decode_header
from email.mime.text import MIMEText
from email.utils import parseaddr
from pprint import pprint, pformat

class Devnull:
    def write(self, msg): pass
    def flush(self): pass


DEBUGSTREAM = Devnull()
NEWLINE = '\n'
EMPTYSTRING = ''
COMMASPACE = ', '


###############################################################################

class NotSupportedMailFormat(Exception):
    pass

###############################################################################

class SMTPDropBox(smtpd.SMTPServer):
    
    # receive the message and do appropriate processing.
    
    def __init__(self, inTuple, outTuple, outputFilename, jsonFilename, numMessages=0):
        print "have outputfilename=%s, jsonFilename=%s." % (outputFilename, jsonFilename)
        self.numMessages        = max(numMessages, 0)  # no negative numbers of msgs.
        self.receivedMessages   = 0
        self.outfilename        = outputFilename or ""
        self.jsonFilename       = jsonFilename   or ""
        smtpd.SMTPServer.__init__(self, inTuple, outTuple)

    def dumpMessageToScreen(self, peer, mailfrom, rcpttos, data):
        print 'Receiving message from :', peer
        print 'Message addressed from :', mailfrom
        print 'Message addressed to   :', rcpttos
        print 'Message length         :', len(data)
        print 'have mail data         :', pformat(data)
        inheaders = 1
        lines = data.split('\n')
        print '---------- MESSAGE FOLLOWS ----------'
        for line in lines:
            # headers first
            if inheaders and not line:
                print 'X-Peer:', peer[0]
                inheaders = 0 
            print line
        print '------------ END MESSAGE ------------'
        return

    def storeJson(self, msg):
        if not self.jsonFilename:
            print "No JSON filename 'jsonFilename' provided, not dumping json of msg to that filename."
            return
        #print "starting with dict: " + pformat(msg)
        res = json.dumps(msg)
        if res:
            jsonfh = open(self.jsonFilename, "w+")
            jsonfh.write(res)
            jsonfh.close()
        else:
            print "no json object created, nothing to store."
        return

    def process_message(self, peer, mailfrom, rcpttos, data):
        
        print "=" * 80
        print "Starting to process message..."

        self.dumpMessageToScreen(peer, mailfrom, rcpttos, data)
        msg = email.message_from_string(data)
        result = self.parseMsg(msg)
        result['mailfrom'] = mailfrom
        result['rcpttos' ] = rcpttos
        result['msgdata' ] = data
        self.storeJson(result)
        
        afile_list  = result.get('attachments', None)
        #afile       = afile_list[0]
        #afile_contents = afile.getvalue()
        #print "afile contents : " + afile_contents

        subj     = msg.get('Subject', 'default subject')
        print "subject      : " + subj
        msgBody  = self.get_text(msg)
        print "Msg body     : " + msgBody
        print "Message dict : " + pformat(msg.__dict__)
        print "message dump : " + pformat(msg)
        
        toaddr = ",".join(rcpttos)
        #self.sendMessageAgain(fromaddr=mailfrom, toaddr=toaddr, subj=subj, msgBody=msgBody, attr=afile_contents)
        #self.send_mail(send_from=mailfrom, send_to=rcpttos, subject=subj, text=msgBody, attachments=afile_list)
        #self._deliver(mailfrom, rcpttos, data)
        

        self.receivedMessages += 1
        if (self.numMessages != 0) and (self.receivedMessages >= self.numMessages):
            print "num messages: %d" % self.receivedMessages
            exit(0)

    def get_text(self, msg):
        text = ""
        if msg.is_multipart():
            html = None
            for part in msg.get_payload():
                if part.get_content_charset() is None:
                    charset = chardet.detect(str(part))['encoding']
                else:
                    charset = part.get_content_charset()
                if part.get_content_type() == 'text/plain':
                    text = unicode(part.get_payload(decode=True),str(charset),"ignore").encode('utf8','replace')
                if part.get_content_type() == 'text/html':
                    html = unicode(part.get_payload(decode=True),str(charset),"ignore").encode('utf8','replace')
            if html is None:
                return text.strip()
            else:
                return html.strip()
        else:
            text = unicode(msg.get_payload(decode=True),msg.get_content_charset(),'ignore').encode('utf8','replace')
            return text.strip()

    def parse_attachment(self, message_part):
        content_disposition = message_part.get("Content-Disposition", None)
        if content_disposition:
            dispositions = content_disposition.strip().split(";")
            if bool(content_disposition and dispositions[0].lower() == "attachment"):
    
                file_data = message_part.get_payload(decode=True)
                # Used a StringIO object since PIL didn't seem to recognize
                # images using a custom file-like object
                attachment = StringIO(file_data)
                attachment.content_type = message_part.get_content_type()
                attachment.size = len(file_data)
                attachment.name = None
                attachment.create_date = None
                attachment.mod_date = None
                attachment.read_date = None
                
                for param in dispositions[1:]:
                    name,value = param.split("=")
                    name = name.lower()
    
                    if name == "filename":
                        attachment.name = value
                    elif name == "create-date":
                        attachment.create_date = value  #TODO: datetime
                    elif name == "modification-date":
                        attachment.mod_date = value #TODO: datetime
                    elif name == "read-date":
                        attachment.read_date = value #TODO: datetime
                return attachment
    
        return None
    
    def parse(self, content):
        """
        Parse the email and return a dictionary of relevant data.
        """
        p = EmailParser()
        msgobj = p.parse(content)
        retval = self.parseMsg(msgobj)
        return retval
        
    def parseMsg(self, msgobj):    
        if msgobj['Subject'] is not None:
            decodefrag = decode_header(msgobj['Subject'])
            subj_fragments = []
            for s , enc in decodefrag:
                if enc:
                    s = unicode(s , enc).encode('utf8','replace')
                subj_fragments.append(s)
            subject = ''.join(subj_fragments)
        else:
            subject = None
    
        attachments = []
        body = None 
        html = None 
        for part in msgobj.walk():
            attachment = self.parse_attachment(part)
            if attachment:
                attachments.append(attachment)
            elif part.get_content_type() == "text/plain":
                if body is None:
                    body = ""
                body += unicode(
                    part.get_payload(decode=True),
                    part.get_content_charset(),
                    'replace'
                ).encode('utf8','replace')
            elif part.get_content_type() == "text/html":
                if html is None:
                    html = ""
                html += unicode(
                    part.get_payload(decode=True),
                    part.get_content_charset(),
                    'replace'
                ).encode('utf8','replace')
        outDict = {
            'subject'       : subject,
            'body'          : body,
            'html'          : html,
            'from'          : parseaddr(msgobj.get('From'))[1], # Leave off the name and only return the address
            'to'            : parseaddr(msgobj.get('To'))[1],   # Leave off the name and only return the address
            'attachments'   : attachments,
            }

        if (0):
            print "parsed"
            print "msg subject: " + (outDict['subject'] or "")
            print "msg body   : " + (outDict['body'   ] or "")
            print "msg html   : " + (outDict['html'   ] or "")
            print "msg to     : " + (outDict['to'     ] or "")
            print "msg att    : " + pformat(outDict['attachments'])
    
        return outDict

###############################################################################

def main():
    server = SMTPDropBox(('localhost', 55026), None, 'smtpDropboxOutput.txt', 'smtpDropboxOutput.json', 1)
    asyncore.loop()

if __name__ == "__main__":
    main()


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
