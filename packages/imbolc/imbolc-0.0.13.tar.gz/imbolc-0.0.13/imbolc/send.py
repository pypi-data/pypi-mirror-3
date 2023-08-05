#!/usr/bin/python
# -*- coding: utf-8 -*-
''' Отправка сообщений '''
from decorators import safely

send = sys.modules[__name__]  # for auto-import

def main():
    from privat import GMAIL_LOGGER, MAIN_EMAIL

    all(GMAIL_LOGGER, MAIN_EMAIL, u'письмо', u'тема')
    #~ gmail(GMAIL_LOGGER[0], GMAIL_LOGGER[1], MAIN_EMAIL, u'письмо', u'тема')
    #~ gtalk(GMAIL_LOGGER[0], GMAIL_LOGGER[1], MAIN_EMAIL, u'сообщение')
    


def all(login_and_password, target, body, subject=''):
    login, passwd = login_and_password
    gmail(login, passwd, target, body, subject)
    gtalk(login, passwd, target,
        '[%s]\n%s' % (subject, body) if subject else body)
    


def gtalk(login, passwd, target, msg, safe=True):
    '''
    Отправка одиночного сообщения в jabber
        *jid        - jid отправителя
        *passwd     - пароль отправителя
        *target     - jid получателя
        *msg        - cообщение
        **safe      - (bool) игнорировать исключения
    '''
    import xmpp
    try:
        jid = xmpp.protocol.JID(login)
        cl = xmpp.Client(jid.getDomain(), debug=[])
        if not cl.connect(('talk.google.com', 5223)):
            raise IOError('Can not connect to server.')
        if not cl.auth(jid.getNode(), passwd):
            raise IOError('Can not auth with server.')
        cl.send(xmpp.Message(target, msg, typ='chat'))
        cl.disconnect()
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception, ex:
        if not safe:
            raise

def gmail(login, passwd, target, body, subject, safe=True):
    '''
    Отправка одиночного email через gmail
    '''
    try:
        g = Gmail(login, passwd)
        g.send(target, subject, body)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception, ex:
        if not safe:
            raise

class Gmail(object):
    ''' Отправка мыл через gmail '''
    
    def __init__(self, sender, password):
        self.sender = str(sender)
        self.password = password
        self.server = None

    def auth(self):
        # аутентификация
        from smtplib import SMTP
        from socket import sslerror
        
        server = SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(0)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(self.sender, self.password)
        self.server= server
        
    def send(self, to, subj, body):
        # отправка сообщения
        from smtplib import SMTP
        #~ from socket import sslerror
        if not self.server:
            self.auth()
        to, subj, body = [s.encode('utf-8') if isinstance(s, unicode) else s for s in (to, subj, body)]
        full_text = 'From: %s\r\nTo: %s\r\nSubject:%s\r\nContent-Type: text/plain; charset="utf-8"\r\n\r\n%s' % (self.sender, to, subj, body)
        rc = self.server.sendmail(self.sender, to, full_text)


if __name__ == "__main__":
    main()


