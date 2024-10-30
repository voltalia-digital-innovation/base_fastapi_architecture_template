import os
from smtplib import SMTP
from typing import Dict, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from email.mime.application import MIMEApplication
from modules.core.env import (
    DEFAULT_REPLY_TO_EMAIL, SMTP_EMAIL_HOST,
    SMTP_EMAIL_HOST_PASSWORD, SMTP_EMAIL_PORT, SMTP_FROM_EMAIL
)


class SMTPEmail:
    """
    This class implement e-mail service
    using smtp lib that allows file sending

    Author: Matheus Henrique (m.araujo)
    """

    def __init__(
        self,
        email_host: str = SMTP_EMAIL_HOST,
        email_port: int = SMTP_EMAIL_PORT,
        email_host_password: str = SMTP_EMAIL_HOST_PASSWORD,
    ) -> None:
        self.from_email: str = SMTP_FROM_EMAIL

        self.server = SMTP(email_host, email_port)
        self.server.starttls()
        self.server.login(self.from_email, email_host_password)

    def send_mail(
        self,
        template: str,  # Convert this to template path to render template here in this method
        render_vars: Dict,
        subject: str,
        to_email: List[str],
        bcc_email: List[str] = [],
        from_email: str = None,
        reply_to_email: str = DEFAULT_REPLY_TO_EMAIL,
        attachment_obj: bytes = None
    ):
        """
        This method send email with file attatched

        Author: Matheus Henrique (m.araujo)

        Parameters:
        - render_vars: Dict,
        - subject: str,
        - to_email: List[str],
        - bcc_email: List[str] = [],
        - from_email: str = None,
        - reply_to_email: str = settings.DEFAULT_REPLY_TO_EMAIL,
        - attachment_obj: bytes = None

        Returns:
            None
        """
        if from_email is None:
            from_email = self.from_email

        templates_path = 'base_api/core/services/email/templates'
        jinja_env = Environment(loader=FileSystemLoader(
            os.path.abspath(templates_path)
        ))
        template = jinja_env.get_template(template)

        template = template.render(
            **render_vars
        )

        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = from_email
        message['To'] = ','.join(to_email) if len(to_email) > 0 else ''
        message['Bcc'] = ','.join(bcc_email) if len(bcc_email) > 0 else ''
        message['Reply-To'] = reply_to_email

        message.attach(MIMEText(template, "html"))

        if attachment_obj:
            attachment = MIMEApplication(
                attachment_obj['file'], attachment_obj['name'])
            attachment['Content-Disposition'] = f"attachment; filename={
                attachment_obj['name']}"
            message.attach(attachment)

        msg_body = message.as_string()

        self.server.sendmail(from_email, to_email + bcc_email, msg_body)

    def quit_server_connection(self):
        """
        Quit SMTP connection

        Author: Matheus Henrique (m.araujo)
        """
        self.server.quit()
