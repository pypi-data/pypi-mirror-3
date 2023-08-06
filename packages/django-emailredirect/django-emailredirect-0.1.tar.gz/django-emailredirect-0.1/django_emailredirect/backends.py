from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend

class EmailBackend(SMTPEmailBackend):
    def send_messages(self, email_messages):
        for msg in email_messages:
            pre_txt = "This email should be sent to: %s\n" % str(msg.to)
            pre_txt += "------------\n\n"
            msg.to = settings.EMAIL_REDIRECT
            msg.body = pre_txt + msg.body

        return super(EmailBackend, self).send_messages(email_messages)
