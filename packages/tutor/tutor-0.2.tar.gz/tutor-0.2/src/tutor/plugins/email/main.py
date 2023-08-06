#-*- coding: utf8 -*-
from StringIO import StringIO
from tutor.util import fs_util
import pyson
import pyson.json_encoding
from email.mime.text import MIMEText
import smtplib
import collections
import contextlib
import shelve
import fs.osfs
import random
from propertylib import oncedescriptor

@pyson.json_encoding.register_cls('tutor.MailMessage')
class Message(object):
    '''A simple e-mail message object
    
    Parameters
    ----------
    mailfrom : str
        Sender's e-mail address. It can also be given as a tuple of 
        (email, name) with the sender's name. 
    mailto : str
        Recipient's e-mail address or a list of e-mail addresses. Can also be
        given as a tuple or a list of tuples of (email, name).
    subject : str
        String containing the message subject.
    data : str
        A string of text containing the text part of the message.
    xhtmldata : str
        The message in XHTML form. If both `data` and `xhtmldata` are given,
        a XHTML message is constructed with a text-only fallback.
        
    Examples
    --------
    
    This creates and sends a simple text message using a Gmail account:
    
    >>> msg = Message('foo@gmail.com', 'foobar@bar.com',
    ...                subject='Test message', data='My message for you!')
    
    The `.send()` method sends the message through SMTP using `foo@gmail.com`
    as the username. 
    
    >>> msg.send(passwd='*passwd*', gmail=True) # doctest: +SKIP
    
    Under the hood, the MIME content of the message is built automatically
    from the message's content                   
    
    >>> print(msg.encode())
    Content-Type: text/plain; charset="us-ascii"
    MIME-Version: 1.0
    Content-Transfer-Encoding: 7bit
    From: foo@gmail.com
    To: foobar@bar.com
    Subject: Test message
    <BLANKLINE>
    My message for you!
    '''
    def __init__(self, mailfrom, mailto, subject=None, data=None, xhtmldata=None):
        self.mailfrom = mailfrom
        self.mailto = [mailto]
        self.subject = subject
        self.data = data
        if not (xhtmldata == None):
            raise NotImplementedError

    def attach(self, fname, data, mime):
        '''Attach a file to the message'''
        #TODO: attachments 
        raise NotImplementedError

    def encode(self):
        '''MIME Encodes message to send it using sendmail'''

        try:
            data = self.data.encode('ascii')
            msg = MIMEText(data)
        except UnicodeEncodeError:
            data = self.data.encode('utf8')
            msg = MIMEText(data, _charset='utf8')

        msg['From'] = self.mailfrom
        msg['To'] = ', '.join(self.mailto)
        if self.subject:
            msg['Subject'] = self.subject
        return msg.as_string()

    def send(self, host='ĺocalhost', port=25, ssl=False, username=None, passwd=None, gmail=False):
        '''Sends message via SMTP. 
        
        Parameters
        ----------
        
        host : str
            Name or IP address for the SMTP server
        port : int
            Port the SMTP server listens.
        ssl : bool
            If True, uses SSL encryption.
        username, passwd : str
            Username and password to use in TSL authentication. If no username
            is given, it is assumed to be the `mailfrom` attribute of the 
            message.
        gmail : bool
            If True, it sends message using Gmail's SMTP server. Username and
            password must correspond to those of a valid Gmail account.
        '''

        if gmail:
            host = 'smtp.gmail.com'
            port = 587
            if not passwd:
                raise ValueError('password must be specified')
        if ssl:
            smtp = smtplib.SMTP_SSL(host, port)
        else:
            smtp = smtplib.SMTP(host, port)
        if username or passwd:
            username = username or self.mailfrom
            smtp.starttls()
            smtp.login(username, passwd)
        smtp.sendmail(self.mailfrom, self.mailto, self.encode())
        return smtp.quit()

    def _asbytesdata(self, data):
        return data

    def __eq__(self, other):
        for attr in ['mailfrom', 'mailto', 'subject', 'data']:
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    def __json_encode__(self):
        return self.__dict__

    @classmethod
    def __json_decode__(cls, json):
        new = object.__new__(cls)
        new.__dict__.update(json)
        return new

@pyson.json_encoding.register_cls('tutor.Mailbox')
class Mailbox(collections.MutableSequence):
    '''Represents a group of e-mail messages.
    
    Messages are grouped in a list-like structure and are stored in a database
    in the filesystem. Users can add arbitrary tags to messages'''

    def __init__(self, dbdir):
        if isinstance(dbdir, basestring):
            self.dbdir = fs.osfs.OSFS(dbdir, create=True)
        else:
            self.dbdir = dbdir
        self.dbname = self.dbdir.getsyspath('maildb')
        self._attachfiles = self.dbdir.makeopendir('attachments')
        if self.dbdir.exists('maildb'):
            with self.dbdir.open('maildb.bak', 'w') as F:
                with self.dbdir.open('maildb') as Fsource:
                    F.write(Fsource.read())

        try:
            self._db = shelve.open(self.dbname, 'r', protocol=2)
        except:
            db = shelve.open(self.dbname, 'c', protocol=2)
            db.close()
            self._db = shelve.open(self.dbname, 'r', protocol=2)

    @contextlib.contextmanager
    def _db_write(self, msg_id=True):
        self._db.close()
        del self._db
        db = shelve.open(self.dbname, 'w', protocol=2)
        try:
            yield db
        finally:
            if msg_id:
                db['#msg_id'] = self._msg_id
            db.close()
            self._db = shelve.open(self.dbname, 'r', protocol=2)

    def db_update(self, tags=False, msg_id=False, meta=False):
        if tags or msg_id:
            with self._db_write(False) as db:
                if tags:
                    db['#tags'] = self._tags
                if msg_id:
                    db['#msg_id'] = self._msg_id
                if meta:
                    db['#meta'] = self._meta
    #===========================================================================
    # Abstract metods
    #===========================================================================
    def __delitem__(self, idx):
        self.delmessages([idx])

    def __getitem__(self, idx):
        return self._db[self._msg_id[idx]]

    def __iter__(self):
        db, ids = self._db, self._msg_id
        for m_id in ids:
            yield db[m_id]

    def __len__(self):
        return len(self._msg_id)

    def __setitem__(self, idx, value):
        del self[idx]
        self.insert(idx, value)

    def insert(self, idx, value):
        if not isinstance(value, Message):
            raise TypeError('value must be a Message object, got: %s' % type(value))
        msg_id = 'msg-' + self.newid()

        with self._db_write() as db:
            if msg_id in self._msg_id:
                raise RuntimeError
            self._msg_id.insert(idx, msg_id)
            db[msg_id] = value

        #self.addmessages([value], idx)

    def newid(self, size=10):
        '''New randomized string id'''

        DATA = 'abcdefghijhlmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return ''.join(random.choice(DATA) for _ in range(size))

    def addmessages(self, messages, idx=None):
        raise NotImplementedError

    def delmessages(self, idxlist=None):
        '''Clear all messages in list of indexes.'''

        if idxlist is None:
            idxlist = range(len(self))

        msgs = { idx: self._msg_id[idx] for idx in idxlist }
        with self._db_write() as db:
            try:
                for idx, mid in msgs.items():
                    del db[str(mid)]
                    msgs[idx] = None
            finally:
                self._msg_id = [ mid for (i, mid) in enumerate(self._msg_id) if msgs.get(i, 0) is not None ]

    def _get_idx(self, idx):
        if isinstance(idx, int):
            return idx
        elif isinstance(idx, basestring):
            return self._msg_id.index(idx)
        elif isinstance(idx, Message):
            return self.index(idx)
        else:
            raise TypeError(type(idx))

    def _get_mid(self, idx):
        return self._msg_id[self._get_idx(idx)]

    def _get_msg(self, idx):
        return self._db[self._get_mid(idx)]

    def message(self, mailto, subject=None, data=None, xhtmldata=None):
        msg = Message(None, mailto, subject=subject, data=data, xhtmldata=xhtmldata)
        self.append(msg)
        return msg

    #===========================================================================
    # Properties
    #===========================================================================
    @oncedescriptor
    def _msg_id(self):
        return self._db.get('#msg_id', [])

    @oncedescriptor
    def _tags(self):
        return self._db.get('#tags', {})

    @oncedescriptor
    def _meta(self):
        return self._db.get('#meta', {})

    #===========================================================================
    # Tagging
    #===========================================================================
    def _assure_tag(self, tag):
        if tag not in self._tags:
            raise ValueError('unsupported tag: %s' % tag)

    def addtag(self, tag):
        '''Adds a tag to a list of allowed tags'''

        self._tags.setdefault(tag, set())
        self.db_update(tags=True)

    def tag(self, idx, tag):
        '''Tag message at index with the given tag name'''

        self._assure_tag(tag)
        m_id = self._get_mid(idx)
        self._tags[tag].add(m_id)
        self.db_update(tags=True)

    def untag(self, idx, tag):
        '''Untag messsage'''

        self._assure_tag(tag)
        m_id = self._get_mid(idx)
        self._tags[tag].discard(m_id)
        self.db_update(tags=True)

    def tagged(self, tag):
        '''Return all messages tagged with the given tag.'''

        self._assure_tag(tag)
        changed_db = False
        tagged = []
        for obj in list(self._tags[tag]):
            try:
                msg = self._db[obj]
            except KeyError:
                self._tags[tag].discard(obj)
                changed_db = True
            else:
                tagged.append(msg)
        if changed_db:
            self.db_update(tags=True)
        return tagged

    def itertags(self, idx):
        m_id = self._get_mid(idx)
        for tag, objs in self._tags.items():
            if m_id in objs:
                yield tag

    def gettags(self, idx):
        '''Return a list of all tags in ix'''

        return list(self.itertags(idx))

    def hastag(self, idx, tag):
        '''dfsd'''
        self._assure_tag(tag)
        return any(tag_i == tag for tag_i in self.itertags(idx))

    #===========================================================================
    # Meta information
    #===========================================================================
#    def _assure_meta(self, meta):
#        if meta not in self._meta:
#            raise ValueError('unsupported meta information tag: %s' % meta)
#
#    def addmeta(self, tag):
#        '''Adds a tag to a list of allowed meta information fields'''
#
#        self._meta.setdefault(tag, set())
#        self.db_update(meta=True)
#
#    def setmeta(self, idx, tag, value):
#        '''Tag message at index with the given tag name'''
#
#        self._assure_meta(tag)
#        idx = self._get_idx(idx)
#        m_idx = self._msg_id[idx]
#        self._meta[tag][m_idx] = value
#        self.db_update(meta=True)
#
#    def getmeta(self, idx):
#        pass
#
#    def delmeta(self, idx, tag):
#        '''Untag messsage'''
#
#        self._assure_meta(tag)
#        idx = self._get_idx(idx)
#        m_id = self._msg_id[idx]
#        tags = self._meta[tag]
#        del tags[m_id]
#        self.db_update(meta=True)
#
#    def hasmeta(self, tag):
#        '''Return all messages tagged with the given tag.'''
#
#        self._assure_tag(tag)
#        changed_db = False
#        tagged = []
#        for obj in self._tags[tag]:
#            try:
#                msg = self._db[obj]
#            except KeyError:
#                self._tags[tag].discard(obj)
#                changed_db = True
#            tagged.append(msg)
#        if changed_db:
#            self.db_update(tags=True)
    def __json_encode__(self):
        fields = ['dbdir', 'dbname']
        fields = {f: getattr(self, f) for f in fields}
        new = {'fields': fields,
               'db': dict(self._db)}
        return new

    @classmethod
    def __json_decode__(cls, json):
        dbdir = json['fields']['dbdir']
        new = object.__new__(cls)
        new.__dict__.update(json['fields'])
        #dbcontent = dbdir.getcontents(new.dbname)
        try:
            new._db = shelve.open(new.dbname, 'n')
            with new._db_write(False) as db:
                dbjson = {k.encode('utf8'): v for (k, v) in json['db'].items()}
                dbjson['#msg_id'] = map(str, dbjson.get('#msg_id', []))
                for tagset in dbjson.get('#tags', {}).values():
                    tags = map(str, tagset)
                    tagset.clear()
                    tagset.update(tags)
                db.update(dbjson)
            new._db
        except Exception:
#            with dbdir.open(new.dbname, 'w') as F:
#                F.write(dbcontent)
            raise
        return new

@pyson.json_encoding.register_cls('tutor.Outbox')
class Outbox(Mailbox):
    def __init__(self, dbdir, mailfrom=None, host=None, port=None, login=None, passwd=None, ssl=False):
        super(Outbox, self).__init__(dbdir)
        conf = self._db.get('#smtpconf', {})

        # Automatic configuration of GMail accounts
        if mailfrom and mailfrom.endswith('@gmail.com'):
            host = host or 'smtp.gmail.com'
            port = port or 587

        self.mailfrom = mailfrom or conf.get('mailfrom', None)
        self.host = host or conf.get('host', None)
        self.port = port or conf.get('port', None)
        self.ssl = ssl or conf.get('ssl', None)
        self.login = login or conf.get('login', None)
        self.passwd = passwd or conf.get('passwd', None)
        with self._db_write(False) as db:
            db['#smtpconf'] = {k: getattr(self, k) for k in
                               ['mailfrom', 'host', 'port', 'ssl', 'login', 'passwd']}
        self.addtag('pending')

    def insert(self, idx, value):
        if value.mailfrom is None:
            value.mailfrom = self.mailfrom
        super(Outbox, self).insert(idx, value)
        self.tag(idx, 'pending')

    def sendmessage(self, msg):
        if self.ssl:
            smtp = smtplib.SMTP_SSL(self.host, self.port)
        else:
            smtp = smtplib.SMTP(self.host, self.port)
        if self.login or self.passwd:
            username = self.login or self.mailfrom
            smtp.starttls()
            smtp.login(username, self.passwd)
        smtp.sendmail(msg.mailfrom or self.mailfrom, msg.mailto, msg.encode())

        print 'Message sent to %s.' % msg.mailto
        self.untag(msg, 'pending')
        return smtp.quit()

    def sendmail(self):
        for msg in self.pending():
            self.sendmessage(msg)

    def pending(self):
        return self.tagged('pending')

#    def sent(self):
#        sent = set(self)
#        for msg in self.pending():
#            pass

    @contextlib.contextmanager
    def usingpassword(self, passwd):
        oldpass = self.passwd
        try:
            self.passwd = passwd
            yield
        finally:
            self.passwd = oldpass

    def __json_encode__(self):
        fields = ['mailfrom', 'host', 'port', 'ssl', 'login', 'passwd', 'dbdir']
        fields = {f: getattr(self, f) for f in fields}
        new = super(Outbox, self).__json_encode__()
        new['fields'].update(fields)
        return new

class Inbox(Mailbox):
    def checkmail(self):
        pass

    def __json_encode__(self):
        fields = ['mailfrom', 'host', 'port', 'ssl', 'login', 'passwd', 'dbdir']
        return {f: getattr(self, f) for f in fields}

    @classmethod
    def __json_decode__(cls, obj):
        raise NotImplementedError

if __name__ == '__main__':
    mail = Outbox('out')
    mail.delmessages()
    m = Message('foo@bar.com', 'bar@foo.com', data='sfsdf')
    mail.append(m)
    mail.append(Message('foo@bar.com', 'bar@foo.com', data='sdfs fsdf sd'))
    mail.append(Message('foo@bar.com', 'ham@spam.com', data='sdfsdsf sd s sd sd'))

    print mail.pending()
    mail.sendmail()
    print mail.pending()

    json = pyson.json_encode(mail)
    mail = pyson.json_decode(json)
    mail.sendmail()
    print mail.pending()

if __name__ == '__main__':
    import doctest
    doctest.testmod()
