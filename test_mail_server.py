import os
import asyncore
import smtpd
import datetime
import base64
import quopri
import logging
from email.parser import Parser,BytesParser 
from email.mime.text import MIMEText
import pdb

# Dummy SMTP serer class.
class MyDebuggingServer(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        now = datetime.datetime.today()
        inheaders = 0
        b64encoded = 0
        qpencoded = 0
        
        # Separate mail header and body by empty line.
        lines = data.split('\n\n')
        headers = lines[0].split('\n')
        parser = Parser()
        #headers = parser.parsestr(lines[0])
        mail_body = lines[1]
        
        logger.info(str(now) + ' Receive message')
        logger.info('---------- MESSAGE FOLLOWS ----------')
        
        # Output mail header.
        for line in headers:
            # headers first
            if not inheaders and not line:
                logger.info('X-Peer:', peer[0])
                inheaders = 1
            
            if 'Content-Transfer-Encoding: base64' in line:
                b64encoded = 1

            if 'Content-Transfer-Encoding: quoted-printable' in line:
                qpencoded = 1
                
            logger.info(line)
        
        logger.info('')
        
        # Decode the base64 encoded string.
        if b64encoded:
            mail_body = lines[1].replace('\n', '')
            mail_body = base64.b64decode(mail_body)
        
        # Decode the quoted-printable encoded string.
        if qpencoded:
            mail_body = lines[1].replace('\n', '')
            mail_body = quopri.decodestring(mail_body)
        
        # Output mail body.
        mail_body = mail_body.decode('utf-8')
        logger.info(mail_body)
        logger.info('------------ END MESSAGE ------------')


# Start the server.
#pdb.set_trace()
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
logger = logging.getLogger('test_mail_server')
logger.setLevel(logging.DEBUG)
filename = script_dir + '/test_mail_server.log'
fh = logging.FileHandler(filename, encoding='utf-8')
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

hostname = ''
port = 8025
MyDebuggingServer((hostname, port), None, decode_data=True)

logger.info('Server Starting...')
logger.info('Listening at port :%d', port)

try:
    asyncore.loop()
except:
    logger.info('Server Stopped')
