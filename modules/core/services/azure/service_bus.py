import json
from typing import Dict, List
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from modules.core.env import SB_CONNECTION_STR, SB_EMAIL_QUEUE, SB_MAX_WAIT_TIME


class AzureServiceBusService:
    """
    This class have methods to handle Azure Service Bus iteractions

    Author: Matheus Henrique (m.araujo)
    """

    def get_servicebus_client(self, ):
        """
        Get the Service Bus client

        Author: Matheus Henrique (m.araujo)
        """
        servicebus_client = ServiceBusClient.from_connection_string(
            conn_str=SB_CONNECTION_STR)
        return servicebus_client

    def get_sender(self, servicebus_client, queue_name: str):
        """
        Get Service Bus instance to send messages to queue

        Author: Matheus Henrique (m.araujo)
        """

        if not queue_name:
            queue_name = SB_EMAIL_QUEUE
        receiver = servicebus_client.get_queue_sender(queue_name=queue_name)
        return receiver

    def get_receiver(self, servicebus_client, queue_name: str = SB_EMAIL_QUEUE):
        """
        Get Service Bus instance to receive messages from queue

        Author: Matheus Henrique (m.araujo)
        """
        sender = servicebus_client.get_queue_receiver(queue_name=queue_name)
        return sender

    def send_messages(self, messages: List[ServiceBusMessage], sender):
        """
        Send messages to Service Bus queue

        Author: Matheus Henrique (m.araujo)
        """
        sender.send_messages(messages)

    def read_messages(self, receiver, messages_amount: int = 1):
        """
        Get messages from Service Bus queue

        Author: Matheus Henrique (m.araujo)
        """
        messages = receiver.receive_messages(
            max_wait_time=SB_MAX_WAIT_TIME,
            max_message_count=messages_amount)

        return messages

    def pop_messages(self, messages: List[ServiceBusMessage], receiver):
        """
        Pop messages from Service Bus queue

        Author: Matheus Henrique (m.araujo)
        """
        for message in messages:
            receiver.complete_message(message)

    def send_a_bunch_of_dict_to_queue(self, messages: List[Dict], queue_name: str = None):
        """
        It will put a bunch of messages in Azure Service Bus queue

        Author: Matheus Henrique (m.araujo)

        Parameters:
        - messages: List[Dict]
        - queue_name: str (if none, default will be "SB_EMAIL_QUEUE")
        """
        msgs = []
        for message in messages:
            msgs.append(ServiceBusMessage(json.dumps(message)))

        servicebus_client = AzureServiceBusService().get_servicebus_client()
        sender = AzureServiceBusService().get_sender(servicebus_client, queue_name)

        AzureServiceBusService().send_messages(msgs, sender)
