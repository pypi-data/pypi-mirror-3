#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
import buffet
import smtplib
from mimetypes import guess_type
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage
from email.MIMEBase import MIMEBase
from email.Header import Header
from email.Utils import formatdate, parseaddr, formataddr
from email import Encoders
from cocktail import schema
from woost.models import Item, Site, File


class EmailTemplate(Item):

    encoding = "utf-8"

    members_order = [
        "title",
        "mime_type",
        "sender",
        "receivers",
        "bcc",
        "template_engine",
        "subject",
        "body",
        "initialization_code"
    ]

    title = schema.String(
        listed_by_default = False,
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        full_text_indexed = True,
        descriptive = True,
        translated = True
    )

    mime_type = schema.String(
        required = True,
        default = "html",
        listed_by_default = False,
        enumeration = [
            "plain",
            "html"
        ],
        text_search = False
    )

    sender = schema.CodeBlock(
        language = "python"
    )

    receivers = schema.CodeBlock(
        language = "python",
        required = True
    )
    
    bcc = schema.CodeBlock(
        language = "python",
        listed_by_default = False
    )

    template_engine = schema.String(
        enumeration = buffet.available_engines.keys(),
        text_search = False,
        listed_by_default = False
    )

    subject = schema.String(
        translated = True,
        edit_control = "cocktail.html.TextArea"
    )

    body = schema.String(
        translated = True,
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea"
    )

    initialization_code = schema.CodeBlock(
        language = "python"
    )

    def send(self, context = None):

        smtp_host = Site.main.smtp_host or "localhost"
        smtp_port = smtplib.SMTP_PORT
        smtp_user = Site.main.smtp_user
        smtp_password = Site.main.smtp_password

        if context is None:
            context = {}
        
        if context.get("attachments") is None:
            context["attachments"] = {}

        def eval_member(key):
            expr = self.get(key)
            return eval(expr, context.copy()) if expr else None

        # MIME block
        mime_type = self.mime_type
        pos = mime_type.find("/")

        if pos != -1:
            mime_type = mime_type[pos + 1:]

        # Custom initialization code
        init_code = self.initialization_code
        if init_code:
            exec init_code in context

        # Subject and body (templates)
        if self.template_engine:
            template_engine = buffet.available_engines[self.template_engine]
            engine = template_engine(
                options = {"mako.output_encoding": self.encoding}
            )

            def render(field_name):
                markup = self.get(field_name)
                if markup:
                    template = engine.load_template(
                        "EmailTemplate." + field_name,
                        self.get(field_name)
                    )
                    return engine.render(context, template = template)                    
                else:
                    return u""
           
            subject = render("subject").strip()
            body = render("body")
        else:
            subject = self.subject.encode(self.encoding)
            body = self.body.encode(self.encoding)
            
        message = MIMEText(body, _subtype = mime_type, _charset = self.encoding)

        # Attachments
        attachments = context.get("attachments")
        if attachments:
            attachments = dict(
                (cid, attachment) 
                for cid, attachment in attachments.iteritems()
                if attachment is not None
            )
            if attachments:
                message_text = message
                message = MIMEMultipart("related")
                message.attach(message_text)

                for cid, attachment in attachments.iteritems():
                    
                    if isinstance(attachment, File):
                        file_path = attachment.file_path
                        file_name = attachment.file_name
                        mime_type = attachment.mime_type
                    else:
                        file_path = attachment
                        file_name = os.path.basename(file_path)
                        mime_type_guess = guess_type(file_path)
                        if mime_type_guess:
                            mime_type = mime_type_guess[0]
                        else:
                            mime_type = "application/octet-stream"

                    main_type, sub_type = mime_type.split('/', 1)
                    message_attachment = MIMEBase(main_type, sub_type)
                    message_attachment.set_payload(open(file_path).read())
                    Encoders.encode_base64(message_attachment)
                    message_attachment.add_header("Content-ID", "<%s>" % cid)
                    message_attachment.add_header(
                        'Content-Disposition',
                        'attachment; filename="%s"' % file_name
                    )
                    message.attach(message_attachment)

        def format_email_address(address, encoding):
            name, address = parseaddr(address)
            name = Header(name, encoding).encode()
            address = address.encode('ascii')
            return formataddr((name, address))

         # Receivers (python expression)
        receivers = eval_member("receivers")
        if receivers:
            receivers = set(r.strip().encode(self.encoding) for r in receivers) 

        if not receivers:
            return set()
 
        message["To"] = ", ".join([
            format_email_address(receiver, self.encoding) 
            for receiver in receivers
        ])

        # Sender (python expression)
        sender = eval_member("sender")
        if sender:
            message['From'] = format_email_address(sender, self.encoding)

        # BCC (python expression)
        bcc = eval_member("bcc")
        if bcc:
            receivers.update(r.strip().encode(self.encoding) for r in bcc)

        if subject:
            message["Subject"] = Header(subject, self.encoding).encode()

        message["Date"] = formatdate()

        # Send the message
        smtp = smtplib.SMTP(smtp_host, smtp_port)
        if smtp_user and smtp_password:
            smtp.login(
                smtp_user.encode(self.encoding), 
                smtp_password.encode(self.encoding)
            )
        smtp.sendmail(sender, list(receivers), message.as_string())
        smtp.quit()

        return receivers

