import imaplib, re, time, base64, getpass

re_subject = re.compile(r'^Subject:.* ([0-9]+)\.([0-9A-Fa-f]+)\.([0-9A-Za-z_-]+)')

class imap_backend:
    def __init__(self, nimbstor, user, password, host, mailbox = 'INBOX', port = 143, ssl = False, cram = False, verbose = False):
        self._nimbstor = nimbstor
        self._mailbox = mailbox
        if password == '':
            password = getpass.unix_getpass(prompt = '      IMAP password: ')
        self._connect = (user, password, host, port, ssl, cram)
        self._login()
        self._imap = None
        self._messages = {}
        self._verbose = verbose
        _, msglist = self._imap.search(None, 'ALL')
        for msgnum in msglist[0].split():
            _, header = self._imap.fetch(msgnum, '(RFC822.HEADER)')
            for headline in header[0][1].split('\r\n'):
                ma_subject = re_subject.match(headline)
                if ma_subject:
                    number = int(ma_subject.group(1))
                    checksum1 = ma_subject.group(2)
                    checksum2 = ma_subject.group(3)
                    self._messages[(number, checksum1, checksum2)] = msgnum
                    self._nimbstor.append_block_info(number, checksum1, checksum2, self)
                    break
  
    def _login(self):
        user, password, host, port, ssl, cram = self._connect
        if ssl: self._imap = imaplib.IMAP4_SSL(host, port)
        else: self._imap = imaplib.IMAP4(host, port)
        if cram: self._imap.login_cram_md5(user, password)
        else: self._imap.login(user, password)
        self._imap.select(self._mailbox)
  
    def activate(self):
        self._nimbstor.open(self)
  
    def close(self, dont_commit = False):
        pass
  
    def write_buffer(self, buf, number, checksum1, checksum2):
        message = '\r\n'.join([
          "Subject: %07d.%s.%s" % (number, checksum1, checksum2),
          '',
          base64.encodestring(buf),
        ])
        self._imap.append(self._mailbox, '', time.time(), message)
        self._nimbstor.append_block_info(number, checksum1, checksum2, self)
  
    def read_buffer(self, number, checksum1, checksum2, decode_func):
        msgnum = self._messages[(number, checksum1, checksum2)]
        _, message = self._imap.fetch(msgnum, '(RFC822.TEXT)')
        return decode_func(base64.decodestring(message[0][1]))

__all__ = ('imap_backend',)
