# A modified version of django.core.mail which allows extra headers.

# Use this module for e-mailing.

from django.conf import settings
from email.MIMEText import MIMEText
from email.Header import Header
import smtplib, rfc822
import os, random, datetime, sys

from django.core.mail import BadHeaderError, SafeMIMEText

def send_mail(subject, message, from_email, recipient_list, fail_silently=False, auth_user=settings.EMAIL_HOST_USER, auth_password=settings.EMAIL_HOST_PASSWORD, extra_headers=None):
    """
    Easy wrapper for sending a single message to a recipient list. All members
    of the recipient list will see the other recipients in the 'To' field.
    """
    return send_mass_mail([[subject, message, from_email, recipient_list]], fail_silently, auth_user, auth_password, extra_headers)

def send_mass_mail(datatuple, fail_silently=False, auth_user=settings.EMAIL_HOST_USER, auth_password=settings.EMAIL_HOST_PASSWORD, extra_headers=None):
    """
    Given a datatuple of (subject, message, from_email, recipient_list), sends
    each message to each recipient list. Returns the number of e-mails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    """
    try:
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        if auth_user and auth_password:
            server.login(auth_user, auth_password)
    except:
        if fail_silently:
            return
        raise
    num_sent = 0
    for subject, message, from_email, recipient_list in datatuple:
        if not recipient_list:
            continue
        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        msg = SafeMIMEText(message, 'plain', settings.DEFAULT_CHARSET)
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = ', '.join(recipient_list)
        msg['Date'] = rfc822.formatdate()
	msg['Message-ID'] = '<%s_%d_%d@rocksoc.org.uk>' % \
			(datetime.datetime.now().isoformat('T').replace(':', '.'),
                         os.getpid(), random.randrange(0, sys.maxint))
	if extra_headers:
            for h in extra_headers:
                msg[h] = extra_headers[h]
        try:
            server.sendmail(from_email, recipient_list, msg.as_string())
            num_sent += 1
        except:
            if not fail_silently:
                raise
    try:
        server.quit()
    except:
        if fail_silently:
            return
        raise
    return num_sent

def mail_admins(subject, message, fail_silently=False):
    "Sends a message to the admins, as defined by the ADMINS setting."
    send_mail(settings.EMAIL_SUBJECT_PREFIX + subject, message, settings.SERVER_EMAIL, [a[1] for a in settings.ADMINS], fail_silently)

def mail_managers(subject, message, fail_silently=False):
    "Sends a message to the managers, as defined by the MANAGERS setting."
    send_mail(settings.EMAIL_SUBJECT_PREFIX + subject, message, settings.SERVER_EMAIL, [a[1] for a in settings.MANAGERS], fail_silently)
