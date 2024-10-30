import os
from ast import Dict
from typing import List
from jinja2 import Environment, FileSystemLoader
from modules.core.env import DEFAULT_FROM_EMAIL, ENV, SB_EMAIL_QUEUE
from modules.core.services.azure.service_bus import AzureServiceBusService


class Email:
    """
    This class implement e-mail service
    using Azure service Bus

    Author: Matheus Henrique (m.araujo)
    """

    def send_email(
        self, users: List[str] = [], bcc_email: List[str] = [], template: str = '',
        system: str = 'base_fastapi_plus', subject: str = 'Base Fastapi Architecture template notification',
        render_vars: Dict = {}, body: str = None, email_queue_name: str = SB_EMAIL_QUEUE
    ) -> bool:
        """
        This method send messages

        Author: Matheus Henrique (m.araujo)
        Returns:
            bool: sent message or not
        """

        email_dict = self.__mount_email_queue_message(
            users=users, bcc_email=bcc_email, template=template,
            system=system, render_vars=render_vars, subject=subject,
            body=body
        )

        AzureServiceBusService().send_a_bunch_of_dict_to_queue(
            [email_dict], email_queue_name)

    def __mount_email_queue_message(
        self, users: List[str], bcc_email: List[str], template: str,
        system: str, subject: str, render_vars: Dict, body: str = None
    ):
        message_dict = {}

        ##### mount the menssage ######
        message_dict["system"] = system
        message_dict["to_email"] = ','.join(
            users) if ENV == 'PROD' else DEFAULT_FROM_EMAIL
        message_dict["bcc_email"] = ','.join(
            bcc_email) if ENV == 'PROD' else DEFAULT_FROM_EMAIL
        message_dict["subject"] = subject
        message_dict["env"] = 'dev' if ENV == 'DEV' else 'prod'

        if body:
            message_dict["body"] = body
        else:
            templates_path = 'modules/core/services/email/templates'
            jinja_env = Environment(loader=FileSystemLoader(
                os.path.abspath(templates_path)
            ))
            template = jinja_env.get_template(template)

            message_dict["body"] = template.render(
                **render_vars
            ).replace('\n', '')

        return message_dict
